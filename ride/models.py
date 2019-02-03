import datetime

from django.db import models

from accounts.models import User
from scooter import funcs
# from scooter.models import Scooter

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

from scooter.models import Scooter

#
# class Ride(models.Model):
#     scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     price = models.PositiveSmallIntegerField(null=True)
#     start_time = models.DateTimeField(auto_now_add=True)
#     end_time = models.DateTimeField(null=True)
#     start_point_latitude = models.DecimalField(max_digits=9, decimal_places=6)
#     start_point_longitude = models.DecimalField(max_digits=9, decimal_places=6)
#     end_point_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
#     end_point_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
#     is_finished = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.user.profile.name + " :" + str(self.scooter.device_code)
#
#     def end_ride(self):
#         if self.is_finished:
#             data = {'error': 'error: ride is finished'}
#             return Response(data, status=HTTP_400_BAD_REQUEST)
#         if self.scooter.status != 2:
#             data = {'error': 'error: device not occupied'}
#             return Response(data, status=HTTP_400_BAD_REQUEST)
#         # modify
#         # really turn the device off here!
#         self.scooter.turn_off()
#         self.end_point_latitude = self.scooter.latitude
#         self.end_point_longitude = self.scooter.longitude
#         self.end_time = datetime.datetime.now()
#         self.save()
#         self.price = funcs.price(self)
#         self.is_finished = True
#         self.save()
#         self.user.profile.credit -= self.price
#         self.user.profile.save()
#         self.scooter.status = 1
#         self.scooter.save()
#         data = {'message': 'success: device deactivated',
#                 # 'device_id': device_id
#                 'ride_id': self.id
#                 }
#         return Response(data, status=HTTP_200_OK)
