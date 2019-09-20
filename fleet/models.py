import django.utils.timezone
from django.db import models


class BusinessModel(models.Model):
    name = models.CharField(max_length=255)
    every_n_minute_charging = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True, null=True, editable=False)

    def __str__(self):
        return self.name


class Fleet(models.Model):
    business_model = models.ForeignKey(BusinessModel, on_delete=models.CASCADE, default=0)
    active = models.BooleanField(default=False)
    minimum_battery = models.PositiveSmallIntegerField(blank=False, null=False)
    payout_period_minutes = models.PositiveSmallIntegerField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    time_threshold = models.PositiveIntegerField(default=300, verbose_name='time threshold(s)')

    # def __str__(self):
    #     str_fleet = 'business model: '
    #     str_fleet += self.business_model.__str__() + "\n"
    #     str_fleet += 'n minute charging: '
    #     str_fleet += str(self.business_model.every_n_minute_charging) + "\n"
    #     str_fleet += 'n minute charging: '
    #     str_fleet += self.business_model.every_n_minute_charging + "\n"
    #     str_fleet += 'n minute charging: '
    #     str_fleet += self.business_model.every_n_minute_charging + "\n"
    #     str_fleet += 'n minute charging: '
    #     str_fleet += self.business_model.every_n_minute_charging + "\n"



