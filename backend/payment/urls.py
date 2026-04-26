from django.urls import path
from .views import InitiatePaymentView, VerifyPaymentView

urlpatterns = [
    path("verify/", VerifyPaymentView.as_view(), name="verify-payment"),

    path("initiate/<int:registration_id>/", InitiatePaymentView.as_view(), name="initiate-payment"),
]
