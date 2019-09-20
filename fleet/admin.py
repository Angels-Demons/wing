from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from fleet.models import Fleet, BusinessModel


class FleetAdmin(admin.ModelAdmin):
    list_display = ('business_model', 'active', 'action', 'minimum_battery', 'payout_period_minutes', 'timestamp')

    def action(self, obj):
        try:
            link = reverse("admin:scooter_ride_change", args=[obj.current_ride.id]) #model name has to be lowercase
            return format_html(u'<a href="%s">%s</a>' % (link, "activate"))
        except:
            return None
    action.allow_tags = True


class BusinessModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'every_n_minute_charging', 'timestamp')


admin.site.register(Fleet, FleetAdmin)
admin.site.register(BusinessModel, BusinessModelAdmin)
