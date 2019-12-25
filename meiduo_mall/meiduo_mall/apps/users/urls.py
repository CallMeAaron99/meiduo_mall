from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.is_username_exist, name='is_username_exist'),
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.is_mobile_exist, name='is_mobile_exist'),
]