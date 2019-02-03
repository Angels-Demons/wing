from rest_framework import serializers

from accounts.models import Profile
from scooter.models import Scooter, Ride


# used in My State API
class ProfileSerializer(serializers.ModelSerializer):
    is_riding = serializers.SerializerMethodField()
    ride_id = serializers.SerializerMethodField()
    timer = serializers.SerializerMethodField()

    def get_ride_id(self, profile):
        return self.ride_id

    def get_timer(self, profile):
        return self.timer

    def get_is_riding(self, profile):
        print(type(profile))
        if isinstance(profile, Profile):
            ride = Ride.objects.filter(user=profile.user, is_finished=False).first()
        else:
            ride = Ride.objects.filter(user=profile.instance.user, is_finished=False).first()
        if ride:
            self.ride_id = ride.id
            self.timer = ride.get_duration()
            return True
        else:
            self.ride_id = None
            self.timer = "0"
            return False

    class Meta:
            model = Profile
            fields = ['is_riding', 'credit', 'ride_id', 'timer']


class ScooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scooter
        fields = ['device_code', 'latitude', 'longitude', 'battery', 'status']


class ScooterAnnounceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scooter
        fields = ['latitude', 'longitude', 'battery']
