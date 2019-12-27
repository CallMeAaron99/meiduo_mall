from django.shortcuts import render, redirect
from django.views import View
from django import http
from django_redis import get_redis_connection
import re

from .models import User


def is_username_exist(request, username):
    if request.method == 'GET':
        return http.JsonResponse({'count': User.objects.filter(username=username).count()})
    return http.HttpResponseForbidden()


def is_mobile_exist(request, mobile):
    if request.method == 'GET':
        return http.JsonResponse({'count': User.objects.filter(mobile=mobile).count()})
    return http.HttpResponseForbidden()


class RegisterView(View):
    """ register """

    @staticmethod
    def get(request):
        return render(request, 'register.html')

    @staticmethod
    def post(request):
        # registration_info = request.POST

        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        # 数据的 '' 和 None 判断
        if not all([username, password, password2, mobile, sms_code, allow]):
            return http.HttpResponseForbidden()

        # username 判断
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden()

        # password 判断
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden()

        # 二次密码判断
        if password != password2:
            return http.HttpResponseForbidden()

        # mobile 判断
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden()

        # 协议判断
        if allow != 'on':
            return http.HttpResponseForbidden()

        # 获取 redis 短信验证码
        redis_connection = get_redis_connection('verification')
        server_sms_code = redis_connection.get('sms_code_%s' % mobile)

        # 短信验证码过期
        if server_sms_code is None:
            return render(request, 'register.html', {'register_errmsg': "短信验证码过期"})

        # 短信验证码不正确
        if sms_code != server_sms_code.decode():
            return render(request, 'register.html', {'register_errmsg': "短信验证码不正确"})

        # 录入信息
        User.objects.create_user(username=username, password=password, mobile=mobile)

        return redirect('users:login')


class LoginView(View):
    """ login """

    @staticmethod
    def get(request):
        return render(request, 'login.html')

