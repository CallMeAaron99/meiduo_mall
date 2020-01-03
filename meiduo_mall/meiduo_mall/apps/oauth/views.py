from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views import View
from django import http
from django.conf import settings
from django_redis import get_redis_connection
from QQLoginTool.QQtool import OAuthQQ


from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.re_verify import re_verification
from meiduo_mall.utils import serializer
from logging import getLogger
from users.models import User
from .models import OAuthQQUser
from users import constants

logger = getLogger('django')


def _get_oauth(request):
    next_redirect = request.GET.get('state') or request.GET.get('next') or '/'

    return OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                   client_secret=settings.QQ_CLIENT_SECRET,
                   redirect_uri=settings.QQ_REDIRECT_URI,
                   state=next_redirect)


def qq_login(request):
    """ qq 登录"""

    if request.method == 'GET':

        # 拼接 qq 授权页面的 URL
        qq_url = _get_oauth(request).get_qq_url()

        return http.JsonResponse({'login_url': qq_url, 'code': RETCODE.OK, 'errmsg': "ok"})
    else:
        return http.HttpResponseForbidden()


class OAuthCallback(View):

    def get(self, request):
        qq_code = request.GET.get('code')

        oauth_qq = _get_oauth(request)

        try:
            # 获取 access_token
            access_token = oauth_qq.get_access_token(qq_code)

            # 获取 open_id
            open_id = oauth_qq.get_open_id(access_token)

        except Exception as e:

            # 获取 token 或 id 失败
            logger.info(e)
            return render(request, 'oauth_callback.html', {'openid_errmsg', 'QQ授权失败'})

        try:

            # 查询该 id 是否有绑定用户
            oauth_qq_user = OAuthQQUser.objects.get(openid=open_id)

            # 有绑定
            user = oauth_qq_user.user

            login(request, user)

            response = redirect(oauth_qq.state)
            response.set_cookie('username', user.username, max_age=constants.REMEMBERED_PASSWORD_SESSION_EXPIRY)
            return response
        # 未绑定
        except OAuthQQUser.DoesNotExist:
            open_id = serializer.serialize(600, open_id=open_id).decode()
            return render(request, 'oauth_callback.html', {'openid': open_id})

    def post(self, request):
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code = request.POST.get('sms_code')
        openid = request.POST.get('openid')

        if all([mobile, password, sms_code, openid]) is False:
            return http.HttpResponseForbidden()

        # 手机号和密码格式判断
        if re_verification(mobile=mobile, password=password) is False:
            return http.HttpResponseForbidden()

        # 获取短信验证码
        redis_connection = get_redis_connection('verification')
        server_sms_code = redis_connection.get('sms_code_%s' % mobile)

        # 短信验证码过期
        if server_sms_code is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '短信验证码过期'})

        # 短信验证码不正确
        if sms_code != server_sms_code.decode():
            # redis_connection.delete('sms_code_%s' % mobile)
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '短信验证码不正确'})

        # 将 open id 解密并重新赋值
        openid = serializer.deserialize(openid)

        # 解密失败
        if openid is None:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'QQ授权过期'})

        try:
            # 手机号是否已注册过
            user = User.objects.get(mobile=mobile)

            # 手机号已绑定过用户
            if user.check_password(password) is False:
                return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})
        except User.DoesNotExist:
            # 手机号未绑定过用户
            # 创建新用户
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)

        # 绑定新建用户
        OAuthQQUser.objects.create(user=user, openid=openid['open_id'])

        login(request, user)
        response = redirect(request.GET.get('state') or '/')
        response.set_cookie('username', user.username, max_age=constants.REMEMBERED_PASSWORD_SESSION_EXPIRY)
        return response
