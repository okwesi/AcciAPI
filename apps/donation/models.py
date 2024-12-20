from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

from apps.shared.models import BaseModel
from apps.transaction.models import PaymentTransaction

User = get_user_model()


class Donation(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='donations/', null=True, blank=True)

    class Meta:
        verbose_name = 'Donation'
        verbose_name_plural = 'Donations'

    def __str__(self):
        return self.title


class Pledge(BaseModel):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='pledges')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pledges')
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    currency = models.CharField(max_length=30)
    redeem_date = models.DateField()
    is_redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Pledge'
        verbose_name_plural = 'Pledges'

    def __str__(self):
        return f'{self.user} pledged {self.amount} for {self.donation}'


class DonationPayment(BaseModel):
    payment_transaction = models.OneToOneField(
        PaymentTransaction,
        on_delete=models.CASCADE,
        related_name='donation_payment'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='donation_payments',
    )
    donation = models.ForeignKey(
        Donation,
        on_delete=models.CASCADE,
        related_name='donation_payments'
    )
    is_pledge = models.BooleanField(default=False)
    pledge = models.ForeignKey(
        Pledge,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donation_pledge_payments'
    )
    donated_at = models.DateTimeField(default=now)

    class Meta:
        verbose_name = 'Donation Payment'
        verbose_name_plural = 'Donation Payments'
