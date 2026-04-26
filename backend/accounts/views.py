from django.contrib.auth import get_user_model
from django.core import signing
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from .models import RoleChangeRequest, AuditLog
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    VerifyEmailSerializer,
    ResendVerificationSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    RoleChangeRequestSerializer,
    RoleChangeRequestReviewSerializer,
    AuditLogSerializer,
)
from .utils import log_action
from .tasks import send_email_task

User = get_user_model()

@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_verified=False)

        # Generate signed token
        token = signing.dumps(str(user.pk), salt='email-verify')
        
        # Dispatch email task
        verify_url = f"http://localhost:5173/auth/verify-email/?token={token}"
        send_email_task.delay(
            subject="Verify your NexEvent account",
            message=f"Please verify your email using this link: {verify_url}",
            recipient_list=[user.email]
        )

        log_action(request, user, 'register')

        return Response({
            'message': 'Registration successful. Please check your email to verify your account.'
        }, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        try:
            user_id = signing.loads(token, salt='email-verify', max_age=86400)
            user = User.objects.get(pk=user_id)
        except (signing.BadSignature, signing.SignatureExpired, User.DoesNotExist):
            return Response({'error': 'Invalid or expired verification token.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_verified:
            return Response({'message': 'Email already verified.'}, status=status.HTTP_200_OK)

        user.is_verified = True
        user.save(update_fields=['is_verified'])

        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['username'] = user.username
        refresh['role'] = user.role
        refresh['is_verified'] = user.is_verified

        log_action(request, user, 'verify_email')

        return Response({
            'message': 'Email successfully verified.',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
        }, status=status.HTTP_200_OK)

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class ResendVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                token = signing.dumps(str(user.pk), salt='email-verify')
                verify_url = f"http://localhost:5173/auth/verify-email/?token={token}"
                send_email_task.delay(
                    subject="Verify your NexEvent account",
                    message=f"Please verify your email using this link: {verify_url}",
                    recipient_list=[user.email]
                )
                log_action(request, user, 'resend_verification')
        except User.DoesNotExist:
            pass

        return Response({'message': 'If the email exists, a verification link has been sent.'}, status=status.HTTP_200_OK)

@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get('email'))
            log_action(request, user, 'login')
        return response

class CustomTokenRefreshView(TokenRefreshView):
    pass

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            log_action(request, request.user, 'logout')

            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Token is invalid or already blacklisted.'}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            ts = user.last_login.timestamp() if user.last_login else 0
            token = signing.dumps({'uid': str(user.pk), 'ts': ts}, salt='password-reset')
            reset_url = f"http://localhost:5173/auth/reset-password/?token={token}"
            send_email_task.delay(
                subject="Password Reset for NexEvent",
                message=f"Reset your password using this link: {reset_url}",
                recipient_list=[user.email]
            )
            log_action(request, user, 'password_reset_requested')
        except User.DoesNotExist:
            pass
        
        return Response({'message': 'If the email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            data = signing.loads(token, salt='password-reset', max_age=3600)
            user = User.objects.get(pk=data['uid'])
            expected_ts = user.last_login.timestamp() if user.last_login else 0
            if data['ts'] != expected_ts:
                raise ValueError("Token is no longer valid.")
        except (signing.BadSignature, signing.SignatureExpired, User.DoesNotExist, ValueError, KeyError):
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=['password'])
        log_action(request, user, 'password_reset_completed')

        return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class RoleChangeRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == User.Role.ADMIN:
            status_filter = request.query_params.get('status')
            queryset = RoleChangeRequest.objects.all()
            if status_filter:
                queryset = queryset.filter(status=status_filter)
        else:
            queryset = RoleChangeRequest.objects.filter(user=request.user)
        
        serializer = RoleChangeRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != User.Role.STUDENT:
            return Response({'error': 'Only students can request a role change.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check cooldown
        latest_request = RoleChangeRequest.objects.filter(user=request.user).order_by('-created_at').first()
        if latest_request and latest_request.status == RoleChangeRequest.Status.PENDING:
            return Response({'error': 'You already have a pending role request.'}, status=status.HTTP_400_BAD_REQUEST)
        if latest_request and latest_request.cooldown_until and latest_request.cooldown_until > timezone.now():
            return Response({'error': f'You must wait until {latest_request.cooldown_until} to request again.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        role_req = serializer.save(user=request.user, current_role=request.user.role)
        log_action(request, request.user, 'role_request_submitted', 'RoleChangeRequest', role_req.id)

        # Notify user
        send_email_task.delay(
            subject="Role Request Received",
            message="Your request to become an ORGANIZER has been received and is pending review.",
            recipient_list=[request.user.email]
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RoleChangeRequestReviewView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            role_req = RoleChangeRequest.objects.get(pk=pk)
        except RoleChangeRequest.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        if role_req.status != RoleChangeRequest.Status.PENDING:
            return Response({'error': 'Request is not pending.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleChangeRequestReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']
        comment = serializer.validated_data.get('comment', '')

        role_req.reviewed_by = request.user
        role_req.reviewed_at = timezone.now()
        role_req.review_comment = comment

        user = role_req.user
        response_data = {'message': f'Request {action}d successfully.'}

        if action == 'approve':
            role_req.status = RoleChangeRequest.Status.APPROVED
            user.role = role_req.requested_role
            user.save(update_fields=['role'])
            
            send_email_task.delay(
                subject="Role Request Approved",
                message="Congratulations! Your request to become an ORGANIZER has been approved.",
                recipient_list=[user.email]
            )
            log_action(request, request.user, 'role_request_approved', 'RoleChangeRequest', role_req.id)
            
            # Instruction: "After approval, return a new JWT pair in the response so the frontend can update the token with the new role claim without forcing a re-login."
            refresh = RefreshToken.for_user(user)
            refresh['email'] = user.email
            refresh['username'] = user.username
            refresh['role'] = user.role
            refresh['is_verified'] = user.is_verified
            response_data['student_tokens'] = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
            
        else:
            role_req.status = RoleChangeRequest.Status.REJECTED
            role_req.cooldown_until = timezone.now() + timedelta(days=30)
            
            send_email_task.delay(
                subject="Role Request Rejected",
                message=f"Your request to become an ORGANIZER was rejected. Comment: {comment}",
                recipient_list=[user.email]
            )
            log_action(request, request.user, 'role_request_rejected', 'RoleChangeRequest', role_req.id)
            
        role_req.save()

        return Response(response_data, status=status.HTTP_200_OK)

class AuditLogListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.all().order_by('-created_at')

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        action = self.request.query_params.get('action')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        return queryset