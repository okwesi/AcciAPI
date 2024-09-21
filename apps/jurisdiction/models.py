from django.db import models

from apps.member.models import Member
from apps.shared.models import BaseModel


class Area(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    area_head = models.OneToOneField(Member, on_delete=models.SET_NULL, related_name='area_head', null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.name}"


class District(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    district_head = models.OneToOneField(Member, on_delete=models.SET_NULL, related_name='district_head', null=True,
                                         blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.name} - {self.area}"


class Branch(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    branch_head = models.OneToOneField(Member, on_delete=models.SET_NULL, related_name='branch_head', null=True,
                                       blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    contact_information = models.TextField(null=True, blank=True)
    map_latitude = models.FloatField(null=True, blank=True)
    map_longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.name} - {self.district}"
    class Meta:
        verbose_name_plural = 'Branches'
