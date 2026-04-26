from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Registration
from .serializers import RegistrationSerializer
from .services import register_user_for_event, cancel_registration


class RegisterForEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        try:
            registration, razorpay_order = register_user_for_event(
                request.user,
                event_id
            )

            data = {
                "id": registration.id,
                "event": str(registration.event.id),
                "status": registration.status,
                "registered_at": registration.registered_at.isoformat(),
            }

            if razorpay_order:
                data["razorpay_order"] = razorpay_order
                data["message"] = "Seat reserved. Complete payment."
            else:
                data["message"] = "Event full. Added to waitlist."

            return Response(data, status=201)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancelRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        registration = get_object_or_404(
            Registration,
            id=pk,
            student=request.user
        )

        try:
            result = cancel_registration(registration)
            return Response({
                "detail": "Registration cancelled successfully",
                "promoted_waitlisted": result
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyRegistrationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        registrations = Registration.objects.filter(
            student=request.user
        ).select_related("event")
        serializer = RegistrationSerializer(registrations, many=True)
        return Response(serializer.data)


class AdminEventRegistrationsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, event_id):
        registrations = Registration.objects.filter(
            event_id=event_id
        ).select_related("student")
        data = [
            {
                "id": r.id,
                "student_email": r.student.email,
                "status": r.status,
                "registered_at": r.registered_at.isoformat(),
                "cancelled_at": r.cancelled_at.isoformat() if r.cancelled_at else None,
            }
            for r in registrations
        ]
        return Response(data)