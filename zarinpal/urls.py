# Github.com/Rasooll
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^request/$', views.transaction_request, name='request'),
    url(r'^verify/$', views.transaction_verify, name='verify'),
]