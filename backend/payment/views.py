import razorpay
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Payment
from event_registration.models import Registration  # Import Registration
from .services import create_razorpay_order       # Import your order creation logic

try:
    from ticket.services import generate_ticket
except ImportError:
    generate_ticket = None


class InitiatePaymentView(APIView):
    """
    NEW FEATURE: This view allows users who were promoted from the waitlist 
    (status: PENDING_PAYMENT) to generate a Razorpay Order ID.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, registration_id):
        # 1. Get the registration and ensure it belongs to the logged-in student
        registration = get_object_or_404(
            Registration, 
            id=registration_id, 
            student=request.user
        )

        # 2. Check if the status is PENDING_PAYMENT
        if registration.status != "PENDING_PAYMENT":
            return Response(
                {"error": f"Payment cannot be initiated for status: {registration.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Create Razorpay Order
        try:
            # This calls the service that talks to Razorpay and saves the Payment model
            payment = create_razorpay_order(registration)
            
            return Response({
                "registration_id": registration.id,
                "razorpay_order_id": payment.razorpay_order_id,
                "amount": payment.amount / 100,  # Convert paise to rupees for frontend
                "currency": "INR",
                "status": "Order created. Proceed to payment verification."
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": f"Failed to create order: {str(e)}"}, status=500)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {"error": "Missing payment credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.select_related("registration").get(
                razorpay_order_id=razorpay_order_id
            )
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        registration = payment.registration

        
        if payment.status == "SUCCESS":
            if registration.status != "CONFIRMED":
                registration.status = "CONFIRMED"
                registration.save(update_fields=["status"])

               
                if not hasattr(registration, "ticket"):
                    generate_ticket(registration)

            return Response(
                {"message": "Payment already processed"},
                status=status.HTTP_200_OK,
            )

        
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )
        except razorpay.errors.SignatureVerificationError:
            payment.status = "FAILED"
            payment.save(update_fields=["status"])
            return Response(
                {"error": "Invalid payment signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )

       
        with transaction.atomic():
            payment.status = "SUCCESS"
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.save()

            registration.status = "CONFIRMED"
            registration.save(update_fields=["status"])

            generate_ticket(registration)

        return Response(
            {"message": "Payment verified successfully"},
            status=status.HTTP_200_OK,
        )