from django.contrib import admin
from django.contrib.auth import get_user_model

from accounts.models import Profile

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'is_active', 'is_admin', 'is_staff', 'timestamp', 'get_credit')

    def get_credit(self, obj):
        return obj.profile.credit

    get_credit.short_description = 'Credit'
    get_credit.admin_order_field = 'profile__credit'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'credit', 'name', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
