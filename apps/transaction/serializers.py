from django.utils import timezone
from rest_framework import serializers

from apps.events.models import Event
from .models import PaymentTransaction
from ..donation.models import Donation, Pledge
from ..donation.serializers.donation import DonationSerializer
from ..shared.utils.payment import verify_payment


class PaymentTransactionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'location', 'start_datetime', 'end_datetime')


class PaymentTransactionDonationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Donation
        fields = ('id', 'title', 'description')


class PaymentTransactionSerializer(serializers.ModelSerializer):
    category_object = serializers.SerializerMethodField()

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'full_name', 'category', 'payment_method', 'amount',
            'payment_started_at', 'payment_completed_at', 'status',
            'currency', 'is_verified', 'category_object', 'reference'
        ]

    def get_category_object(self, obj):
        category_mapping = {
            'event': (Event, PaymentTransactionEventSerializer),
            'donation': (Donation, PaymentTransactionDonationSerializer),
        }
        model_and_serializer = category_mapping.get(obj.category)
        if model_and_serializer:
            model, serializer = model_and_serializer
            try:
                instance = model.objects.get(id=obj.category_object_id)
                return serializer(instance).data
            except model.DoesNotExist:
                return None
        return None


class PaymentVerificationSerializer(serializers.Serializer):
    reference = serializers.CharField()

    def process_verification(self):
        """Process Paystack payment verification and update the transaction if successful."""
        reference = self.validated_data['reference']
        verification_result = verify_payment(reference)

        # If verification fails, raise a validation error
        if verification_result["status"] != "success":
            raise serializers.ValidationError("Payment Transaction verification failed")

        # Update or create the transaction based on the verification data
        transaction_data = verification_result["data"]
        payment_transaction, _ = PaymentTransaction.objects.update_or_create(
                reference=transaction_data["reference"],
                defaults={
                    "status": transaction_data["status"],
                    "payment_completed_at": transaction_data["paid_at"],
                    "receipt_number": transaction_data.get("receipt_number"),
                    "amount": transaction_data["amount"]/100,
                    "currency": transaction_data["currency"],
                    "gateway_response": transaction_data["gateway_response"],
                    "authorization_code": transaction_data["authorization"]["authorization_code"],
                    "fees": transaction_data.get("fees"),
                    "bank_name": transaction_data["authorization"]["bank"],
                    "customer_email": transaction_data["customer"]["email"],
                    "customer_phone": transaction_data["customer"]["phone"],
                    "is_verified": transaction_data["status"] == "success",
                    "payment_method": transaction_data["channel"],
                    "transaction_object": transaction_data,
                },
            )

        if payment_transaction.category == 'donation':
            try:
                pledge = Pledge.objects.get(
                    donation_id=payment_transaction.category_object_id,
                    user=payment_transaction.user,
                    is_redeemed=False
                )
                print(pledge)
                pledge.is_redeemed = True
                pledge.redeemed_at = timezone.now()
                pledge.save()
            except Pledge.DoesNotExist:
                pass
        return payment_transaction
