from django.shortcuts import render
from django import http
from django_redis import get_redis_connection
from random import randint

from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.libs.yuntongxun.sms import CCP
from logging import getLogger

logger = getLogger('django')


def image_verification_code(request, uuid):
    """  图形验证码 """
    if request.method == 'GET':
        # 生成图形验证码
        name, text, img_bytes = captcha.generate_captcha()

        # 图形验证码保存到 redis
        redis_connection = get_redis_connection('verification')
        redis_connection.setex(uuid, 300, text)

        return http.HttpResponse(img_bytes, content_type='image/png')

    return http.HttpResponseForbidden()


def sms_verification_code(request, mobile):
    """短信验证码"""
    if request.method == 'GET':
        # image_verify_info = request.GET

        client_image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 数据的 '' 和 None 判断
        if all([client_image_code, uuid, mobile]) is False:
            return http.HttpResponseForbidden()

        # 获取 redis 中的图形验证码
        redis_connection = get_redis_connection('verification')
        server_image_code = redis_connection.get(uuid)

        # 图形验证码过期
        if server_image_code is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': "图形验证码已过期"})

        # 图形验证码不正确
        if server_image_code.decode().lower() != client_image_code.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': "图形验证码不正确"})

        # 生成短信验证码
        sms_code = '%06d' % randint(0, 999999)

        # 发送短信
        CCP().send_template_sms(to=mobile, datas=[sms_code, 5], temp_id=1)

        #  短信验证码保存到 redis
        redis_connection.setex('sms_code_%s' % mobile, 60 * 5, sms_code)

        # 测试短信验证码
        logger.info(sms_code)

        return http.JsonResponse({'code': RETCODE.OK})

    return http.HttpResponseForbidden()
