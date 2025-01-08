from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.api.serializers.users import GroupSerializer
from apps.jurisdiction.models import Branch
from apps.jurisdiction.serializers.branch import ShortBranchSerializer
from apps.member.models import Member
from apps.shared.errors import INVALID_LOGIN
from apps.shared.literals import (
    PASSWORD, VERIFICATION_CODE, PHONE_NUMBER, OLD_PASSWORD, NEW_PASSWORD,
    REFRESH_TOKEN
)
from apps.shared.task import send_sms
from apps.shared.utils.helpers import generate_tokens
from acci.settings.base import ENVIRONMENT

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    branch = ShortBranchSerializer(many=False, read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'gender', 'phone_number', 'groups', 'branch'
        ]


class UserWithTokenSerializer(UserSerializer):
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['access_token', 'refresh_token']

    def to_representation(self, obj):
        ret = super().to_representation(obj)
        if obj.user_type == 'member':
            ret.pop('groups')
        tokens = generate_tokens(obj)

        ret['access_token'] = tokens['access_token']
        ret['refresh_token'] = tokens['refresh_token']

        return ret


class ProfileVerificationSerializer(serializers.Serializer):
    """
    Serializer for profile verification.
    """
    verification_code = serializers.IntegerField()
    password = serializers.CharField(write_only=True, min_length=6)
    phone_number = serializers.CharField(required=True)

    def create(self, validated_data):
        verification_code = validated_data[VERIFICATION_CODE]
        phone_number = validated_data[PHONE_NUMBER]
        password = validated_data[PASSWORD]

        try:
            user = User.objects.get(phone_number=phone_number, verification_code=verification_code)
            user.set_password(password)
            user.set_is_verified()
            user.save()

        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid phone number or verification code')

        return user

    def validate(self, data):
        """
        Validate verification code and password.
        """
        verification_code = data.get(VERIFICATION_CODE)
        phone_number = data.get(PHONE_NUMBER)

        try:
            User.objects.get(phone_number=phone_number, verification_code=verification_code)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid phone number or verification code')

        return data


class ProfileVerificationResendSerializer(serializers.Serializer):
    """
    Serializer for profile verification.
    """
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['phone_number']

    def create(self, validated_data):
        user = User.objects.get(phone_number=validated_data['phone_number'])
        code = user.set_sms_verification()
        message = f'Your verification code is {code}'
        send_sms(user.phone_number, message, sender_id='ACCI')
        return user

    def validate_phone_number(self, val):
        """
        Resend verification code for a specific user
        """

        try:
            User.objects.get(phone_number=val)

        except User.DoesNotExist:
            raise serializers.ValidationError('Could not find user with this Phone number')

        return val


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(phone_number=attrs["phone_number"])
            if user.user_type != 'admin':
                raise serializers.ValidationError("You are not an admin")
        except User.DoesNotExist:
            raise serializers.ValidationError(INVALID_LOGIN)
        user = authenticate(**attrs)
        if user is None:
            raise serializers.ValidationError(INVALID_LOGIN)
        attrs['user'] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def update(self, instance, validated_data):
        instance.set_password(validated_data[NEW_PASSWORD])
        instance.save()
        return instance

    def validate(self, attrs):
        user = self.instance
        if user.check_password(attrs.get(OLD_PASSWORD)):
            return attrs
        raise serializers.ValidationError("Old password Invalid")


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)

    def create(self, validated_data):
        token = RefreshToken(validated_data[REFRESH_TOKEN])
        token.blacklist()
        return token

    def validate_refresh_token(self, val):
        try:
            RefreshToken(val)
        except TokenError:
            raise serializers.ValidationError('Refresh token is blacklisted and cannot be used. '
                                              'Try login instead to get a new refresh token')


class MemberCheckSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)

    def validate_phone_number(self, value):
        # First check if member exists
        if not Member.objects.filter(phone_number=value, is_active=True).exists():
            raise serializers.ValidationError("Member with this phone number does not exist.")

        # Check if user exists and is verified
        if User.objects.filter(phone_number=value, is_verified=True).exists():
            raise serializers.ValidationError("User with this phone number already exists. Please Sign In.")

        return value

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        member = Member.objects.get(phone_number=phone_number)

        # Check if user exists but is not verified
        try:
            user = User.objects.get(phone_number=phone_number, is_verified=False)
            # Generate new verification code for existing unverified user
            code = user.set_sms_verification()
            user.save()
        except User.DoesNotExist:
            # Create new user if doesn't exist
            user = User.objects.create(
                username=phone_number,
                user_type='member',
                member=member,
                phone_number=phone_number,
                **{
                    key: getattr(member, key)
                    for key in ['first_name', 'last_name', 'email', 'branch', 'gender']
                    if hasattr(member, key)
                }
            )
            code = user.set_sms_verification()
            user.save()

        message = f"Your verification code is {code}"
        send_sms(user.phone_number, message, sender_id='ACCI')
        return user


class MemberLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        user = authenticate(**attrs)
        if user is None:
            raise serializers.ValidationError(INVALID_LOGIN)
        attrs['user'] = user
        return attrs


class MemberUserWithTokenSerializer(UserSerializer):
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['access_token', 'refresh_token']

    def to_representation(self, obj):

        ret = super().to_representation(obj)
        ret.pop("groups")
        tokens = generate_tokens(obj)

        ret['access_token'] = tokens['access_token']
        ret['refresh_token'] = tokens['refresh_token']

        return ret
