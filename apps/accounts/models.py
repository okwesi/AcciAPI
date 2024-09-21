import random

from asgiref.sync import sync_to_async
from django.contrib.auth.models import Permission, UserManager
from django.contrib.auth.models import PermissionsMixin, AbstractUser, Group
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.member.models import Member
from apps.shared.literals import (
    ADD_ADMIN, UPDATE_ADMIN, DELETE_ADMIN, LIST_ADMINS, ADD_MEMBER, UPDATE_MEMBER, DELETE_MEMBER, VIEW_MEMBERS,
    VIEW_GROUPS_AND_ROLES, CREATE_GROUPS_AND_ROLES, UPDATE_GROUPS_AND_ROLES, DELETE_GROUPS_AND_ROLES, VIEW_BRANCHES,
    ADD_AREA, UPDATE_AREA, DELETE_AREA, VIEW_AREAS, ADD_DISTRICT, UPDATE_DISTRICT, DELETE_DISTRICT, VIEW_DISTRICTS,
    ADD_BRANCH, UPDATE_BRANCH, DELETE_BRANCH, VIEW_BRANCHES, LIST_BRANCH_MEMBERS, LIST_DISTRICT_MEMBERS,
    LIST_AREA_MEMBERS, DELETE_CUSTOM_TYPE, ADD_CUSTOM_TYPE, UPDATE_CUSTOM_TYPE, VIEW_CUSTOM_TYPES
)
from apps.shared.models import BaseModel
from apps.shared.utils.validators import validate_only_digits


class PermissionManager(models.Manager):
    def get_permissions(self, *args, **kwargs):
        """
        Custom manager method to get filtered permissions.
        """
        return super().get_queryset().exclude(
            Q(codename__startswith='add_') |
            Q(codename__startswith='change_') |
            Q(codename__startswith='delete_') |
            Q(codename__startswith='view_')
        )


class AppPermission(Permission):
    """
    Proxy model to attach the custom manager to the built-in Permission model.
    """
    objects = PermissionManager()

    class Meta:
        proxy = True


class GroupManager(models.Manager):
    def get_groups(self, is_active=False, *args, **kwargs):
        """
        Custom manager method to get filtered groups.
        """
        if is_active:
            return Group.objects.filter(ranking__is_active=True)
        return Group.objects.all()

    def get_super_admin_group(self, *args, **kwargs):
        return self.get(ranking__is_default=True, name='Super Admin')


class AppGroup(Group):
    """
    Proxy model to attach the custom manager to the built-in group model.
    """
    objects = GroupManager()

    class Meta:
        proxy = True


class CustomUserManager(UserManager):
    """
    Custom manager for User model to add additional methods.
    """

    def get_users_with_permission(self, permission):
        """
        Retrieve all users who have a given permission or are superusers.

        Args:
            permission (str): The codename of the permission to check.

        Returns:
            QuerySet: A queryset of User instances that have the specified permission or are superusers.
        """
        # Get the permission object
        try:
            permission = Permission.objects.get(codename=permission)
        except Permission.DoesNotExist:
            # Handle the case where the permission does not exist
            return self.none()

        # Query for users with the permission directly, through a group, or who are superusers
        return self.get_queryset().filter(
            Q(user_permissions=permission) |
            Q(groups__permissions=permission) | Q(is_superuser=True)
        ).distinct()


class User(AbstractUser, BaseModel, PermissionsMixin):
    GENDER_CHOICES = (('m', 'Male'), ('f', 'Female'),)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(unique=True, max_length=40,
                                    validators=[
                                        MinLengthValidator(12, "Phone number number must be at least 14 characters."),
                                        validate_only_digits], )
    verification_code = models.IntegerField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(blank=True, null=True)
    member = models.OneToOneField(Member, on_delete=models.CASCADE, blank=True, null=True)
    branch = models.ForeignKey('jurisdiction.Branch', on_delete=models.SET_NULL, blank=True, null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'email']
    objects = CustomUserManager()

    class Meta:
        permissions = [
            # users:
            (VIEW_GROUPS_AND_ROLES, 'view groups and roles'),
            (CREATE_GROUPS_AND_ROLES, 'create new groups and assign roles'),
            (UPDATE_GROUPS_AND_ROLES, 'update existing groups and their roles'),
            (ADD_ADMIN, 'create a new admin'),
            (LIST_ADMINS, 'view admins'),
            (DELETE_ADMIN, 'delete admin'),
            (UPDATE_ADMIN, 'update admin'),


            # members:
            (VIEW_MEMBERS, 'view members'),
            (UPDATE_MEMBER, 'update an existing member'),
            (ADD_MEMBER, 'add a new member'),
            (DELETE_MEMBER, 'delete a member'),
            (LIST_BRANCH_MEMBERS, 'view members of my branch'),
            (LIST_DISTRICT_MEMBERS, 'view members of my district'),
            (LIST_AREA_MEMBERS, 'view members of my area'),
            # Jurisdiction:
                # branches:
                (VIEW_BRANCHES, 'view branches'),
                (UPDATE_BRANCH, 'update an existing branch'),
                (ADD_BRANCH, 'add a new branch'),
                (DELETE_BRANCH, 'delete a branch'),

                # districts:
                (VIEW_DISTRICTS, 'view districts'),
                (UPDATE_DISTRICT, 'update an existing district'),
                (ADD_DISTRICT, 'add a new district'),
                (DELETE_DISTRICT, 'delete a district'),

                # areas:
                (VIEW_AREAS, 'view areas'),
                (UPDATE_AREA, 'update an existing area'),
                (ADD_AREA, 'add a new area'),
                (DELETE_AREA, 'delete a area'),

            # custom_types:
            (VIEW_CUSTOM_TYPES, 'view custom types'),
            (UPDATE_CUSTOM_TYPE, 'update an existing custom type'),
            (ADD_CUSTOM_TYPE, 'add a new custom type'),
            (DELETE_CUSTOM_TYPE, 'delete a custom type'),
        ]

    def set_sms_verification(self):
        self.verification_code = random.randint(10000, 99999)
        self.save()
        return self.verification_code

    def set_is_verified(self):
        self.is_verified = True
        self.verified_on = timezone.now()
        self.save()

    @property
    def is_super_admin(self):
        return self.groups.filter(name='Super Admin', ranking__is_default=True).exists()

    @sync_to_async
    def has_permission(self, perm):
        return self.has_perm(perm)

    def __str__(self):
        return f'{self.id}-{self.get_full_name()}'


class GroupRank(BaseModel):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='ranking')
    rank = models.PositiveIntegerField()
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.group.name} - {self.rank}'

    class Meta:
        ordering = ['rank']
