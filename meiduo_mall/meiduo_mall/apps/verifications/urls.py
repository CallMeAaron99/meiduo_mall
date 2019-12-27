from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^image_codes/(?P<uuid>[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-4[a-zA-Z0-9]{3}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12})/$', views.image_verification_code, name='image_verification_code'),
    url(r'^sms_codes/(?P<mobile>1[345789]\d{9})/$', views.sms_verification_code, name='sms_verification_code'),
]
