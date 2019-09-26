import datetime

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from scooter.models import Scooter, Site, Ride, Announcement, time_threshold


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('scooter', 'ride', 'time', 'latitude', 'longitude', 'battery', 'device_status',
                    'gps_board_connected', 'gps_valid', 'ack_start', 'ack_end', 'alerted')
    search_fields = ['scooter__device_code']


class IsAliveFilter(admin.SimpleListFilter):
    title = 'alive'
    parameter_name = 'alive'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            # return (datetime.datetime.now() - obj.last_announce).seconds < time_threshold
            # return queryset.filter(benevolence_factor__gt=75)
            alive_scooters = []
            for scooter in queryset:
                if (datetime.datetime.now() - scooter.last_announce).seconds < time_threshold:
                    alive_scooters.append(scooter)
            return alive_scooters
        elif value == 'No':
            # return queryset.exclude(benevolence_factor__gt=75)
            not_alive_scooters = []
            for scooter in queryset:
                if not (datetime.datetime.now() - scooter.last_announce).seconds < time_threshold:
                    not_alive_scooters.append(scooter)
            return not_alive_scooters
        return queryset


class ScooterAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'device_code', '_current_ride', 'latitude', 'longitude',
                    'site', 'battery', 'status', 'device_status', 'alerted',
                    'alive', 'gps_board_connected', 'gps_valid',
                    'qr_info',
                    'last_announce', 'activation_date',
                    'is_operational', 'modem_ssid', 'modem_password',)
    # list_filter = ('IsAliveFilter', 'is_operational', 'status', 'device_status', 'last_announce')
    list_filter = ('is_operational', 'status', 'device_status', 'last_announce')
    search_fields = ('phone_number', 'device_code',)

    def alive(self, obj):
        try:
            return (datetime.datetime.now() - obj.last_announce).seconds < time_threshold
        except Exception:
            return False
    alive.boolean = True
    alive.allow_tags = True

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
