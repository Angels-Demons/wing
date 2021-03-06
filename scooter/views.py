import datetime
import random
import time

from django.contrib.auth.decorators import login_required, permission_required
from gmplot import gmplot

from api import log
from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import AllowAny

from accounts.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)

# from ride.models import Ride
from api.my_http import my_get_object_or_404, my_get_object_or_return_404
from scooter.Serializers import ScooterSerializer, ScooterAnnounceSerializer, ProfileSerializer, \
    ScooterAnnounceSerializerFakeLocation, AnnounceSerializer, SiteSerializer
# from scooter import funcs
from scooter.models import Scooter, Ride, Announcement, DeviceType, Status, Site
import logging
from django.db.models import Q

MAXIMUM_RETRIES = 0
SLEEP_TIME = 1


def authenticate(request):
    if not ('HTTP_AUTHORIZATION' in request.META and 'phone' in request.POST):
        data = {
            "message": "error: token or phone not found",
            "message_fa": "خطا: توکن یا شماره پیدا نشد",
            "code": 301,
            "status": 401,
        }
        return Response(data, status=HTTP_401_UNAUTHORIZED)
    token = request.META['HTTP_AUTHORIZATION']
    token = str(token).split(' ')[1]
    phone = request.POST['phone']
    # if len(token) != 40:
    #     data = {'error': 'error: token or phone not found'}
    #     return Response(data, status=HTTP_404_NOT_FOUND)

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
        data = {
            "message": "error: invalid/outdated credentials",
            "message_fa": "خطا: هویت غیر معتبر/منقضی",
            "code": 300,
            "status": 401,
        }
        return Response(data, status=HTTP_401_UNAUTHORIZED)
    if owner_of_token.user == owner_of_phone:
        return owner_of_phone
    else:
        data = {
            "message": "error: invalid/outdated credentials",
            "message_fa": "خطا: هویت غیر معتبر/منقضی",
            "code": 300,
            "status": 401,
        }
        return Response(data, status=HTTP_401_UNAUTHORIZED)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def announce_api(request):
    data = request.GET.copy()
    device_code = data['device_code']
    if int(device_code) < 9999999:
        scooter = get_object_or_404(Scooter, device_code=device_code)
    else:
        scooter = get_object_or_404(Scooter, imei=device_code)
    data['scooter'] = scooter.id
    if scooter.current_ride:
        data['ride'] = scooter.current_ride.id
        # modify: retrieve the ack start or end individually from current ride with small overhead
        # if scooter.current_ride.start_acknowledge_time is None:
        #     data['ack_start'] = True

    announce = AnnounceSerializer(data=data)
    if not announce.is_valid():
        return Response(str(announce.errors), status=HTTP_400_BAD_REQUEST)
    announce = announce.save()
    scooter.last_announce = announce.time
    scooter.save()

    # modify: comment out later until code_61 --------- [after gps_valid is sent]
    if announce.latitude == 0 and announce.longitude == 0:
        data['gps_valid'] = False
        instance = ScooterAnnounceSerializerFakeLocation(instance=scooter, data=data)
    else:
        data['gps_valid'] = True
        instance = ScooterAnnounceSerializer(instance=scooter, data=data)
    # code_61 -----------------------------------------

    # modify: uncomment later until code_62 --------- [after gps_valid is sent]
    # if announce.gps_valid:
    #     instance = ScooterAnnounceSerializerFakeLocation(instance=scooter, data=data)
    # else:
    #     instance = ScooterAnnounceSerializer(instance=scooter, data=data)
    # code_62 ---------------------------------------

    if not instance.is_valid():
        return Response(str(instance.errors), status=HTTP_400_BAD_REQUEST)

    error = ""
    instance.save()
    if announce.ack_start:
        try:
            ride = Ride.objects.filter(scooter=scooter, is_finished=False, start_acknowledge_time=None).last()
            ride.start_acknowledge_time = datetime.datetime.now()
            ride.save()
            ride.initiate_payout_counter()
        except AttributeError as e:
            error += "invalid start ack"

    if announce.ack_end:
        try:
            ride = Ride.objects.filter(scooter=scooter, is_finished=True, end_acknowledge_time=None).last()
            ride.end_acknowledge_time = datetime.datetime.now()
            ride.save()
        except AttributeError as e:
            error += "invalid end ack"

    # modify: comment out later until code_63 --------- [after ack_start and ack_end is sent]
    try:
        # check if this is start ack
        ride = Ride.objects.filter(scooter=scooter, is_finished=False, start_acknowledge_time=None).last()
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

    # code_63 -------------------------------------------------------------------------------

    data = {'message': 'success: announce received',
            'status': scooter.status,
            'warning': error
            }
    return Response(data, status=HTTP_200_OK)


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

    if 'qr_info' in request.POST:
        # scooter = get_object_or_404(Scooter, qr_info=request.POST['qr_info'])
        scooter = Scooter.objects.filter(qr_info=request.POST['qr_info'], site=user.profile.site).first()
        if scooter:
            return scooter.start_ride_atomic(user=user)
            # return scooter.start_ride(user=user)
    if 'device_code' in request.POST:
        # scooter = get_object_or_404(Scooter, device_code=request.POST['device_code'])
        scooter = Scooter.objects.filter(device_code=request.POST['device_code'], site=user.profile.site).first()
        if scooter:
            return scooter.start_ride_atomic(user=user)
            # return scooter.start_ride(user=user)
        else:
            data = {
                "message": "error: invalid QR or device code",
                "message_fa": "خطا: کد تصویری/ کد دستگاه نامعتبر یا خارج سازمانی",
                "code": 200,
                "status": 404,
            }
            return Response(data, HTTP_404_NOT_FOUND)

    data = {
        "message": "error: no qr_info or device_code was found in request",
        "message_fa": "خطا: کد تصویری یا کد دستگاه در درخواست یافت نشد",
        "code": 201,
        "status": 400,
    }
    return Response(data, HTTP_400_BAD_REQUEST)
    # scooter = get_object_or_404(Scooter, Q(qr_info=qr_info) or Q(device_code=device_code))


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
def end_ride_mobile_api(request):
    user = authenticate(request)
    if not isinstance(user, User):
        return user

    ride = user.profile.current_ride
    if not ride:
        # MODIFY: REDUNDANCY 65 =====================================================
        current_user_rides = Ride.objects.filter(user=user, is_finished=False)
        if current_user_rides:
            for ride in current_user_rides:
                ride.end_ride_atomic()
            logging.error("end_ride for User(%s) did not find current_ride but ended %d unfinished rides manually"
                          % (user.phone, current_user_rides.count()))
            log.error("end_ride did not find current_ride but ended %d unfinished rides manually"
                      % current_user_rides.count(), user)

            data = {
                "message": "error: user has unfinished ride",
                "message_fa": "خطا: کاربر سفر ناتمام دارد",
                "code": 901,
                "status": 400,
            }
            return Response(data, status=HTTP_400_BAD_REQUEST)
        # MODIFY: REDUNDANCY 65 =====================================================
        data = {
            "message": "error: user is not riding",
            "message_fa": "خطا: کاربر در حال سفر نیست",
            "code": 201,
            "status": 400,
        }
        return Response(data, status=HTTP_400_BAD_REQUEST)
    # ride = get_object_or_404(Ride, user=user, is_finished=False)
    if ride.scooter.type == DeviceType.Bicycle.value and ride.scooter.device_status == Status.Occupied.value:
        ride.scooter.turn_off()
        data = {
            "message": "error: lock the bike and retry again",
            "message_fa": "خطا: ابتدا قفل دوچرخه را ببندید و دوباره تلاش کنید",
            "code": 211,
            "status": 400,
        }
        return Response(data, status=HTTP_400_BAD_REQUEST)
    return ride.end_ride_atomic()


@csrf_exempt
@api_view(["POST"])
# @permission_classes((AllowAny,))
def my_profile_api(request):
    user = authenticate(request)
    if not isinstance(user, User):
        return user
    if 'app_version' in request.POST:
        user.profile.app_version = request.POST['app_version']
        user.profile.save()

    if 'site' and 'name' and 'code' in request.POST:
        if int(request.POST['site']) == 0:
            user.profile.site = None
            user.profile.member_code = None
            user.profile.save()
        else:
            user.profile.site_id = Site.objects.get(id=request.POST['site']).id
            user.profile.name = request.POST['name']
            user.profile.member_code = request.POST['code']
            user.profile.save()

    # return MyStateSerializer.make_my_state(user.profile)
    return Response(ProfileSerializer(user.profile).data)


@csrf_exempt
@api_view(["POST"])
# @permission_classes((AllowAny,))
def sites(request):
    user = authenticate(request)
    if not isinstance(user, User):
        return user
    return Response(SiteSerializer(Site.objects.all(), many=True).data)


@login_required
# @permission_required('zarinpal.top_up', login_url="/admin")
def ride_trajectory(request, ride_id):
    ride = Ride.objects.get(pk=ride_id)

    latitude_list = []
    longitude_list = []
    print(ride.announcement_set.count())
    for announce in ride.announcement_set.all():
        latitude_list.append(float(announce.latitude))
        longitude_list.append(float(announce.longitude))

    # gmap3 = gmplot.GoogleMapPlotter(30.3164945,
    #                                 78.03219179999999, 13)

    gmap3 = gmplot.GoogleMapPlotter(35.801571, 51.491839, 20)
    # scatter method of map object
    # scatter points on the google map
    gmap3.scatter(latitude_list, longitude_list, '# FF0000',
                  size=40, marker=False)

    # Plot method Draw a line in
    # between given coordinates
    gmap3.plot(latitude_list, longitude_list,
               'cornflowerblue', edge_width=2.5)
    # file_name = "/scooter/templates/scoooter/ride_trajectory/%s.html" % str(ride_id)
    file_name = "%s.html" % str(ride_id)
    # file_name = "/home/ubuntu/wing-server/production/wing/scooter/ride_trajectory/1.html"
    # f = open(file_name, 'a')
    # f.write("")
    # f.close()
    gmap3.draw(file_name)
    return render(request, "scooter/ride_trajectory/1.html")
