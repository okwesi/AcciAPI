from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from apps.jurisdiction.models import Branch
from apps.jurisdiction.serializers.branch import ShortBranchSerializer
from apps.member.models import Member
from apps.shared.models import CustomTypes


class ShortMemberSerializer(serializers.ModelSerializer):
    member_title = serializers.SerializerMethodField(source='member_title.name')
    branch = serializers.SerializerMethodField(source='branch.name')
    district = serializers.SerializerMethodField(source='branch.district.name')
    area = serializers.SerializerMethodField(source='branch.district.area.name')

    class Meta:
        model = Member
        fields = [
            'id', 'email', 'gender', 'phone_number', "first_name",
            "last_name", "other_name", 'member_title', "branch",
            "district", "area"
        ]

    def get_member_title(self, obj):
        if obj.member_title:
            return obj.member_title.name
        else:
            return None

    def get_branch(self, obj):
        if obj.branch:
            return obj.branch.name
        else:
            return None

    def get_district(self, obj):
        if obj.branch and obj.branch.district:
            return obj.branch.district.name
        else:
            return None

    def get_area(self, obj):
        if obj.branch and obj.branch.district and obj.branch.district.area:
            return obj.branch.district.area.name
        else:
            return None


class MemberSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False)
    gender = serializers.ChoiceField(choices=Member.GENDER_CHOICES)
    marital_status = serializers.ChoiceField(choices=Member.MARITAL_STATUS_CHOICES, required=False)
    communication_preferences = serializers.ChoiceField(choices=Member.COMMUNICATION_CHOICES, required=False)
    educational_level = serializers.ChoiceField(choices=Member.EDUCATION_LEVEL_CHOICES, required=False)
    member_title = serializers.PrimaryKeyRelatedField(queryset=CustomTypes.objects.all(), required=False)
    member_type = serializers.PrimaryKeyRelatedField(queryset=CustomTypes.objects.all(), required=False)
    member_position = serializers.PrimaryKeyRelatedField(queryset=CustomTypes.objects.all(), required=False)
    member_group = serializers.PrimaryKeyRelatedField(queryset=CustomTypes.objects.all(), many=True, required=False)

    class Meta:
        model = Member
        fields = [
            'id', 'email', 'phone_number', 'address', 'emergency_contact_name',
            'emergency_contact_phone_number', 'first_name', 'last_name', 'other_name',
            'gender', 'date_of_birth', 'hometown', 'region', 'country',
            'marital_status', 'branch', 'is_baptised', 'date_joined', 'communication_preferences',
            'occupation', 'educational_level', 'member_title', 'member_type', 'member_position', 'member_group'
        ]
        extra_kwargs = {
            'phone_number': {'required': True},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        member_group_data = validated_data.pop('member_group', [])

        validated_data['branch'] = user.branch
        validated_data['created_by'] = user
        instance = super().create(validated_data)

        if member_group_data:
            instance.member_group.set(member_group_data)

        instance.save()
        return instance


class FullMemberSerializer(serializers.ModelSerializer):
    branch = ShortBranchSerializer()
    member_group = serializers.SerializerMethodField()
    member_title = serializers.SerializerMethodField()
    member_position = serializers.SerializerMethodField()
    member_type = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            'id', 'email', 'phone_number', 'address', 'emergency_contact_name',
            'emergency_contact_phone_number', 'first_name', 'last_name', 'other_name',
            'gender', 'date_of_birth', 'hometown', 'region', 'country',
            'marital_status', 'branch', 'is_baptised', 'date_joined', 'communication_preferences',
            'occupation', 'educational_level', 'member_title', 'member_type', 'member_position', 'member_group'
        ]

    def get_member_group(self, obj):
        from apps.shared.serializers.custom_types import CustomTypesSerializer
        return CustomTypesSerializer(obj.member_group.all(), many=True).data

    def get_member_title(self, obj):
        from apps.shared.serializers.custom_types import CustomTypesSerializer
        return CustomTypesSerializer(obj.member_title).data if obj.member_title else None

    def get_member_position(self, obj):
        from apps.shared.serializers.custom_types import CustomTypesSerializer
        return CustomTypesSerializer(obj.member_position).data if obj.member_position else None

    def get_member_type(self, obj):
        from apps.shared.serializers.custom_types import CustomTypesSerializer
        return CustomTypesSerializer(obj.member_type).data if obj.member_type else None


class BulkMemberSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    other_name = serializers.CharField(required=False, allow_null=True,)
    email = serializers.EmailField(required=False, allow_null=True,)
    gender = serializers.ChoiceField(choices=Member.GENDER_CHOICES, required=False)
    occupation = serializers.CharField(required=False, allow_null=True,)
    country = serializers.CharField(required=False, allow_null=True,)
    region = serializers.CharField(required=False, allow_null=True,)
    hometown = serializers.CharField(required=False, allow_null=True,)
    address = serializers.CharField(required=False, allow_null=True,)
    phone_number = serializers.CharField(required=False, allow_null=True,)
    date_joined = serializers.DateField(required=False, allow_null=True,)
    is_baptised = serializers.BooleanField(required=False, allow_null=True,)

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'other_name', 'email', 'gender', 'occupation', 'country', 'region',
                  'hometown', 'address', 'phone_number', 'date_joined', 'is_baptised']
