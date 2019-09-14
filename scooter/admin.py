from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from scooter.models import Scooter, Site, Ride, Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('scooter', 'time', 'latitude', 'longitude', 'battery', 'device_status')
    search_fields = ('scooter__device_code',)


class ScooterAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'device_code', '_current_ride', 'latitude', 'longitude',
                    'site', 'battery', 'status', 'device_status',
                    'qr_info',
                    'last_announce', 'activation_date',
                    'is_operational', 'modem_ssid', 'modem_password',)
    list_filter = ('is_operational', 'status', 'device_status', 'activation_date')
    search_fields = ('phone_number', 'device_code',)

    def _current_ride(self, obj):
        try:
            link = reverse("admin:scooter_ride_change", args=[obj.current_ride.id]) #model name has to be lowercase
            return format_html(u'<a href="%s">%s</a>' % (link, obj.current_ride))
        except:
            return None
    _current_ride.allow_tags = True


def end_ride_manually(modeladmin, request, queryset):
    for ride in queryset:
        if ride.is_finished:
            continue
        ride.end_ride()


end_ride_manually.short_description = "End selected rides manually"


class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'scooter', 'user', 'price', 'is_finished', 'is_reversed', 'is_terminated',
                    'duration', 'distance',
                    'start_time', 'start_acknowledge_time',
                    'end_time', 'end_acknowledge_time',
                    'start_point_latitude', 'start_point_longitude', 'end_point_latitude', 'end_point_longitude',
                    )
    actions = [end_ride_manually]
    list_filter = ('is_reversed', 'is_terminated')
    search_fields = ('scooter__device_code', 'user__phone')


admin.site.register(Scooter, ScooterAdmin)
admin.site.register(Site)
admin.site.register(Ride, RideAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
