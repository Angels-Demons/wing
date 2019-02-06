from django.contrib import admin

from charging.models import Tariff


class TariffAdmin(admin.ModelAdmin):
    list_display = ['name', 'initial_price', 'free_minutes', 'free_kilometers', 'per_minute_price',
                    'per_kilometer_price', 'initial_credit', 'minimum_credit', 'active', 'timestamp']


admin.site.register(Tariff, TariffAdmin)
