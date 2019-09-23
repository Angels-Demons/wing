import datetime

from django.db import models
# from river.models.fields.state import StateField

from accounts.models import User, Profile


class TopUp(models.Model):

    class Meta:
        permissions = (
            ("top_up", "Can top up users"),
        )

    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=False)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, editable=False)
    amount = models.SmallIntegerField()
    description = models.CharField(max_length=255)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     super(TopUp, self).save()
    def save(self, *args, **kwargs):
        former = self.profile.credit
        self.profile.credit += self.amount
        self.profile.save()
        if former + self.amount == self.profile.credit:
            self.success = True
            super(TopUp, self).save(*args, **kwargs)
        else:
            super(TopUp, self).save(*args, **kwargs)


class Choices:
    transaction_status_choices = (
        (0, 'شروع'),
        (1, 'درخواست نامعتبر'),  # gets error
        (2, 'درخواست معتبر'),  # gets redirected to zarinpal portal
        (3, 'تراکنش ناتمام'),  # gets error
        (4, 'تراکنش کامل و تایید نشده'),
        (5, 'تراکنش موفق'),
        (6, 'تراکنش تکراری'),
        (7, 'تراکنش ناموفق'),
    )

    transaction_status_choices_english = (
        (0, 'start'),
        (1, 'invalid request'),  # gets error
        (2, 'valid request'),  # gets redirected to zarinpal portal
        (3, 'canceled or terminated'),  # gets error
        (4, 'completed_not_verified'),
        (5, 'recharged'),
        (6, 'duplicated'),
        (7, 'failed'),
    )


class Transaction(models.Model):
    authority = models.BigIntegerField(null=True, editable=False)
    ref_id = models.BigIntegerField(null=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, editable=False)
    amount = models.IntegerField(editable=False)
    description = models.CharField(max_length=255)
    # email = models.EmailField(blank=True, null=True)
    state = models.PositiveSmallIntegerField(choices=Choices.transaction_status_choices, editable=False)
    recharged = models.BooleanField(default=False, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    # authority = models.BigIntegerField(null=True)
    # ref_id = models.BigIntegerField(null=True)
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    # amount = models.IntegerField()
    # description = models.CharField(max_length=255)
    # state = models.PositiveSmallIntegerField(choices=Choices.transaction_status_choices)
    # recharged = models.BooleanField(default=False)
    # timestamp = models.DateTimeField(null=True)

    def recharge(self):
        self.user.profile.credit += self.amount
        self.user.profile.save()
        self.state = 5
        self.recharged = True
        self.save()

    def __str__(self):
        return self.user.__str__() + ' ' + str(self.amount)
