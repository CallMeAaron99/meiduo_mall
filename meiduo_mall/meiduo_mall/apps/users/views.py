from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django_redis import get_redis_connection
from django.views import View
from django import http
import re

from .models import User
from . import constants


def is_username_exist(request, username):
    """ 用户名重名 """
    if request.method == 'GET':
        return http.JsonResponse({'count': User.objects.filter(username=username).count()})

    return http.HttpResponseForbidden()


def is_mobile_exist(request, mobile):
    """ 手机号重复 """
    if request.method == 'GET':
        return http.JsonResponse({'count': User.objects.filter(mobile=mobile).count()})

    return http.HttpResponseForbidden()


def log_out(request):
    """ log out """
    if request.method == 'GET':

        # 解除登录状态
        logout(request)

        # 删除 username cookie
        response = redirect('/login/')
        response.delete_cookie('username')

        return response

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

        return redirect('/')


class LoginView(View):
    """ login """

    @staticmethod
    def get(request):
        return render(request, 'login.html')

    @staticmethod
    def post(request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        if all([username, password]) is False:
            return http.HttpResponseForbidden()

        # 用户名或手机格式不正确
        if not re.match(r'^([a-zA-Z0-9_-]{5,20}|1[345789]\d{9})$', username):
            return http.HttpResponseForbidden()

        # 密码式不正确
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden()

        # 用户名密码判断原理
        # try:
        #     user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     return http.HttpResponse("用户名或密码不正确")
        # else:
        #     if user.check_password(password) is False:
        #         return http.HttpResponse("用户名或密码不正确")

        # 多账号登录, or 查询
        # from django.db.models.query_utils import Q
        # try:
        #     user = User.objects.get(Q(username=username) | Q(mobile=username))
        # except User.DoesNotExist:
        #     return http.HttpResponse("用户名或密码不正确")
        # else:
        #     if user.check_password(password) is False:
        #         return http.HttpResponse("用户名或密码不正确")

        # 多账号登录, 正则表达式
        # try:
        #     if re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
        #         user = User.objects.get(username=username)
        #     else:
        #         user = User.objects.get(mobile=username)
        # except User.DoesNotExist:
        #     return http.HttpResponse("用户名或密码不正确")
        # else:
        #     if user.check_password(password) is False:
        #         return http.HttpResponse("用户名或密码不正确")

        # 用户名密码判断 (正确返回 user 模型类对象, 否则返回 None)
        user = authenticate(request, username=username, password=password)

        # 用户名或密码不正确
        if user is None:
            return render(request, 'login.html', {'account_errmsg': "用户名或密码不正确"})

        # 登录状态保持
        login(request, user)

        # 获取 HttpResponse 对象
        response = redirect('/')

        # 记住登录没勾选
        if remembered is None:
            # 登录状态会话结束时消失
            request.session.set_expiry(constants.DEFAULT_PASSWORD_SESSION_EXPIRY)
            response.set_cookie('username', user.username)
        else:
            request.session.set_expiry(constants.REMEMBERED_PASSWORD_SESSION_EXPIRY)
            response.set_cookie('username', user.username, max_age=constants.REMEMBERED_PASSWORD_SESSION_EXPIRY)

        return response
