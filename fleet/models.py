import django.utils.timezone
from django.db import models


class BusinessModel(models.Model):
    name = models.CharField(max_length=255)
    every_n_minute_charging = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True, null=True, editable=False)


class Fleet(models.Model):
    business_model = models.ForeignKey(BusinessModel, on_delete=models.CASCADE, default=0)
    active = models.BooleanField(default=False)
    minimum_battery = models.PositiveSmallIntegerField(blank=False, null=False)
    payout_period_minutes = models.PositiveSmallIntegerField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, editable=False)
