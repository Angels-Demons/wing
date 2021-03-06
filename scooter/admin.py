import datetime

from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html

from scooter.models import Scooter, Site, Ride, Announcement, time_threshold


def is_owner(user):
    (owners_group, created) = Group.objects.get_or_create(name='owners')
    if user in owners_group.user_set.all():
        print("user is owner")
        return True
    print("user is not owner")
    return False


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('scooter', 'ride', 'time', 'latitude', 'longitude', 'battery', 'device_status',
                    'gps_board_connected', 'gps_valid', 'ack_start', 'ack_end', 'alerted')
    search_fields = ['scooter__device_code']

    def get_queryset(self, request):
        if is_owner(request.user):
            return super().get_queryset(request).filter(scooter__site=request.user.owner.site)
        return super().get_queryset(request)


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
    list_display = ('device_code', 'type', 'site', 'phone_number', '_current_ride', 'latitude', 'longitude',
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

    def get_queryset(self, request):
        if is_owner(request.user):
            return super().get_queryset(request).filter(site=request.user.owner.site)
        return super().get_queryset(request)


def end_ride_manually(modeladmin, request, queryset):
    for ride in queryset:
        if ride.is_finished:
            continue
        ride.end_ride_atomic()


end_ride_manually.short_description = "End selected rides manually"


class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'scooter', 'user', 'price', 'is_finished', 'is_reversed', 'is_terminated',
                    'trajectory',
                    'duration', 'distance',
                    'start_time', 'start_acknowledge_time',
                    'end_time', 'end_acknowledge_time',
                    'start_point_latitude', 'start_point_longitude', 'end_point_latitude', 'end_point_longitude',
                    )
    actions = [end_ride_manually]
    list_filter = ('is_reversed', 'is_terminated')
    search_fields = ('scooter__device_code', 'user__phone')

    def trajectory(self, obj):
        try:
            link = "/../../../scooter/ride_trajectory/" + str(obj.id)
            # link = reverse("admin:scooter_ride_change", args=[obj.current_ride.id])  # model name has to be lowercase
            return format_html(
                """<input type="button" style="margin:2px;2px;2px;2px;" value="%s" onclick = "location.href=\'%s\'"/>"""
                % ("trajectory", link))
        except Exception as e:
            print(e)
            return None

    trajectory.allow_tags = True
    # trajectory.label = "trajectory"

    def get_queryset(self, request):
        if is_owner(request.user):
            return super().get_queryset(request).filter(scooter__site=request.user.owner.site)
        return super().get_queryset(request)


admin.site.register(Scooter, ScooterAdmin)
admin.site.register(Site)
admin.site.register(Ride, RideAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
