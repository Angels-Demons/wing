from django.contrib import admin
from django.contrib.auth.models import Group

from zarinpal.models import Transaction, TopUp


def is_owner(user):
    (owners_group, created) = Group.objects.get_or_create(name='owners')
    if user in owners_group.user_set.all():
        print("user is owner")
        return True
    print("user is not owner")
    return False


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'authority', 'ref_id', 'amount', 'description', 'state', 'recharged', 'timestamp')

    def get_queryset(self, request):
        if is_owner(request.user):
            return super().get_queryset(request).filter(user__profile__site=request.user.owner.site)
        return super().get_queryset(request)


class TopUpAdmin(admin.ModelAdmin):
    list_display = ('profile', 'admin', 'amount', 'description', 'success', 'timestamp')
    readonly_fields = ('profile', 'admin', 'amount', 'description', 'success')

    # def get_readonly_fields(self, request, obj=None):
    #     if obj:
    #         return ['profile', 'admin', 'amount', 'description', 'success']
    #     else:
    #         return []

    def get_queryset(self, request):
        if is_owner(request.user):
            return super().get_queryset(request).filter(profile__site=request.user.owner.site)
        return super().get_queryset(request)


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TopUp, TopUpAdmin)
