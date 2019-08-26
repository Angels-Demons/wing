import datetime

from background_task import background
from pytz import UTC

from api import sms_send, sms, mqtt
from django.db import models
from accounts.models import User
# from ride.models import Ride
import geopy.distance
from django.core.validators import MinValueValidator

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
    battery = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])
    status = models.PositiveSmallIntegerField(choices=Choices.scooter_status_choices)
    device_status = models.PositiveSmallIntegerField(choices=Choices.scooter_status_choices, default=1)
    activation_date = models.DateTimeField(auto_now_add=True)
    last_announce = models.DateTimeField(null=True, blank=True)
    modem_ssid = models.CharField(max_length=255, null=True, blank=True)
    modem_password = models.CharField(max_length=255, null=True, blank=True)

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
        if user.profile.credit < user.profile.tariff.minimum_credit:
            data = {
                # 'code': NOT_ENOUGH_CREDIT
                'error': 'error: not enough credit'}
            return Response(data, status=HTTP_200_OK)

        # modify
        # Here we don't take the credit off the wallet at start. We do it at the end
        # user.profile.credit -= user.profile.tariff.initial_price
        # user.profile.save()
        ride = Ride.initiate_ride(user=user, scooter=self)
        self.status = 2
        # modify
        # here: add scooter to the transient que
        # (a wait list for response of scooter and maybe reversing the transaction)
        self.save()
        self.turn_on()
        data = {'message': 'success: device activated',
                # 'device_id': device_id,
                'ride_id': ride.id}
        # print("before func")
        ride.reverse_started_ride(ride.id)
        # print("after func")
        return Response(data, status=HTTP_200_OK)

    # modify
    def turn_on(self):
        # sms.lock_unlock(self.phone_number, False, self.device_code)
        mqtt.send_mqtt('scooter/' + str(self.phone_number), 'unlock')

    # modify
    def turn_off(self):
        # sms.lock_unlock(self.phone_number, True, self.device_code)
        mqtt.send_mqtt('scooter/' + str(self.phone_number), 'lock')

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
    def nearby_devices(latitude, longitude, radius, user):
        nearby = []
        ride = Ride.objects.filter(user=user, is_finished=False).first()
        if ride:
            nearby.append(ride.scooter)
            return nearby
        scooters = Scooter.objects.all()
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
    battery = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])
    device_status = models.PositiveSmallIntegerField(choices=Choices.scooter_status_choices)
#     modify
#     def create(self):


class Ride(models.Model):
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    price = models.PositiveSmallIntegerField(null=True, editable=False, blank=True)
    start_time = models.DateTimeField(auto_now_add=True, editable=False)
    start_acknowledge_time = models.DateTimeField(null=True, editable=False, verbose_name='start ack')
    end_time = models.DateTimeField(null=True, editable=False)
    end_acknowledge_time = models.DateTimeField(null=True, editable=False, verbose_name='end ack')
    start_point_latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='start Lat', editable=False, blank=True)
    start_point_longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='start Lng', editable=False)
    end_point_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, verbose_name='end Lat', editable=False)
    end_point_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, verbose_name='end Lng', editable=False)
    is_finished = models.BooleanField(default=False)
    duration = models.FloatField(null=True, verbose_name='duration(m)', editable=False)
    distance = models.SmallIntegerField(null=True, verbose_name='distance(km)', editable=False)
    is_reversed = models.BooleanField(default=False, editable=False)

    @staticmethod
    def initiate_ride(user, scooter,):
        ride = Ride(user=user,
                    scooter=scooter,
                    start_point_latitude=scooter.latitude,
                    start_point_longitude=scooter.longitude,
                    is_finished=False)
        ride.save()
        return ride

    def __str__(self):
        return self.user.profile.name + " :" + str(self.scooter.device_code)

    def end_ride(self, is_reversed=False):
        if self.is_finished:
            data = {'error': 'error: ride is finished'}
            return Response(data, status=HTTP_400_BAD_REQUEST)
        if self.scooter.status != 2:
            data = {'error': 'error: device not occupied'}
            return Response(data, status=HTTP_400_BAD_REQUEST)
        # modify
        # really turn the device off here!
        self.end_point_latitude = self.scooter.latitude
        self.end_point_longitude = self.scooter.longitude
        self.end_time = datetime.datetime.now()
        self.distance = self.get_distance_in_kilometers()
        self.duration = self.get_duration_in_minutes()
        self.is_reversed = is_reversed
        # modify
        # charge = True means it calculates the price at the end and charges the user
        price = self.set_price_charge(charge=not is_reversed)
        self.is_finished = True
        self.save()
        # self.user.profile.save()
        self.scooter.status = 1
        self.scooter.save()
        self.scooter.turn_off()
        data = {'message': 'success: device deactivated',
                # 'device_id': device_id
                'ride_id': self.id
                }
        return Response(data, status=HTTP_200_OK)

    def get_duration_in_seconds(self):
        # t_delta = (datetime.datetime.now().replace(tzinfo=None) - self.start_time.replace(tzinfo=None)).seconds
        # modify : this is always true. why?
        print(self.start_acknowledge_time)
        if self.start_acknowledge_time is None:
            # print(self.start_acknowledge_time)
            # print('ride started but not acknowledged: return 0 for timer')
            return 0
        # print('ride started and acknowledged: return real time for timer')
        t_delta = (datetime.datetime.now() - self.start_acknowledge_time).seconds

        debug = False
        # print(datetime.datetime.now() - self.start_time)
        # return datetime.datetime.now(tz=None) - self.start_time
        time_delta = datetime.timedelta(minutes=1, seconds=10)
        if debug:
            print("\n--------")
            print(datetime.datetime.now())
            print(datetime.datetime.now().replace(tzinfo=None))
            print(datetime.datetime.now().replace(tzinfo=UTC))

            print(self.start_time)
            print(self.start_time.replace(tzinfo=None))
            print(self.start_time.replace(tzinfo=UTC))
            print("--------\n")
            print(t_delta)
        return t_delta

    def get_duration_in_minutes(self):
        return self.get_duration_in_seconds()/60

    def get_distance_in_kilometers(self):
        start_point = (self.start_point_latitude, self.start_point_longitude)
        end_point = (self.end_point_latitude, self.end_point_longitude)
        distance = geopy.distance.vincenty(start_point, end_point).km
        return distance

    def set_price_charge(self, charge=False):
        tariff = self.user.profile.tariff
        price = tariff.initial_price
        if self.duration > tariff.free_minutes:
            price += (self.duration - tariff.free_minutes) * tariff.per_minute_price
        if self.distance > tariff.free_kilometers:
            price += (self.distance - tariff.free_kilometers) * tariff.per_kilometer_price
        # print('price:')
        # print(tariff.per_minute_price)
        # print(tariff.per_kilometer_price)
        # print(self.get_duration_in_minutes())
        # print(self.get_duration_in_seconds())
        # print(self.get_distance_in_kilometers())
        # print()
        # print(tariff.initial_price)
        # print(self.get_duration_in_minutes() * tariff.per_minute_price)
        # print(self.get_distance_in_kilometers() * tariff.per_kilometer_price)
        # print(price)
        # print()
        if charge:
            self.price = price
            self.user.profile.credit -= price
            self.user.profile.save()
        else:
            self.price = 0
        self.save()
        return self.price

    @staticmethod
    @background(schedule=30)
    def reverse_started_ride(ride_id):
        # print("====== reversing initiated")
        ride = Ride.objects.get(pk=ride_id)
        if ride.start_acknowledge_time is None:
            print("ride reversed due to no response from device")
            ride.end_ride(is_reversed=True)
