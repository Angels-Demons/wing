from rest_framework import serializers

from accounts.models import Profile
from scooter.models import Scooter, Ride, Announcement, Site


# used in My State API
class ProfileSerializer(serializers.ModelSerializer):
    is_riding = serializers.SerializerMethodField()
    ride_is_verified = serializers.SerializerMethodField()
    ride_id = serializers.SerializerMethodField()
    timer = serializers.SerializerMethodField()
    battery = serializers.SerializerMethodField()
    site = serializers.SerializerMethodField()

    def get_site(self, profile):
        if profile.site is not None:
            return profile.site.name

    def get_battery(self, profile):
        return self.battery

    def get_ride_id(self, profile):
        return self.ride_id

    def get_timer(self, profile):
        return self.timer

    def get_is_riding(self, profile):
        # print(type(profile))
        # modify
        # if isinstance(profile, Profile):
        #     print("is instance of profile")
        #     ride = Ride.objects.filter(user=profile.user, is_finished=False).first()
        # else:
        #     print("is not instance of profile")
        #     ride = Ride.objects.filter(user=profile.instance.user, is_finished=False).first()

        # ride = Ride.objects.filter(user=profile.user, is_finished=False).first()
        ride = profile.current_ride
        if ride:
            self.ride_id = ride.id
            self.timer = ride.get_duration_in_seconds()
            self.battery = ride.scooter.battery
            return True
        else:
            self.ride_id = None
            self.timer = "0"
            self.battery = 0
            return False

    def get_ride_is_verified(self, profile):
        # if isinstance(profile, Profile):
        #     print("is instance of profile")
        #     ride = get_object_or_404(Ride, user=profile.user, is_finished=False)
        # else:
        #     print("is not instance of profile")
        #     ride = get_object_or_404(Ride, user=profile.instance.user, is_finished=False)
        ride = Ride.objects.filter(user=profile.user, is_finished=False).first()
        # modify: modified! used to be if ride.scooter.device_status == 2

        if ride and ride.start_acknowledge_time is not None:
            return True
        else:
            return False

    class Meta:
            model = Profile
            fields = ['is_riding', 'ride_is_verified', 'credit', 'ride_id', 'timer', 'battery',
                      'site', 'member_code', 'name']


class ScooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scooter
        fields = ['device_code', 'latitude', 'longitude', 'battery', 'status', 'type']


class ScooterAnnounceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scooter
        fields = ['latitude', 'longitude', 'battery', 'device_status', 'gps_board_connected', 'gps_valid', 'alerted']


class ScooterAnnounceSerializerFakeLocation(serializers.ModelSerializer):
    class Meta:
        model = Scooter
        fields = ['battery', 'device_status', 'gps_board_connected', 'gps_valid', 'alerted']


class AnnounceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Announcement
        fields = [
            'scooter', 'ride',
            'time', 'latitude', 'longitude', 'battery', 'device_status',
            'gps_board_connected', 'gps_valid', 'ack_start', 'ack_end', 'alerted'
        ]


class SiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Site
        fields = ['id', 'name']
