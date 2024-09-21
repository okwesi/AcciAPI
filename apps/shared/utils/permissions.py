from django.conf import settings
from rest_framework import permissions


class ValidateWebhookToken(permissions.BasePermission):
    """Custom permission to validate the webhook token."""

    def has_permission(self, request, view):
        token = request.GET.get('token')
        return token == settings.SFTP_WEBHOOK_TOKEN


class UserPermission(permissions.BasePermission):
    """
    Permission to check if user has 'create users with group' permission.
    """

    def __init__(self, permission_code):
        self.permission_code = permission_code

    def has_permission(self, request, view):
        # Check if the user has the specified permission
        return request.user.has_perm(
            f'accounts.{self.permission_code}'
        )
