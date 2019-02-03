from django.db import models


class Tariff(models.Model):
    name = models.CharField(max_length=255)
    initial_price = models.PositiveSmallIntegerField()
    per_minute_price = models.PositiveSmallIntegerField()
    per_kilometer_price = models.PositiveSmallIntegerField()
    initial_credit = models.PositiveSmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name + '_' + \
               str(self.initial_price) + '_' + \
               str(self.per_minute_price) + '_' + \
               str(self.initial_credit)
