from django.utils import timezone
from rest_framework import serializers

from apps.donation.models import Donation, DonationPayment, Pledge
from apps.donation.serializers.pledge import ShortPledgeSerializer
from apps.shared.utils import payment
from apps.transaction.models import PaymentTransaction


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ('id', 'title', 'description', 'cover_image', 'date_created')
        read_only_fields = ('id', 'date_created')


class ListDonationSerializer(serializers.ModelSerializer):
    pledge = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ('id', 'title', 'description', 'cover_image', 'date_created', 'pledge')

    def get_pledge(self, obj):
        user = self.context['request'].user
        try:
            pledge = Pledge.objects.get(donation=obj, user=user, is_redeemed=False)
            return ShortPledgeSerializer(instance=pledge).data
        except Pledge.DoesNotExist:
            return None


class MakeDonationSerializer(serializers.Serializer):
    donation_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    currency = serializers.CharField(max_length=5)
    payment_url = serializers.URLField(read_only=True)

    def validate_donation_id(self, value):
        try:
            donation = Donation.objects.get(id=value, is_active=True)
            return value
        except Donation.DoesNotExist:
            raise serializers.ValidationError('Donation with the given ID does not exist.')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

    def validate(self, data):
        data['donation'] = Donation.objects.get(id=data['donation_id'], is_active=True)
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['amount'] = float(validated_data.pop('amount'))
        user = request.user

        payment_data = payment.initialize(
            email=user.email if user.is_authenticated else '',
            amount=validated_data['amount'],
            currency=validated_data['currency'],
        )

        payment_transaction = PaymentTransaction.objects.create(
            full_name=user.get_full_name(),
            user=user if user.is_authenticated else None,
            category='donation',
            category_object_id=validated_data['donation'].id,
            amount=validated_data['amount'],
            currency=validated_data['currency'],
            payment_started_at=timezone.now(),
            is_verified=False,
            reference=payment_data["reference"]
        )

        DonationPayment.objects.create(
            payment_transaction=payment_transaction,
            user=user if user.is_authenticated else None,
            donation=validated_data['donation'],
            is_pledge=False,
            donated_at=timezone.now()
        )

        validated_data['payment_url'] = payment_data['payment_url']
        return validated_data
