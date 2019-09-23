# Github.com/Rasooll
from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    url(r'^request/$', views.transaction_request, name='request'),
    url(r'^verify/$', views.transaction_verify, name='verify'),
    url(r'^top_up/(?P<profile_id>\d+)/(?P<phone>\d+)', views.top_up, name='top_up'),
    url(r'^top_up_exe/', views.top_up_exe, name='top_up_exe'),
    # path('end_ride/', views.top_up, name='top_up'),
]
