from rest_framework import serializers

from apps.jurisdiction.models import Area
from apps.member.models import Member
from apps.member.serializer import ShortMemberSerializer


class AreaSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    area_head = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'area_head']

    def validate_area_head(self, value):
        if value is None:
            return None
        if self.instance and self.instance.area_head == value:
            return value
        if self.instance and Area.objects.filter(area_head=value, is_active=True).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('Area Head already has an area.')
        elif not self.instance and Area.objects.filter(area_head=value, is_active=True).exists():
            raise serializers.ValidationError('Area Head already has an area.')
        return value

    def create(self, validated_data):
        return Area.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class FullAreaSerializer(serializers.ModelSerializer):
    area_head = ShortMemberSerializer()

    class Meta:
        model = Area
        fields = ['id', 'name', 'area_head']
