import datetime
import socket
import traceback
from enum import Enum

from api import log
from background_task import background
from django.db.models import SET_NULL
from pytz import UTC

from api import sms_send, sms, mqtt
from django.db import models, transaction
from accounts.models import User
# from ride.models import Ride
import geopy.distance
from django.core.validators import MinValueValidator
from fleet.models import Fleet
from decimal import Decimal

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

seconds_in_a_minute = 60
half_a_minute = 60

# modify
# try:
#     fleet = Fleet.objects.filter(active=True).first()
#     business_model = Bus
# except:
#     fleet = Fleet(payout_period_minutes=10,
#                   minimum_battery=30,
#                   time_threshold=300,
#                   active=True)
#     # fleet.save()
#
# every_n_minute_charging = fleet.business_model.every_n_minute_charging
# payout_period_minutes = fleet.payout_period_minutes
# minimum_battery = fleet.minimum_battery
# time_threshold = fleet.time_threshold
#
# print(every_n_minute_charging + payout_period_minutes + minimum_battery)


try:
    fleet = Fleet.objects.filter(active=True).first()
    every_n_minute_charging = fleet.business_model.every_n_minute_charging
    payout_period_minutes = fleet.payout_period_minutes
    minimum_battery = fleet.minimum_battery
    time_threshold = fleet.time_threshold
    print(fleet)
except:
    every_n_minute_charging = True
    payout_period_minutes = 1
    minimum_battery = 30
    time_threshold = 300

print(every_n_minute_charging + payout_period_minutes + minimum_battery)


@background(schedule=half_a_minute)
def check_for_unattached_scooters(counter=0):
    print(str(counter) + " :Checking for unattached scooters at: " + str(datetime.datetime.now()))
    occupied_scooters = Scooter.objects.filter(status=2)
    for scooter in occupied_scooters:
        if scooter.current_ride is None:
            print("Buggy scooter (occupied with None current_ride) fixed. device_code: " + str(scooter.device_code))
            log.error("Buggy scooter (occupied with None current_ride) fixed. device_code: " + str(scooter.device_code))
            scooter.status = 1
            scooter.save()
        # elif Ride.objects.filter(scooter=scooter, is_finished=False).count() != 1:
        # # print(Ride.objects.filter(scooter=scooter, is_finished=False).count())
        #     print("Checker detected a buggy scooter (occupied with no ride attached) " + str(scooter.device_code))
        #     scooter.status = 1
        #     scooter.save()

    check_for_unattached_scooters(counter+1)


class DeviceType(Enum):
    Scooter = 1
    Bicycle = 2


class Status(Enum):
    Ready = 1
    Occupied = 2


class Choices:
    scooter_status_choices = (
        (Status.Ready.value, Status.Ready.name),
        (Status.Occupied.value, Status.Occupied.name),
        # (3, 'low_battery'),
        # (4, 'unavailable'),
        # (5, ''),
        # (6, ''),
    )

    device_type_choices = (
        (DeviceType.Scooter.value, DeviceType.Scooter.name),
        (DeviceType.Bicycle.value, DeviceType.Bicycle.name),
    )


class Site(models.Model):
    name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, editable=False)

    def __str__(self):
        return self.name


def lock(IMEI):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 1234)
    sock.connect(server_address)
    # token,lock/unlock,IMEI
    token = b'afvafvafsdvaf'
    message = token + b',' + b'lock' + b',' + IMEI.encode()
    print('sending {!r}'.format(message))
    sock.sendall(message)


def unlock(IMEI):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 1234)
    sock.connect(server_address)
    # token,lock/unlock,IMEI
    token = b'afvafvafsdvaf'
    message = token + b',' + b'unlock' + b',' + IMEI.encode()
    print('sending {!r}'.format(message))
    sock.sendall(message)


class Scooter(models.Model):
    type = models.PositiveSmallIntegerField(choices=Choices.device_type_choices, default=DeviceType.Scooter.value)
    phone_number = models.BigIntegerField(unique=True)
    device_code = models.BigIntegerField(unique=True)
    imei = models.BigIntegerField(unique=True, null=True, blank=True)
    current_ride = models.OneToOneField('scooter.Ride', null=True, blank=True, on_delete=SET_NULL, editable=True, related_name="current_ride")
    qr_info = models.CharField(max_length=255, null=True, unique=True)
    # rider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # has credit
    # has internet package
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    battery = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])
    status = models.PositiveSmallIntegerField(choices=Choices.scooter_status_choices)
    device_status = models.PositiveSmallIntegerField(choices=Choices.scooter_status_choices, default=1)
    activation_date = models.DateTimeField(auto_now_add=True)
    last_announce = models.DateTimeField(null=True, blank=True)
    is_operational = models.BooleanField(default=False)
    modem_ssid = models.CharField(max_length=255, null=True, blank=True)
    modem_password = models.CharField(max_length=255, null=True, blank=True)
    gps_board_connected = models.BooleanField(default=True, verbose_name="GPS Board")
    gps_valid = models.BooleanField(default=True)
    alerted = models.BooleanField(default=False)

    # def save(self, *args, **kwargs):
    #     ride = Ride.objects.filter(scooter=self, is_finished=False).first()
    #     print(self.get_deferred_fields().__sizeof__())
    #     print(self._meta.concrete_fields)
    #     if not ride and 0:
    #         pass
    #     super(Scooter, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.device_code)

    def start_ride(self, user):
        if user.profile.current_ride is not None:
            data = {
                "message": "error: user is already on a ride",
                "message_fa": "خطا: کاربر در حال سفر است",
                "code": 202,
                "status": 400,
            }
            return Response(data, status=HTTP_400_BAD_REQUEST)

        # MODIFY: REDUNDANCY 55 =====================================================
        current_user_rides = Ride.objects.filter(user=user, is_finished=False)
        if current_user_rides:
            for ride in current_user_rides:
                ride.end_ride_atomic()
            # logging.error("start_ride for User(%s) failed with %d unfinished rides (ended manually)"
            #               % (user.phone, current_user_rides.count()))
            log.error("start_ride failed with %d unfinished rides (ended manually)"
                      % current_user_rides.count(), user)

            data = {
                "message": "error: user has unfinished ride",
                "message_fa": "خطا: کاربر سفر ناتمام دارد",
                "code": 901,
                "status": 400,
            }
            return Response(data, status=HTTP_400_BAD_REQUEST)
        # MODIFY: REDUNDANCY 55 =====================================================

        if self.status != 1:
            data = {
                "message": "error: device is not free",
                "message_fa": "خطا: دستگاه در حالت آزاد نمی باشد",
                "code": 203,
                "status": 400,
            }
            return Response(data, status=HTTP_400_BAD_REQUEST)

        # modify maybe: (if status == LOW_BATTERY)
        if self.battery < minimum_battery and self.is_operational:
            data = {
                "message": "error: device has low battery",
                "message_fa": "خطا: باتری دستگاه کم شارژ است",
                "code": 204,
                "status": 200,
            }
            return Response(data, status=HTTP_200_OK)

        if every_n_minute_charging and user.profile.credit < user.profile.tariff.per_minute_price * payout_period_minutes:
            data = {
                "message": "error: not enough credit",
                "message_fa": "خطا: اعتبار شما برای شروع سفر کافی نیست",
                "code": 205,
                "minimum_credit": user.profile.tariff.per_minute_price * payout_period_minutes,
                "status": 200,
            }
            return Response(data, status=HTTP_200_OK)

        if user.profile.credit < user.profile.tariff.minimum_credit:
            data = {
                "message": "error: not enough credit (tariff)",
                "message_fa": "خطا: اعتبار شما برای شروع سفر کافی نیست (تعرفه)",
                "code": 206,
                "minimum_credit": user.profile.tariff.minimum_credit,
                "status": 200,
            }
            return Response(data, status=HTTP_200_OK)

        ride = Ride.initiate_ride(user=user, scooter=self)
        data = {
            "message": "success: activating device",
            "message_fa": "موفق: در حال روشن کردن دستگاه",
            # for compatibility
            "ride_id": ride.id,
            "code": 100,
            # "status": 200,

            "device_code": ride.scooter.device_code,
            "latitude": ride.scooter.latitude,
            "longitude": ride.scooter.longitude,
            "battery": ride.scooter.battery,
            "type": ride.scooter.type,
            "status": ride.scooter.status
        }
        return Response(data, status=HTTP_200_OK)

    # modify
    def turn_on(self):
        if self.type == DeviceType.Scooter.value:
            # sms.lock_unlock(self.phone_number, False, self.device_code)
            mqtt.send_mqtt('scooter/' + str(self.phone_number), 'unlock')
            mqtt.send_mqtt('scooter/' + str(self.device_code), 'unlock')
        elif self.type == DeviceType.Bicycle.value:
            unlock(str(self.imei))
        else:
            raise ValueError("invalid device type")

    # modify
    def turn_off(self):
        if self.type == DeviceType.Scooter.value:
            # sms.lock_unlock(self.phone_number, True, self.device_code)
            mqtt.send_mqtt('scooter/' + str(self.phone_number), 'lock')
            mqtt.send_mqtt('scooter/' + str(self.device_code), 'lock')
        elif self.type == DeviceType.Bicycle.value:
            lock(str(self.imei))
        else:
            raise ValueError("invalid device type")

    def start_ride_atomic(self, user):
        if self.type == DeviceType.Bicycle.value and self.device_status == Status.Occupied.value:
            data = {
                "message": "error: bike is not locked",
                "message_fa": "خطا: قفل دوچرخه باز است!",
                "code": 211,
                "status": 400,
            }
            return Response(data, status=HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                return self.start_ride(user=user)
        except Exception as e:
            log.error(message=e.__str__() + "\n" + str(traceback.format_exc()), user=user)
            data = {
                "message": "error: unknown error",
                "message_fa": "خطا: خطای ناشناخته",
                "code": 501,
                "status": 500,
            }
            return Response(data, status=HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def nearby_devices(latitude, longitude, radius, user):
        nearby = []
        ride = Ride.objects.filter(user=user, is_finished=False).first()
        if ride:
            nearby.append(ride.scooter)
            return nearby
        scooters = Scooter.objects.filter(is_operational=True, site=user.profile.site)
        for scooter in scooters:
            if abs((scooter.latitude + scooter.longitude) - (Decimal(latitude) + Decimal(longitude))) < 2 * Decimal(
                    radius):
                nearby.append(scooter)
        return nearby


class Ride(models.Model):
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    price = models.PositiveIntegerField(null=True, editable=False, blank=True)
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
    is_terminated = models.BooleanField(default=False, editable=False)

    @staticmethod
    def initiate_ride(user, scooter):
        ride = Ride(user=user,
                    scooter=scooter,
                    start_point_latitude=scooter.latitude,
                    start_point_longitude=scooter.longitude,
                    price=0,
                    is_finished=False)
        ride.save()
        ride.reverse_started_ride(ride_id=ride.id)
        user.profile.current_ride = ride
        user.profile.save()
        scooter.current_ride = ride
        scooter.status = 2
        scooter.save()
        # modify: make sure it works!
        # transaction.on_commit(scooter.turn_on())
        scooter.turn_on()
        return ride

    def initiate_payout_counter(self):
        if every_n_minute_charging:
            print("This is initiate_payout_counter method for ride " + str(self.id))
            self.count_for_next_payout(ride_id=self.id, counter=1)
            self.subtract_payout_of_period()

    def __str__(self):
        label = "user: " + str(self.user.phone) + "\n"
        label += "device_code: " + str(self.scooter.device_code) + "\n"
        label += "ride_id: " + str(self.id)
        return label

    def end_ride_atomic(self, is_reversed=False):
        try:
            with transaction.atomic():
                return self.end_ride(is_reversed=is_reversed)
        except Exception as e:
            log.error(message=e.__str__() + "\n" + str(traceback.format_exc()), user=self.user)
            data = {
                "message": "error: unknown error",
                "message_fa": "خطا: خطای ناشناخته",
                "code": 501,
                "status": 500,
            }
            return Response(data, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def end_ride(self, is_reversed=False):
        # if self.is_finished:
        #     data = {
        #         "message": "error: ride is finished",
        #         "message_fa": "خطا: سفر به پایان رسیده است",
        #         "code": 202,
        #         "status": 400,
        #     }
        #     return Response(data, status=HTTP_400_BAD_REQUEST)
        # if self.scooter.status != 2:
        #     data = {
        #         "message": "error: device not occupied",
        #         "message_fa": "خطا: دستگاه در حال استفاده نمی باشد",
        #         "code": 203,
        #         "status": 400,
        #     }
        #     return Response(data, status=HTTP_400_BAD_REQUEST)
        self.end_point_latitude = self.scooter.latitude
        self.end_point_longitude = self.scooter.longitude
        self.end_time = datetime.datetime.now()
        self.distance = self.get_distance_in_kilometers()
        self.duration = self.get_duration_in_minutes()
        self.is_reversed = is_reversed
        if not every_n_minute_charging:
            self.set_price_charge(charge=not is_reversed)

        self.is_finished = True
        self.save()
        self.user.profile.current_ride = None
        self.user.profile.save()
        self.scooter.current_ride = None
        self.scooter.status = 1
        self.scooter.save()
        self.scooter.turn_off()
        data = {
            "message": "success: deactivating device",
            "message_fa": "موفق: در حال خاموش کردن دستگاه",
            "code": 100,
            "status": 200,
        }
        return Response(data, status=HTTP_200_OK)

    def get_duration_in_seconds(self):
        # t_delta = (datetime.datetime.now().replace(tzinfo=None) - self.start_time.replace(tzinfo=None)).seconds
        # modify : this is always true. why?
        # print(self.start_acknowledge_time)
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

    def subtract_payout_of_period(self):
        period_price = self.user.profile.tariff.per_minute_price * payout_period_minutes
        if self.user.profile.credit < period_price:
            self.is_terminated = True
            self.save()
            self.end_ride_atomic()
        else:
            self.user.profile.credit -= period_price
            self.price += period_price
            self.save()
            self.user.profile.save()

    @staticmethod
    @background(schedule=30)
    def reverse_started_ride(ride_id):
        # print("====== reversing initiated")
        ride = Ride.objects.get(pk=ride_id)
        if ride.start_acknowledge_time is None:
            print("ride reversed due to no response from device")
            ride.end_ride_atomic(is_reversed=True)

    @staticmethod
    @background(schedule=payout_period_minutes * seconds_in_a_minute)
    def count_for_next_payout(ride_id, counter):
        print("counter executed for ride with id: " + str(ride_id) + " with period number " + str(counter))
        ride = Ride.objects.get(pk=ride_id)
        if not ride.is_finished:
            ride.subtract_payout_of_period()
            # print("initiating next counter for ride with id: " + str(ride_id))
            ride.count_for_next_payout(ride_id=ride_id, counter=counter+1)


class Announcement(models.Model):
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE)
    ride = models.ForeignKey(Ride, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    battery = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])
    device_status = models.PositiveSmallIntegerField(choices=Choices.scooter_status_choices)
    gps_board_connected = models.BooleanField(default=True)
    gps_valid = models.BooleanField(default=True)
    ack_start = models.BooleanField(default=False)
    ack_end = models.BooleanField(default=False)
    alerted = models.BooleanField(default=False)
