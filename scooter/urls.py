from django.conf.urls import url
from django.urls import path
from scooter.views import *

urlpatterns = [
    # path('inf/', InfoView, name='info'),
    path('announce', announce_api, name='announce'),

    path('my_profile/', my_profile_api, name='my_profile'),
    path('nearby_devices/', nearby_devices_mobile_api, name='nearby_devices'),
    path('start_ride/', start_ride_mobile_api, name='start_ride'),
    # path('verify_ride/', verify_ride_mobile_api, name='verify_ride'),
    path('end_ride/', end_ride_mobile_api, name='end_ride'),
    path('sites/', sites, name='sites'),

    url(r'^ride_trajectory/(?P<ride_id>\d+)/', ride_trajectory, name='ride_trajectory'),
]
