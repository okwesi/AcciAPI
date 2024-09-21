from rest_framework import serializers

from apps.jurisdiction.models import District, Area
from apps.jurisdiction.serializers.area import FullAreaSerializer
from apps.member.models import Member
from apps.member.serializer import ShortMemberSerializer


class DistrictSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    district_head = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), required=False, allow_null=True)
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all(), required=True)

    class Meta:
        model = District
        fields = ['id', 'name', 'district_head', 'area']

    def validate_name(self, value):
        if value is None:
            return None
        if self.instance and self.instance.name == value:
            return value
        if District.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError('District with this name already exists.')
        return value

    def validate_district_head(self, value):
        if self.instance and self.instance.district_head == value:
            return value
        if self.instance and District.objects.filter(district_head=value, is_active=True).exclude(
                id=self.instance.id).exists():
            raise serializers.ValidationError('District Head already has a district.')
        elif not self.instance and District.objects.filter(district_head=value, is_active=True).exists():
            raise serializers.ValidationError('District Head already has a district.')
        return value


    def create(self, validated_data):
        return District.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class FullDistrictSerializer(serializers.ModelSerializer):
    district_head = ShortMemberSerializer()
    area = FullAreaSerializer()

    class Meta:
        model = District
        fields = ['id', 'name', 'district_head', 'area']
