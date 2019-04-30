from django.contrib import admin

from scooter.models import Scooter, Site, Ride, Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('scooter', 'time', 'latitude', 'longitude', 'battery', 'device_status')


class ScooterAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'device_code', 'latitude', 'longitude', 'site', 'battery', 'status',
                    'device_status',
                    'qr_info',
                    'last_announce', 'activation_date')


class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'scooter', 'user', 'price', 'is_finished',
                    'duration', 'distance',
                    'start_time', 'end_time',
                    'start_point_latitude', 'start_point_longitude', 'end_point_latitude', 'end_point_longitude',
                    )


admin.site.register(Scooter, ScooterAdmin)
admin.site.register(Site)
admin.site.register(Ride, RideAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
