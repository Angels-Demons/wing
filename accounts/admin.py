from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from accounts import models
from accounts.models import Profile, Owner
from django.urls import reverse
from django.utils.html import format_html
User = get_user_model()


def is_owner(user):
    (owners_group, created) = Group.objects.get_or_create(name='owners')
    if user in owners_group.user_set.all():
        print("user is owner")
        return True
    print("user is not owner")
    return False


class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'is_active', 'is_admin', 'is_staff', 'timestamp', 'get_credit')

    def get_credit(self, obj):
        return obj.profile.credit

    get_credit.short_description = 'Credit'
    get_credit.admin_order_field = 'profile__credit'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'site', 'member_code', 'credit', '_current_ride', 'app_version', 'name', 'email', 'tariff', 'top_up', 'timestamp')
    search_fields = ('user__phone', 'app_version')
    list_filter = ['site']

    def top_up(self, obj):
        try:
            link = "/../../../zarinpal/top_up/" + str(obj.id) + "/" + str(obj.user.phone)
            # link = reverse("admin:scooter_ride_change", args=[obj.current_ride.id])  # model name has to be lowercase
            return format_html(
                """<input type="button" style="margin:2px;2px;2px;2px;" value="%s" onclick = "location.href=\'%s\'"/>"""
                % ("top up", link))
        except Exception as e:
            print(e)
            return None

    top_up.allow_tags = True
    top_up.label = "top up"

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


class OwnerAdmin(admin.ModelAdmin):
    list_display = ['id', 'site', 'user', 'name', 'phone', 'creator', 'active', 'timestamp', 'email']
    search_fields = ['name', 'phone']

    list_filter = ['active', 'site']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['phone', 'site', 'creator', 'user', 'timestamp']
        else:
            return []

    def get_exclude(self, request, obj=None):
        if obj:
            return []
        else:
            return ['creator', 'user']

    def save_model(self, request, obj, form, change):
        if obj.id:
            super().save_model(request, obj, form, change)
            obj.user.is_active = obj.active
            obj.user.save()
            return
        (brokers_group, created) = Group.objects.get_or_create(name='owners')
        if created:
            # can_fm_list = Permission.objects.get(name='can_fm_list')
            # newgroup.permissions.add(can_fm_list)
            # Modify: determine the group perms
            pass
        obj.creator = request.user
        user = models.UserManager().create_staffuser(obj.phone, str(obj.phone) + "pass")

        print("here 2")
        print(user)

        brokers_group.user_set.add(user)
        obj.user = user
        print(user)
        super().save_model(request, obj, form, change)
    # def get_queryset(self, request):
    #     if request.user.is_superuser:
    #         return super().get_queryset(request=request)
    #     return super().get_queryset(request=request).filter(user=request.user)


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Owner, OwnerAdmin)
