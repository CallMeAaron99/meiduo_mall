from django.shortcuts import render
from django import http
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection


def image_verification_code(request, uuid):
    name, text, img_bytes = captcha.generate_captcha()
    redis_connection = get_redis_connection('verification')
    redis_connection.setex(uuid, 300, text)
    return http.HttpResponse(img_bytes, content_type='image/png')
