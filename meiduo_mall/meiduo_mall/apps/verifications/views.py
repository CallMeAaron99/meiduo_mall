from django_redis import get_redis_connection
from random import randint
from django import http


from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from celery_tasks.sms.tasks import send_sms_code
from logging import getLogger
from . import constants


logger = getLogger('django')


def image_verification_code(request, uuid):
    """  图形验证码 """
    if request.method == 'GET':
        # 生成图形验证码
        name, text, img_bytes = captcha.generate_captcha()

        # 图形验证码保存到 redis
        redis_connection = get_redis_connection('verification')
        redis_connection.setex(uuid, constants.IMAGE_CODE_EXPIRY, text)

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

        # 连接 redis 客户端
        redis_connection = get_redis_connection('verification')

        # 获取 redis 中的短信验证码发送标识
        if redis_connection.get('sms_code_flag_%s' % mobile):
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': "验证码请求过于频繁"})

        # 获取 redis 中的图形验证码
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
        # CCP().send_template_sms(to=mobile, datas=[sms_code, 2], temp_id=1)

        # celery 将发送短信的任务存放到 broker
        send_sms_code.delay(mobile, sms_code)

        # redis 管道对象 (用于一次向数据库发送多个请求)
        pl = redis_connection.pipeline()

        # 短信验证码保存到 redis
        pl.setex('sms_code_%s' % mobile, constants.SMS_CODE_EXPIRY, sms_code)

        # 短信验证码发送标识创建 (防止连续发送短信验证码)
        pl.setex('sms_code_flag_%s' % mobile, constants.SMS_CODE_FLAG_EXPIRY, 1)

        # 执行管道中的 non-sql
        pl.execute()

        # 测试短信验证码
        logger.info(sms_code)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok"})

    return http.HttpResponseForbidden()
