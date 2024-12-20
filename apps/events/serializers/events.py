from rest_framework import serializers
from apps.events.models import Event, EventAmount


class EventAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAmount
        fields = ['amount', 'currency']


class EventSerializer(serializers.ModelSerializer):
    event_amounts = EventAmountSerializer(many=True)

    class Meta:
        model = Event
        fields = (
            'id', 'location', 'start_datetime',
            'end_datetime', 'title', 'description',
            'cover_image', 'event_amounts', 'date_created',
            'created_by'
        )
        read_only_fields = ['id', 'date_created', 'created_by']

    def validate(self, data):
        if self.instance and not data:
            raise serializers.ValidationError("Update payload cannot be empty.")

        start_datetime = data.get('start_datetime')
        end_datetime = data.get('end_datetime')

        if end_datetime and start_datetime and end_datetime < start_datetime:
            raise serializers.ValidationError({
                'end_datetime': "End date cannot be before start date."
            })

        return data

    def create(self, validated_data):
        event_amounts_data = validated_data.pop('event_amounts', [])
        event = Event.objects.create(**validated_data)

        for amount_data in event_amounts_data:
            EventAmount.objects.create(event=event, **amount_data)

        return event

    def update(self, instance, validated_data):
        event_amounts_data = validated_data.pop('event_amounts', None)

        instance = super().update(instance, validated_data)

        if event_amounts_data is not None:
            instance.event_amounts.all().delete()
            for amount_data in event_amounts_data:
                EventAmount.objects.create(event=instance, **amount_data)

        return instance


class ListEventsSerializer(serializers.ModelSerializer):
    event_amounts = EventAmountSerializer(many=True)

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'location', 'description',
            'start_datetime', 'end_datetime',
            'cover_image', 'event_amounts', 'date_created',
            'created_by'
        )
