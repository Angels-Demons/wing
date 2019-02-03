import datetime

from api import sms_send, sms
from django.db import models
from accounts.models import User
# from ride.models import Ride

from decimal import Decimal

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

from scooter import funcs
# from scooter.Serializers import ScooterAnnounceSerializer


class Choices:
    scooter_status_choices = (
        (1, 'ready'),
        (2, 'occupied'),
        (3, 'low_battery'),
        (4, 'unavailable'),
        # (5, ''),
        # (6, ''),
    )


class Site(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Scooter(models.Model):
    phone_number = models.BigIntegerField(unique=True)
    device_code = models.PositiveIntegerField(unique=True)
    qr_info = models.CharField(max_length=255, null=True, unique=True)
    # rider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # has credit
    # has internet package
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    battery = models.PositiveSmallIntegerField()
    status = models.PositiveSmallIntegerField(choices=Choices.scooter_status_choices)
    activation_date = models.DateTimeField(auto_now_add=True)
    last_announce = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.phone_number)

    def start_ride(self, user):
        # if not scooter.device_code == int(device_code):
        #     data = {'error': 'error: wrong device'}
        #     return Response(data, status=HTTP_404_NOT_FOUND)
        if self.status != 1:
            data = {'error': 'error: device not free'}
            return Response(data, status=HTTP_400_BAD_REQUEST)
        # modify
        # really turn the device on here (via sms or net or whatever
        self.turn_on()
        ride = Ride(user=user,
                    scooter=self,
                    start_point_latitude=self.latitude,
                    start_point_longitude=self.longitude,
                    is_finished=False)
        ride.save()
        self.status = 2
        self.save()
        data = {'message': 'success: device activated',
                # 'device_id': device_id,
                'ride_id': ride.id}
        return Response(data, status=HTTP_200_OK)

    # modify
    def turn_on(self):
        sms_send.send_sms(self.phone_number, 'unlock')
        sms.lock_unlock(self.phone_number, False, self.device_code)
        # sms_send.send_sms(9367498998, 'unlock')

    # modify
    def turn_off(self):
        sms_send.send_sms(self.phone_number, 'lock')
        sms.lock_unlock(self.phone_number, True, self.device_code)
        # sms_send.send_sms(9367498998, 'lock')

    # def announce(self, request):
    #     # update self with new info
    #     data = request.GET.copy()
    #     del data['device_code']
    #     instance = ScooterAnnounceSerializer(instance=self, data=data)
    #     if instance.is_valid():
    #         print('valid announcement')
    #         instance.save()
    #         announcement = Announcement(
    #             scooter=self,
    #             latitude=self.latitude,
    #             longitude=self.longitude,
    #             battery=self.battery,
    #             status=self.status,
    #         )
    #         announcement.save()
    #
    #         self.last_announce = announcement.time
    #         self.save()
    #         return Response('announced', status=HTTP_200_OK)
    #     else:
    #         print(instance.errors)
    #         return Response('announcement not valid', status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def nearby_devices(latitude, longitude, radius):
        scooters = Scooter.objects.all()
        nearby = []
        for scooter in scooters:
            if abs((scooter.latitude + scooter.longitude) - (Decimal(latitude) + Decimal(longitude))) < 2 * Decimal(
                    radius):
                nearby.append(scooter)
        return nearby


class Announcement(models.Model):
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    battery = models.PositiveSmallIntegerField()
    status = models.PositiveSmallIntegerField(choices=Choices.scooter_status_choices)


class Ride(models.Model):
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.PositiveSmallIntegerField(null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    start_point_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    start_point_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    end_point_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    end_point_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    is_finished = models.BooleanField(default=False)
    # duration = models.TimeField(null=True)
    # distance = models.SmallIntegerField(null=True)

    def __str__(self):
        return self.user.profile.name + " :" + str(self.scooter.device_code)

    def end_ride(self):
        if self.is_finished:
            data = {'error': 'error: ride is finished'}
            return Response(data, status=HTTP_400_BAD_REQUEST)
        if self.scooter.status != 2:
            data = {'error': 'error: device not occupied'}
            return Response(data, status=HTTP_400_BAD_REQUEST)
        # modify
        # really turn the device off here!
        self.scooter.turn_off()
        self.end_point_latitude = self.scooter.latitude
        self.end_point_longitude = self.scooter.longitude
        self.end_time = datetime.datetime.now()
        self.save()
        self.price = funcs.price(self)
        self.is_finished = True
        self.save()
        self.user.profile.credit -= self.price
        self.user.profile.save()
        self.scooter.status = 1
        self.scooter.save()
        data = {'message': 'success: device deactivated',
                # 'device_id': device_id
                'ride_id': self.id
                }
        return Response(data, status=HTTP_200_OK)

    def get_duration(self):
        # print(datetime.datetime.now() - self.start_time)
        # return datetime.datetime.now(tz=None) - self.start_time
        time_delta = datetime.timedelta(minutes=1, seconds=10)
        t_delta = (datetime.datetime.now().replace(tzinfo=None) - self.start_time.replace(tzinfo=None)).seconds
        print(t_delta)
        return t_delta
