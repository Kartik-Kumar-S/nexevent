from django.urls import path

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    ProfileView,
    VerifyEmailView,
    ResendVerificationView,
    PasswordResetView,
    PasswordResetConfirmView,
    RoleChangeRequestView,
    RoleChangeRequestReviewView,
    AuditLogListView,
)

app_name = 'accounts'

urlpatterns = [
    # Registration & Email Verification
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),

    # JWT Token Management
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Password Reset
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Role Management
    path('role-request/', RoleChangeRequestView.as_view(), name='role_request'),
    path('role-request/<int:pk>/review/', RoleChangeRequestReviewView.as_view(), name='role_request_review'),

    # User Profile
    path('profile/', ProfileView.as_view(), name='profile'),

    # Audit Logs
    path('audit-log/', AuditLogListView.as_view(), name='audit_log'),
]