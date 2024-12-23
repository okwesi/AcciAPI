from django.utils import timezone
from rest_framework import serializers

from apps.donation.models import Donation, DonationPayment, Pledge
from apps.shared.utils import payment
from apps.transaction.models import PaymentTransaction


class PledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pledge
        fields = (
            'id', 'donation', 'amount',
            'currency', 'redeem_date', 'is_redeemed'
        )

    def validate_donation(self, value):
        try:
            Donation.objects.get(id=value.id, is_active=True)
        except Donation.DoesNotExist:
            raise serializers.ValidationError("Donation not found")

        user = self.context['request'].user
        if Pledge.objects.filter(donation=value.id, user=user, is_redeemed=False).exists():
            raise serializers.ValidationError("You have already pledged for this donation.")
        return value

    def validate_redeem_date(self, value):
        if value is None:
            raise serializers.ValidationError('Redeem Date is required.')
        if value < timezone.now().date():
            raise serializers.ValidationError('Redeem Date cannot be in the past.')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Pledge.objects.create(**validated_data)


class ShortPledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pledge
        fields = ('id', 'amount', 'currency', 'redeem_date', 'is_redeemed')


class ListPledgeSerializer(serializers.ModelSerializer):
    donation = serializers.SerializerMethodField()
    class Meta:
        model = Pledge
        fields = (
            'id', 'donation', 'amount',
            'currency', 'redeem_date', 'is_redeemed',
            'redeemed_at'
        )
        read_only_fields = ['donation']

    def get_donation(self, obj):
        return {
            'id': obj.donation.id,
            'title': obj.donation.title,
        }


class RedeemPledgeSerializer(serializers.Serializer):
    pledge_id = serializers.IntegerField()
    payment_url = serializers.URLField(read_only=True)

    def validate_pledge_id(self, value):
        try:
            pledge = Pledge.objects.get(id=value, is_active=True, is_redeemed=False)
        except Pledge.DoesNotExist:
            raise serializers.ValidationError('Pledge with the given ID does not exist or has already been redeemed.')

        if pledge.user != self.context['request'].user:
            raise serializers.ValidationError('Pledge does not belong to the current user.')

        return value

    def create(self, validated_data):
        request = self.context.get('request')
        pledge = Pledge.objects.get(id=validated_data['pledge_id'], is_active=True, is_redeemed=False,
                                    user=request.user)
        user = request.user
        amount = float(pledge.amount)

        # Initialize payment
        payment_data = payment.initialize(
            email=pledge.user.email,
            amount=amount,
            currency=pledge.currency,
        )

        # Create payment transaction
        payment_transaction = PaymentTransaction.objects.create(
            full_name=user.get_full_name(),
            user=pledge.user,
            category='donation',
            category_object_id=pledge.donation.id,
            amount=float(amount),
            currency=pledge.currency,
            payment_started_at=timezone.now(),
            is_verified=False,
            reference=payment_data["reference"]
        )

        DonationPayment.objects.create(
            payment_transaction=payment_transaction,
            user=pledge.user,
            donation=pledge.donation,
            is_pledge=True,
            donated_at=timezone.now()
        )

        validated_data['payment_url'] = payment_data['payment_url']
        return validated_data
