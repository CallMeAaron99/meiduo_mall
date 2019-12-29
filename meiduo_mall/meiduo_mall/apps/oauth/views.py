from django.shortcuts import render, redirect
from django import http
from QQLoginTool.QQtool import OAuthQQ

from meiduo_mall.utils.response_code import RETCODE, err_msg


def get_oauth(request):
    next_redirect = request.GET.get('next') or '/'

    return OAuthQQ(client_id='101568493',
                   client_secret='e85ad1fa847b5b79d07e40f8f876b211',
                   redirect_uri='http://www.meiduo.site:8000/oauth_callback',
                   state=next_redirect)


def qq_login(request):
    if request.method == 'GET':

        # 拼接 qq 授权页面的 URL
        qq_url = get_oauth(request).get_qq_url()

        return http.JsonResponse({'login_url': qq_url, 'code': RETCODE.OK, 'errmsg': err_msg.get(RETCODE.OK)})
    else:
        return http.HttpResponseForbidden()


def oauth_callback(request):
    if request.method == 'GET':

        qq_code = request.GET.get('code')

        oauth_qq = get_oauth(request)

        # 获取 access_token
        access_token = oauth_qq.get_access_token(qq_code)

        # 获取 open_id
        open_id = oauth_qq.get_open_id(access_token)

        return redirect('/register/?next=%s' % oauth_qq.state)
    else:
        return http.HttpResponseForbidden()
