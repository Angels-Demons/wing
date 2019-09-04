from django.contrib import admin

from zarinpal.models import Transaction


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'authority', 'ref_id', 'amount', 'description', 'state', 'recharged', 'timestamp')


admin.site.register(Transaction, TransactionAdmin)
