from django.contrib import admin
from django.contrib.auth import get_user_model

from accounts.models import Profile
from django.urls import reverse
from django.utils.html import format_html
User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'is_active', 'is_admin', 'is_staff', 'timestamp', 'get_credit')

    def get_credit(self, obj):
        return obj.profile.credit

    get_credit.short_description = 'Credit'
    get_credit.admin_order_field = 'profile__credit'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'credit', '_current_ride', 'name', 'email', 'tariff', 'timestamp')

    def _current_ride(self, obj):
        try:
            link = reverse("admin:scooter_ride_change", args=[obj.current_ride.id]) #model name has to be lowercase
            return format_html(u'<a href="%s">%s</a>' % (link, obj.current_ride))
        except:
            return None
    _current_ride.allow_tags = True


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
