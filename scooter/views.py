import datetime
import random
import time

from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny

from accounts.models import User, UserManager, create_profile

from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

# from ride.models import Ride
from api.my_http import my_get_object_or_404, my_get_object_or_return_404
from scooter.Serializers import ScooterSerializer, ScooterAnnounceSerializer, ProfileSerializer, ScooterAnnounceSerializerFakeLocation
# from scooter import funcs
from scooter.models import Scooter, Ride, Announcement
import logging
from django.db.models import Q

MAXIMUM_RETRIES = 0
SLEEP_TIME = 1


def authenticate(request):
    token = request.META['HTTP_AUTHORIZATION']
    token = str(token).split(' ')[1]
    phone = request.POST['phone']

    if len(token) != 40:
        data = {'error': 'error: token or phone not found'}
        return Response(data, status=HTTP_404_NOT_FOUND)

    owner_of_phone = User.objects.filter(phone=phone).first()
    owner_of_token = Token.objects.filter(key=token).first()
    if not owner_of_phone or not owner_of_token:
        # TEMPORARY: commented already =====================================
        # print("Here:")
        # print(phone)
        # print(token)
        # print("")
        # f = open("users.txt", "a")
        # f.write(phone)
        # f.write("\n")
        # f.write(token)
        # f.write("\n")
        # f.close()
        # # user exists but token is invalid
        # if owner_of_phone:
        #     old_token = Token.objects.filter(user=owner_of_phone).first()
        #     if old_token:
        #         old_token.delete()
        #         # old_token.key = token
        #         # old_token.save()
        #     else:
        #         new_token = Token(key=token, user=owner_of_phone)
        #         new_token.save()
        #     return owner_of_phone
        # if owner_of_token:
        #     data = {'error': 'error: invalid credentials'}
        #     return Response(data, status=HTTP_400_BAD_REQUEST)
        # else:
        #     manager = UserManager()
        #     user = manager.create_user(phone, 1111)
        #     # modify
        #     # you can set the tariff_id here
        #     profile = create_profile(user)
        #     return profile.user

        # till here ============================================= 55

        # Temporary : uncommented already the next 2 lines
        data = {'error': 'error: token or phone not found'}
        return Response(data, status=HTTP_404_NOT_FOUND)
    if owner_of_token.user == owner_of_phone:
        return owner_of_phone
    else:
        data = {'error': 'error: invalid credentials'}
        return Response(data, status=HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def announce_api(request):
    # returns error_500 if the parameters are wrong
    device_code = request.GET['device_code']
    # scooter = Scooter.objects.get(device_code=device_code)
    scooter = get_object_or_404(Scooter, device_code=device_code)
    # return scooter.announce(request)

    data = request.GET.copy()
    del data['device_code']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    gps_board_connected = False
    # gps_valid = False
    try:
        gps_board_connected = data['gps_board_connected']
        # gps_valid_data = data['gps_valid']
    except Exception:
        pass
    if latitude == 0 and longitude == 0:
        data['gps_valid'] = False
        # print("got 0 coordinates")
        instance = ScooterAnnounceSerializerFakeLocation(instance=scooter, data=data)
    else:
        data['gps_valid'] = True
        instance = ScooterAnnounceSerializer(instance=scooter, data=data)

    if instance.is_valid():
        # print('valid announcement')
        instance.save()
        try:
            # check if this is start ack
            ride = Ride.objects.get(scooter=scooter, is_finished=False, start_acknowledge_time=None)
            if ride.scooter.device_status == ride.scooter.status:
                ride.start_acknowledge_time = datetime.datetime.now()
                ride.save()
                ride.initiate_payout_counter()
        except:
            pass
        try:
            # check if this is end ack
            ride = Ride.objects.filter(scooter=scooter, is_finished=True, end_acknowledge_time=None).last()

            if ride.scooter.device_status == ride.scooter.status:
                ride.end_acknowledge_time = datetime.datetime.now()
                ride.save()
        except:
            pass

        announcement = Announcement(
            scooter=scooter,
            latitude=latitude,
            longitude=longitude,
            battery=scooter.battery,
            device_status=scooter.device_status,
            gps_board_connected=gps_board_connected,
            gps_valid=data['gps_valid'],
        )
        announcement.save()

        scooter.last_announce = announcement.time
        scooter.save()
        data = {'message': 'success: announce received',
                'status': scooter.status,
                }
        return Response(data, status=HTTP_200_OK)
        # return Response('announced', status=HTTP_200_OK)

    else:
        print(instance.errors)
        return Response('announcement not valid', status=HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
# @permission_classes((AllowAny,))
def nearby_devices_mobile_api(request):
    user = authenticate(request)
    if not isinstance(user, User):
        return user
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    radius = request.POST['radius']
    return Response(ScooterSerializer(Scooter.nearby_devices(latitude, longitude, radius, user), many=True).data)


@csrf_exempt
@api_view(["POST"])
# @permission_classes((AllowAny,))
def start_ride_mobile_api(request):
    user = authenticate(request)
    if not isinstance(user, User):
        return user
    try:
        qr_info = request.POST['qr_info']
        scooter = get_object_or_404(Scooter, qr_info=qr_info)
    except:
        device_code = request.POST['device_code']
        scooter = get_object_or_404(Scooter, device_code=device_code)
    # scooter = Scooter.objects.filter(Q(qr_info=qr_info) or Q(device_code=device_code)).first()
    # scooter = get_object_or_404(Scooter, Q(qr_info=qr_info) or Q(device_code=device_code))
    # if not scooter:
    #     data = {'error': 'error: not a valid qr code'}
    #     return Response(data, status=HTTP_404_NOT_FOUND)
    return scooter.start_ride(user=user)


@csrf_exempt
@api_view(["POST"])
# @permission_classes((AllowAny,))
def verify_ride_mobile_api(request):
    user = authenticate(request)
    if not isinstance(user, User):
        return user
    # ride = Ride.objects.get(user=user, is_finished=False)
    ride = get_object_or_404(Ride, user=user, is_finished=False)
    retries = 0
    while True:
        # print(ride.scooter.device_status)
        if ride.scooter.device_status == 2:
            data = {'message': 'success: device activated',
                    # 'device_id': device_id
                    'activated': True,
                    'timer': ride.get_duration_in_seconds()
                    }
            return Response(data, status=HTTP_200_OK)
        else:
            if retries >= MAXIMUM_RETRIES:
                data = {'message': 'failure: device not activated',
                        # 'device_id': device_id
                        'activated': False
                        }
                return Response(data, status=HTTP_200_OK)
            time.sleep(SLEEP_TIME)
            retries += 1
            print("waiting for scooter request ...\tnumber of retries: " + str(retries))
            logging.info("waiting for scooter request ...\tnumber of retries: " + str(retries))


@csrf_exempt
@api_view(["POST"])
# @permission_classes((AllowAny,))
def end_ride_mobile_api(request):
    user = authenticate(request)
    if not isinstance(user, User):
        return user

    # ride_id = request.POST['ride_id']
    # print(ride_id)
    # print(type(ride_id))
    # ride = Ride.objects.get(pk=ride_id)
    # if not ride.user == user:
    #     data = {'error': 'error: you can only end your own ride'}
    #     return Response(data, status=HTTP_400_BAD_REQUEST)

    # ride = Ride.objects.get(user=user, is_finished=False)
    ride = get_object_or_404(Ride, user=user, is_finished=False)
    # ride = my_get_object_or_return_404(Ride, user=user, is_finished=False)
    return ride.end_ride()


@csrf_exempt
@api_view(["POST"])
# @permission_classes((AllowAny,))
def my_profile_api(request):
    user = authenticate(request)
    if not isinstance(user, User):
        return user
    # return MyStateSerializer.make_my_state(user.profile)
    return Response(ProfileSerializer(user.profile).data)


# class InfoView(APIView):
#     def post(self, request):
#         print('im here')
#         # phone = request.POST['phone']
#         # token = request.POST['token']
#         return Response('hey')
