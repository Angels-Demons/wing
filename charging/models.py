from django.db import models


class Tariff(models.Model):
    name = models.CharField(max_length=255)
    initial_price = models.PositiveSmallIntegerField()
    free_minutes = models.PositiveSmallIntegerField()
    free_kilometers = models.PositiveSmallIntegerField()
    per_minute_price = models.PositiveSmallIntegerField()
    per_kilometer_price = models.PositiveSmallIntegerField()
    initial_credit = models.PositiveSmallIntegerField()
    minimum_credit = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + '_' + \
               str(self.initial_price) + '_' + \
               str(self.per_minute_price) + '_' + \
               str(self.initial_credit)
