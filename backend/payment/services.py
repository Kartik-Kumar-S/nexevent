import razorpay
from django.conf import settings
from .models import Payment


client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def create_razorpay_order(registration):
    """
    Creates Razorpay order and stores Payment object.
    If payment already exists and not FAILED, reuse it.
    """

    
    existing_payment = Payment.objects.filter(
        registration=registration
    ).exclude(status="FAILED").first()

    if existing_payment:
        return existing_payment

    amount_paise = int(registration.event.price * 100)

    order_data = {
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
    }

    razorpay_order = client.order.create(data=order_data)

    payment = Payment.objects.create(
        registration=registration,
        razorpay_order_id=razorpay_order["id"],
        amount=amount_paise,   
        status="CREATED"
    )

    return payment  