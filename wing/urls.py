"""wing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from background_task.models import Task
from django.contrib import admin
from django.urls import path, include

from scooter.models import check_for_unattached_scooters

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('v/', include('api.urls')),
    path('scooter/', include('scooter.urls')),
    path('zarinpal/', include('zarinpal.urls')),
    # path('websocket/', include('example.urls')),
    path('admin/log_viewer/', include('log_viewer.urls')),
]

try:
    tasks = Task.objects.filter(task_name="scooter.models.check_for_unattached_scooters")
    tasks.delete()
    check_for_unattached_scooters(0)
except:
    pass

