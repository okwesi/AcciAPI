from django.contrib.auth import get_user_model
from django.db import models

from apps.shared.models import BaseModel

User = get_user_model()


class PaymentTransaction(BaseModel):
    CATEGORY_CHOICES = (
        ('donation', 'Donation'),
        ('event', 'Event'),
    )

    full_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    category_object_id = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    payment_started_at = models.DateTimeField()
    payment_completed_at = models.DateTimeField(null=True, blank=True)
    reference = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=5, null=True, blank=True)
    receipt_number = models.CharField(max_length=255, null=True, blank=True)
    gateway_response = models.CharField(max_length=255, null=True, blank=True)
    authorization_code = models.CharField(max_length=255, null=True, blank=True)
    fees = models.PositiveIntegerField(null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    transaction_object = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'PaymentTransaction'
        verbose_name_plural = 'PaymentTransactions'

    def __str__(self):
        return f"{self.full_name} - {self.category} ID: {self.category_object_id}"
