from django.contrib import admin

from scooter.models import Scooter, Site, Ride, Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('scooter', 'time', 'latitude', 'longitude', 'battery', 'status')


class ScooterAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'device_code', 'qr_info', 'latitude', 'longitude', 'site', 'battery', 'status', 'activation_date', 'last_announce')


class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'scooter', 'user', 'price', 'start_time', 'end_time', 'start_point_latitude',
                    'start_point_longitude', 'end_point_latitude', 'end_point_longitude', 'is_finished')


admin.site.register(Scooter, ScooterAdmin)
admin.site.register(Site)
admin.site.register(Ride, RideAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
