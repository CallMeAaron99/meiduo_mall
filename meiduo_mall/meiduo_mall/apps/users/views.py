from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django_redis import get_redis_connection
from django.views import View
from django import http
from django.conf import settings
from django.core.mail import send_mail
import json

from .models import User, Address
from areas.models import Area
from . import constants
from meiduo_mall.utils.views import LoginRequiredView
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.re_verify import re_verification
from meiduo_mall.utils import serializer
from celery_tasks.email.taskes import send_verify_email


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


class LogOutView(View):
    """ log out """

    def get(self, request):

        # 解除登录状态
        logout(request)

        # 删除 username cookie
        response = redirect('/login/')
        response.delete_cookie('username')

        return response


class UserCenterView(LoginRequiredView):

    def get(self, request):
        # 查看 request.user 用户是 AnonymousUser 对象还是 AbstractBaseUser 对象
        # if request.user.is_authenticated:
        #     return render(request, 'user_center_info.html')
        # else:
        #     return redirect('/login/?next=/info/')
        return render(request, 'user_center_info.html')


class RegisterView(View):
    """ register """

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
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

        # username, password, mobile  判断
        if re_verification(username=username, password=password, mobile=mobile) is False:
            return http.HttpResponseForbidden()

        # 二次密码判断
        if password != password2:
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
            redis_connection.delete('sms_code_%s' % mobile)
            return render(request, 'register.html', {'register_errmsg': "短信验证码不正确"})

        # 录入信息
        User.objects.create_user(username=username, password=password, mobile=mobile)

        return redirect('/login/')


class LoginView(View):
    """ login """

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        if all([username, password]) is False:
            return http.HttpResponseForbidden()

        # 用户名和密码格式判断
        if re_verification(username=username, password=password) is False:
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

        # 获取 HttpResponse 对象, 如果有 next 查询参数返回参数值, 否则 '/'
        response = redirect(request.GET.get('next') or '/')

        # 记住登录没勾选
        if remembered is None:
            # 登录状态会话结束时消失
            request.session.set_expiry(constants.DEFAULT_PASSWORD_SESSION_EXPIRY)
            response.set_cookie('username', user.username)
        else:
            request.session.set_expiry(constants.REMEMBERED_PASSWORD_SESSION_EXPIRY)
            response.set_cookie('username', user.username, max_age=constants.REMEMBERED_PASSWORD_SESSION_EXPIRY)

        return response


class SendEmailView(LoginRequiredView):

    def put(self, request):

        # 获取请求体数据并解码再用 json 反序列化成 dict 然后获取值
        email = json.loads(request.body.decode()).get('email')

        if email is None:
            return http.HttpResponseForbidden()

        # 邮箱格式判断
        if re_verification(email=email) is False:
            return http.HttpResponseForbidden()

        # 获取当前登录 user
        user = request.user

        # 邮箱已注册过
        if User.objects.filter(email=email).exclude(id=user.id):
            return http.JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': "该邮箱已注册过"})

        # 验证前端邮箱和当前登录用户是否一样, 避免多次执行 SQL
        if user.email != email:
            # 保存邮箱地址到当前登录 user
            user.email = email
            user.save()

        verify_query_string = serializer.serialize(900, id=user.id, email=user.email).decode()

        # celery 将发送 email 任务存放到 broker
        send_verify_email.delay(email, settings.EMAIL_VERIFICATION_URL + '?token=' + verify_query_string)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok"})


class EmailVerificationView(View):

    def get(self, request):

        token = request.GET.get('token')

        # 对 token 解密并重新赋值
        token = serializer.deserialize(token)

        # 解密失败或者查询参数中没有 token
        if token is None:
            return http.HttpResponseForbidden()

        try:
            # 获取需要邮箱激活的用户
            user = User.objects.get(id=token.get('id'), email=token.get('email'))
            # 邮箱激活
            user.email_active = True
            user.save()
            return redirect('/')
        except User.DoesNotExist:
            # 激活失败
            return http.HttpResponseGone()


class AddressView(LoginRequiredView):

    def get(self, request):

        # 获取当前登录用户 id
        user = request.user

        address = []

        # 获取用户所有关联收货地址
        for address_obj in Address.objects.filter(user_id=user.id, is_deleted=False):
            address.append({
                'id': address_obj.id,
                'title': address_obj.title,
                'receiver': address_obj.receiver,
                'province_id': address_obj.province_id,
                'province': address_obj.province.name,
                'city_id': address_obj.city_id,
                'city': address_obj.city.name,
                'district_id': address_obj.district_id,
                'district': address_obj.district.name,
                'place': address_obj.place,
                'mobile': address_obj.mobile,
                'tel': address_obj.tel,
                'email': address_obj.email
            })

        return render(request, 'user_center_site.html', {'addresses': address, 'default_address_id': user.default_address_id})

    def post(self, request):
        """ 新增地址 """
        address_info = json.loads(request.body.decode())

        title = address_info.get('title')
        receiver = address_info.get('receiver')
        province_id = address_info.get('province_id')
        city_id = address_info.get('city_id')
        district_id = address_info.get('district_id')
        place = address_info.get('place')
        mobile = address_info.get('mobile')
        tel = address_info.get('tel')
        email = address_info.get('email')

        if all([title, receiver, province_id, city_id, district_id, place, mobile]) is False:
            return http.HttpResponseForbidden()

        if re_verification(mobile=mobile) is False:
            return http.HttpResponseForbidden()

        # 如果 tel 不为 '' 做 re 判断
        if tel and re_verification(tel=tel) is False:
            return http.HttpResponseForbidden()

        # 如果 email 不为 '' 做 re 判断
        if email and re_verification(email=email) is False:
            return http.HttpResponseForbidden()

        try:
            # province = Area.objects.get(id=province_id)
            # city = Area.objects.get(id=city_id)
            # district = Area.objects.get(id=district_id)

            user = request.user

            # 保存收货地址信息
            address_obj = Address.objects.create(
                user_id=user.id,
                title=title,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 新增地址设为登录用户默认地址
            user.default_address_id = address_obj.id
            user.save()

            # 准备 json 的对象数据
            address = {
                'id': address_obj.id,
                'title': address_obj.title,
                'receiver': address_obj.receiver,
                'province_id': address_obj.province_id,
                'province': address_obj.province.name,
                'city_id': address_obj.city_id,
                'city': address_obj.city.name,
                'district_id': address_obj.district_id,
                'district': address_obj.district.name,
                'place': address_obj.place,
                'mobile': address_obj.mobile,
                'tel': address_obj.tel,
                'email': address_obj.email
            }

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok", 'address': address})
        except Area.DoesNotExist:
            # 省市区数据绑定失败
            return http.HttpResponseForbidden()

    def put(self, request):
        """ 修改地址 """
        pass

    def delete(self, request, address_id):
        """ 删除地址 """

        user = request.user

        try:
            # 获取当前登录用户要删除的 address 模型对象
            address = Address.objects.get(user_id=user.id, id=address_id)
            # 逻辑删除
            address.is_deleted = True
            address.save()

            # 如果删除的是默认地址
            if user.default_address_id == int(address_id):
                # 将最近一次修改过的 address 对象拿到 (QuerySet 可以用下标拿到相应的对象)
                # 将 address 对象的 id 值给 user 中默认地址的 id
                user.default_address_id = Address.objects.filter(user_id=user.id, is_deleted=False)[0].id
                user.save()

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok"})

        except Address.DoesNotExist:
            # 前端数据异常
            return http.HttpResponseForbidden()
