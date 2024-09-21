from django.core.validators import MinLengthValidator
from django.db import models

from apps.shared.models import BaseModel, CustomTypes
from apps.shared.utils.validators import validate_only_digits


class Member(BaseModel):
    GENDER_CHOICES = (('m', 'Male'), ('f', 'Female'),)
    COMMUNICATION_CHOICES = (('email', 'Email'), ('sms', 'SMS'))
    MARITAL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    )
    EDUCATION_LEVEL_CHOICES = (
        ('none', 'None'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('tertiary', 'Tertiary')
    )

    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(unique=True, max_length=40,
                                    validators=[
                                        MinLengthValidator(12, "Phone number number must be at least 14 characters."),
                                        validate_only_digits], )
    address = models.TextField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone_number = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    other_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    hometown = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    branch = models.ForeignKey('jurisdiction.Branch', on_delete=models.SET_NULL, null=True)
    is_baptised = models.BooleanField(default=False)
    date_joined = models.DateField(null=True, blank=True)
    communication_preferences = models.CharField(max_length=5, choices=COMMUNICATION_CHOICES, null=True, blank=True,
                                                 default='sms')
    occupation = models.CharField(max_length=100, null=True, blank=True)
    educational_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, null=True, blank=True)
    member_title = models.ForeignKey(CustomTypes, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='member_title')
    member_type = models.ForeignKey(CustomTypes, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='member_type')
    member_position = models.ForeignKey(CustomTypes, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='member_position')
    member_group = models.ManyToManyField(CustomTypes, blank=True, related_name='member_group')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email}, {self.phone_number})"
