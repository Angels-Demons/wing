from django.contrib import admin

from zarinpal.models import Transaction, TopUp


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'authority', 'ref_id', 'amount', 'description', 'state', 'recharged', 'timestamp')


class TopUpAdmin(admin.ModelAdmin):
    list_display = ('profile', 'admin', 'amount', 'description', 'success', 'timestamp')
    readonly_fields = ('profile', 'admin', 'amount', 'description', 'success')

    # def get_readonly_fields(self, request, obj=None):
    #     if obj:
    #         return ['profile', 'admin', 'amount', 'description', 'success']
    #     else:
    #         return []


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TopUp, TopUpAdmin)
