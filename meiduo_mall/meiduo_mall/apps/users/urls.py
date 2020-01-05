from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.is_username_exist, name='is_username_exist'),
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.is_mobile_exist, name='is_mobile_exist'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogOutView.as_view(), name='log_out'),
    url(r'^info/$', views.UserCenterView.as_view(), name='user_center'),
    url(r'^emails/$', views.SendEmailView.as_view(), name='send_email'),
    url(r'^email/verification/$', views.EmailVerificationView.as_view(), name='email_verification'),
    url(r'^addresses/$', views.AddressView.as_view(), name='address'),
    url(r'^addresses/create/$', views.AddressView.as_view(), name='address_create'),
    url(r'^addresses/(?P<address_id>\d+)/$', views.AddressView.as_view(), name='address_delete'),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.address_default, name='address_default'),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.address_title, name='address_title'),
]
