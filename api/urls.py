from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path
from api.views import *


urlpatterns = [
    # path('', boosh, name='login'),
    # path('v98/', boosh2, name='login'),
    # path('boosham/', boosham, name='login'),
    path('val/', val, name='login'),
    # path('sign/', sign, name='sign'),
]
