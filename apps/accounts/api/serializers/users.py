from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from rest_framework import serializers

from apps.accounts.models import GroupRank, AppPermission, AppGroup
from apps.jurisdiction.models import Branch
from apps.jurisdiction.serializers.branch import ShortBranchSerializer
from apps.shared.task import send_sms

User = get_user_model()
ENVIRONMENT = settings.ENVIRONMENT


class ShortUserSerializer(serializers.ModelSerializer):
    branch = ShortBranchSerializer(many=False, read_only=True)
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'username', 'last_name',
            'gender', 'phone_number', 'date_created', 'branch'
        ]


class NewUserSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=True)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'username', 'last_name',
            'gender', 'phone_number', 'group', 'branch'
        ]

    def create(self, validated_data):
        validated_data['user_type'] = 'admin'
        group = validated_data.pop('group', None)

        user = User(**validated_data)
        code = user.set_sms_verification()
        message = f'Your verification code is {code}'
        user.save()
        # Assign group
        if group:
            user.groups.set([group])
        send_sms(user.phone_number, message, sender_id='ACCI')

        return user

    def update(self, instance, validated_data):
        new_group = validated_data.pop('group', None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Get the current group the user belongs to, if any
        current_group = instance.groups.first()

        # Update or set group
        if new_group is not None:
            if current_group != new_group:
                instance.groups.clear()
                instance.groups.set([new_group])
        elif new_group is None and current_group is not None:
            instance.groups.clear()

        if instance.is_verified is False and ENVIRONMENT == 'production':
            code = instance.set_sms_verification()
            template_name = 'user_verification'
            # TODO: send sms message

        return instance


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    rank = serializers.IntegerField(source='ranking.rank')
    is_default = serializers.BooleanField(source='ranking.is_default')

    class Meta:
        model = Group
        fields = ['id', 'name', 'rank', 'is_default', 'permissions']

    def to_representation(self, instance):
        """
        Conditionally include users based on 'include_users' query parameter.
        """
        representation = super().to_representation(instance)

        request = self.context.get('request')
        if request and 'include_users' in request.query_params:
            representation['users'] = ShortUserSerializer(instance.user_set.filter(is_active=True), many=True).data

        return representation

    def get_permissions(self, obj):
        permissions = obj.permissions
        if AppGroup.objects.get_super_admin_group() == obj:
            permissions = AppPermission.objects.get_permissions()

        data = PermissionSerializer(
            permissions, many=True
        ).data
        return data


class GroupWithRankSerializer(serializers.ModelSerializer):
    # Make permissions and rank optional for partial updates
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, required=False)
    rank = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Group
        fields = [
            'permissions', 'rank', 'name'
        ]

    def validate(self, data):
        # If not a partial update (i.e., it's a creation), enforce name and rank
        if not self.partial:
            if 'name' not in data:
                raise serializers.ValidationError({'name': 'This field is required for creation.'})
            if 'rank' not in data:
                raise serializers.ValidationError({'rank': 'This field is required for creation.'})
        return data

    def create(self, validated_data):
        # Pop permissions and rank, but provide default values to avoid KeyError
        permissions = validated_data.pop('permissions', [])
        rank = validated_data.pop('rank', None)

        # Create the group
        group = Group.objects.create(**validated_data)

        # Set permissions if provided
        if permissions:
            group.permissions.set(permissions)

        # Create GroupRank if rank is provided
        if rank is not None:
            GroupRank.objects.create(group=group, rank=rank)

        return group

    def update(self, instance, validated_data):
        # Get new permissions and ranking data, if provided
        new_permissions = validated_data.get('permissions')
        rank = validated_data.get('rank', instance.ranking.rank)

        # Update name if provided
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Update permissions if provided
        if new_permissions is not None:
            current_permissions = set(instance.permissions.values_list('id', flat=True))
            new_permission_ids = set(permission.id for permission in new_permissions)

            # Remove old permissions
            permissions_to_remove = current_permissions - new_permission_ids
            if permissions_to_remove:
                instance.permissions.remove(*permissions_to_remove)

            # Add new permissions
            permissions_to_add = new_permission_ids - current_permissions
            if permissions_to_add:
                instance.permissions.add(*permissions_to_add)

        # Update or create GroupRank
        group_rank, _ = GroupRank.objects.get_or_create(group=instance)
        group_rank.rank = rank
        group_rank.save()

        return instance
