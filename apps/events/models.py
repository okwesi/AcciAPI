from django.db import models
from apps.shared.models import BaseModel


class Event(BaseModel):
    location = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='events/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} {self.start_datetime} {self.end_datetime}"

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-start_datetime']


class EventAmount(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_amounts')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Event Amount'
        verbose_name_plural = 'Event Amounts'

    def __str__(self):
        return f"{self.event.title} {self.amount}"


class EventRegistration(BaseModel):
    GENDER_CHOICES = [
        ('m', 'Male'),
        ('f', 'Female'),
    ]

    CHURCH_POSITION_CHOICES = [
        ('elder', 'Elder'),
        ('pastor', 'Pastor'),
        ('deacon', 'Deacon'),
        ('member', 'Member'),
        ('deaconess', 'Deaconess'),
        ('prophet', 'Prophet'),
        ('prophetess', 'Prophetess'),
        ('apostle', 'Apostle'),
        ('reverend', 'Reverend'),
        ('other', 'Other'),
        ('none', 'None'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=14)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    is_church_member = models.BooleanField(max_length=3, default=True)
    church_position = models.CharField(max_length=100, choices=CHURCH_POSITION_CHOICES, null=True, blank=True)
    nation = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100)
    city_town = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=30)
    is_paid = models.BooleanField(default=False)
    branch = models.ForeignKey('jurisdiction.Branch', on_delete=models.SET_NULL, null=True, blank=True)
