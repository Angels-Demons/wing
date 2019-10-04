from compat import get_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.db.models import SET_NULL
import django.utils.timezone

from charging.models import Tariff
# from scooter.models import Ride


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        # print(backend)
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        # print(backend)
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                # print('true')
                return True
        except PermissionDenied:
            return False
    # print("false")
    return False


class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, is_staff=False, is_admin=False, is_active=True, is_superuser=False):
        if not phone:
            raise ValueError("Users must have a phone number")
        if not password:
            raise ValueError("Users must have a password")
        # user_obj = self.model(
        #     phone=phone,
        #     is_admin=is_admin,
        #     is_staff=is_staff,
        #     is_active=is_active)

        # user_obj = self.model(phone=phone)
        # user_obj.is_admin = is_admin
        # user_obj.is_staff = is_staff
        # user_obj.is_active = is_active

        user_obj = User(
            phone=phone,
            is_admin=is_admin,
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser)
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone, password=None):
        user = self.create_user(phone,
                                password=password,
                                is_staff=True)

    def create_superuser(self, phone, password=None):
        user = self.create_user(phone,
                                password=password,
                                is_staff=True,
                                is_admin=True,
                                is_superuser=True)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.BigIntegerField(unique=True)
    is_active = models.BooleanField(blank=True, default=True)
    is_admin = models.BooleanField(blank=True, default=False)
    is_staff = models.BooleanField(blank=True, default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = UserManager()
    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = []  # python manage.py createsuperuser

    def __str__(self):
        return str(self.phone)

    def has_perm(self, perm, obj=None):
        # return True
        if self.is_active and self.is_superuser:
            return True

            # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        # return True
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        # return True
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)


def create_profile(user, tariff_id=1):
    profile = Profile(user=user)
    profile.tariff_id = tariff_id
    profile.credit = profile.tariff.initial_credit
    profile.save()
    return profile


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)
    credit = models.SmallIntegerField(default=0)
    current_ride = models.OneToOneField('scooter.Ride', null=True, blank=True, on_delete=SET_NULL, editable=True)
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(default='abc@gmail.com')
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_DEFAULT, default=1)
    app_version = models.CharField(max_length=255, default="0.0.0")
    timestamp = models.DateTimeField(auto_now_add=True, null=True, editable=False)

    def __str__(self):
        return self.name + ' ' + str(self.user.phone)
