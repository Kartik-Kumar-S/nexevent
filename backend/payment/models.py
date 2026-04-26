from django.db import models


class Payment(models.Model):

    STATUS_CHOICES = [
        ("CREATED", "Created"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    registration = models.OneToOneField(
        "event_registration.Registration",  # ← Use correct app label!
        on_delete=models.CASCADE,
        #null=True,  # Allow null temporarily
        #blank=True,  # Allow blank in forms
        related_name="payment"
    )

    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"