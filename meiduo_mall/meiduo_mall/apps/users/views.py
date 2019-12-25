from django.shortcuts import render, redirect
from django.views import View
from django import http
from users.models import User
import re


class RegisterView(View):

    @staticmethod
    def get(request):
        return render(request, 'register.html')

    @staticmethod
    def post(request):
        registration_info = request.POST

        username = registration_info.get('username')
        password = registration_info.get('password')
        password2 = registration_info.get('password2')
        mobile = registration_info.get('mobile')
        sms_code = registration_info.get('sms_code')
        allow = registration_info.get('allow')

        # 数据的 '' 和 None 判断
        if not all([username, password, password2, mobile, sms_code, allow]):
            return http.HttpResponseForbidden()

        # username 判断
        elif not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseBadRequest()

        # password 判断
        elif not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest()

        # 二次密码判断
        elif password != password2:
            return http.HttpResponseBadRequest()

        # mobile 判断
        elif not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseBadRequest()

        # TODO 短信验证

        # 协议判断
        elif allow != 'on':
            return http.HttpResponseBadRequest()

        # 录入信息
        else:
            User.objects.create_user(username=username, password=password, mobile=mobile)

        return redirect('users:login')


class LoginView(View):

    @staticmethod
    def get(request):
        return render(request, 'login.html')

