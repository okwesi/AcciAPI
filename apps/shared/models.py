import base64

from decouple import config as env
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import JSONField
from django.utils import timezone
from rest_framework.exceptions import ValidationError


def xor_cipher(input_str, key):
    """
    Encrypt or decrypt a string using XOR and a key.
    """
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(input_str))


def base64_encode(input_str):
    """
    Encode input string with Base64.
    """
    # Convert to bytes, encode, then convert back to string for database compatibility
    return base64.b64encode(input_str.encode()).decode('utf-8')


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User',
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name='created_%(class)ss'
    )
    modified_by = models.ForeignKey(
        'accounts.User',
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name='modified_%(class)ss'
    )
    date_deleted = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'accounts.User',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='deleted_%(class)ss'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def soft_delete(self, owner, fields_to_encrypt: list = None):
        """
        Soft delete by setting is_active to False and encrypting specified fields.
        """
        self.is_active = False
        self.deleted_by = owner
        self.date_deleted = timezone.now()

        if fields_to_encrypt is not None:
            obj_id_str = str(self.id)
            secret_key = env('SECRET_KEY')
            key = f'{secret_key}{obj_id_str}'

            for field in fields_to_encrypt:
                if hasattr(self, field):
                    value = getattr(self, field)
                    if value is not None:
                        try:
                            encrypted_value = base64_encode(xor_cipher(str(value) + obj_id_str, key))
                            setattr(self, field, encrypted_value)
                        except Exception as e:
                            raise ValidationError(f"Error encrypting {field}: {str(e)}")
                    else:
                        # Handle None value - you might want to set it to a specific value or leave it as None
                        setattr(self, field, None)

        if hasattr(self, 'user'):
            self.user = None

        self.save()


class CustomTypes(BaseModel):
    CATEGORY_CHOICES = (
        ('member_type', 'Member Type'),
        ('member_position', 'Member Position'),
        ('member_title', 'Member Title'),
        ('ministry_group', 'Ministry Group'),

    )
    name = models.CharField(max_length=255, unique=True)  # Mr
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)  # member_title
    category_name = models.CharField(max_length=255, null=True, blank=True)  # Member Title

    def __str__(self):
        return f"{self.id} - {self.name}"

    def get_category_name(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, 'Unknown Category')
