from django.contrib import admin

from charging.models import Tariff


class TariffAdmin(admin.ModelAdmin):
    list_display = ['name', 'initial_price', 'per_minute_price', 'per_kilometer_price', 'initial_credit', 'timestamp', 'active']


admin.site.register(Tariff, TariffAdmin)
