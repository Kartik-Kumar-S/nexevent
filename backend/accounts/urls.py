from django.urls import path

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    ProfileView,
)

app_name = 'accounts'

urlpatterns = [
    # Registration
    path('register/', RegisterView.as_view(), name='register'),

    # JWT Token Management
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    # Logout (blacklist refresh token)
    path('logout/', LogoutView.as_view(), name='logout'),

    # User Profile
    path('profile/', ProfileView.as_view(), name='profile'),
]