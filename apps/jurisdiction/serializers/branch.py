# serializers.py
from rest_framework import serializers

from apps.jurisdiction.models import Branch, District
from apps.member.models import Member


class ShortBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', ]


class BranchSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    branch_head = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), required=False, allow_null=True)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    contact_information = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    map_latitude = serializers.FloatField(required=False, allow_null=True)
    map_longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'branch_head', 'district',
            'address', 'contact_information',
            'map_latitude', 'map_longitude'
        ]

    def validate_name(self, value):
        if self.instance and self.instance.name == value:
            return value
        if Branch.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError('Branch with this name already exists.')
        return value

    def validate_branch_head(self, value):
        if value is None:
            return None
        if self.instance and self.instance.name == value:
            return value
        if self.instance and Branch.objects.filter(branch_head=value, is_active=True).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('Branch Head already has a branch.')
        elif not self.instance and Branch.objects.filter(branch_head=value, is_active=True).exists():
            raise serializers.ValidationError('Branch Head already has a branch.')
        return value

    def create(self, validated_data):
        return Branch.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class FullBranchSerializer(serializers.ModelSerializer):
    branch_head = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'branch_head', 'district',
            'address', 'contact_information',
            'map_latitude', 'map_longitude'
        ]

    def get_branch_head(self, obj):
        from apps.member.serializer import ShortMemberSerializer
        return ShortMemberSerializer(obj.branch_head).data if obj.branch_head else None

    def get_district(self, obj):
        from apps.jurisdiction.serializers.district import FullDistrictSerializer
        return FullDistrictSerializer(obj.district).data if obj.district else None
