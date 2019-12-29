from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^qq/authorization/$', views.qq_login, name='qq_login'),
    url(r'^oauth_callback$', views.oauth_callback, name='oauth_callback'),

]
