from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],  # Enforces Django password rules
        style={'input_type': 'password'},
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text='Confirm password — must match password field.',
    )

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'password', 'password2',
            'student_id', 'department', 'year_of_study',
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password2': 'Passwords do not match.'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'student_id', 'department', 'year_of_study',
            'role', 'is_verified', 'date_joined',
            'notification_preferences',
        ]
        read_only_fields = fields  # All fields are read-only in this serializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the JWT payload
        token['email'] = user.email
        token['username'] = user.username
        token['role'] = user.role
        token['is_verified'] = user.is_verified

        return token

    def validate(self, attrs):
        
        data = super().validate(attrs)

        if not self.user.is_verified:
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed('Please verify your email before logging in.')

        # Add user profile to login response
        data['user'] = UserProfileSerializer(self.user).data

        return data

class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return attrs

from .models import RoleChangeRequest, AuditLog

class RoleChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleChangeRequest
        fields = [
            'id', 'current_role', 'requested_role', 'justification',
            'documents_url', 'status', 'review_comment', 'created_at',
            'reviewed_at'
        ]
        read_only_fields = [
            'id', 'current_role', 'status', 'review_comment',
            'created_at', 'reviewed_at'
        ]

    def validate_requested_role(self, value):
        if value != User.Role.ORGANIZER:
            raise serializers.ValidationError("You can only request the ORGANIZER role.")
        return value

class RoleChangeRequestReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    comment = serializers.CharField(allow_blank=True, required=False)

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = AuditLog
        fields = '__all__'