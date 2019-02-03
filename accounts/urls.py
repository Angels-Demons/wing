from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path
from accounts.views import RegisterView, LoginView, login, sign


urlpatterns = [
    # path('login/', auth_views.login, name='login'),
    # path('logout/', auth_views.logout, name='logout'),
    # path('profile/', views.profile_view, name='profile'),
    # path('register/', RegisterView, name='register'),
    url(r'^register/$', RegisterView.as_view(), name='reg'),
    # path('login/', LoginView, name='login'),
    path('login/', login, name='login'),
    path('sign/', sign, name='sign'),
]
