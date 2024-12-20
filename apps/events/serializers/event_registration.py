from rest_framework import serializers

from apps.accounts.api.serializers.users import ShortUserSerializer
from apps.events.models import EventRegistration
from apps.shared.utils import payment
from apps.transaction.models import PaymentTransaction


class EventRegistrationSerializer(serializers.ModelSerializer):
    payment_url = serializers.URLField(read_only=True)
    user = ShortUserSerializer(read_only=True)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        model = EventRegistration
        fields = (
            'id', 'event', 'full_name', 'email', 'phone_number', 'gender',
            'is_church_member', 'church_position', 'nation', 'region',
            'city_town', 'amount', 'currency', 'is_paid', 'user', 'payment_url'
        )
        read_only_fields = ['id', 'payment_url', 'user', 'date_created']

    def create(self, validated_data):
        request = self.context.get('request')
        user_agent = request.META.get('HTTP_USER_AGENT').lower()
        validated_data['user'] = request.user
        validated_data['amount'] = float(validated_data.pop('amount'))

        registration = EventRegistration.objects.create(**validated_data)

        payment_data = payment.initialize(
            email=registration.email,
            amount=registration.amount,
            currency=registration.currency,
            user_agent=user_agent
        )

        PaymentTransaction.objects.create(
            full_name=registration.full_name,
            category='event',
            category_object_id=registration.id,
            amount=registration.amount,
            payment_started_at=registration.date_created,
            is_verified=False,
            user=registration.user,
            reference=payment_data["reference"]
        )

        registration.payment_url = payment_data["payment_url"]
        return registration


class RegisteredEventSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_date = serializers.DateTimeField(source='event.start_datetime', read_only=True)

    class Meta:
        model = EventRegistration
        fields = [
            'id', 'event_title', 'event_date', 'amount', 'is_paid', 'currency',
            'full_name', 'gender', 'church_position', 'is_church_member',
        ]
