from django.shortcuts import render
from django import http

from .models import ContentCategory, Content
from .utils import get_goods_channels


def index(request):
    """ 主页 """
    if request.method == 'GET':

        context = {}
        goods_channels = get_goods_channels()
        contents = {}

        # 获取所有广告类型对象
        for content_category in ContentCategory.objects.all():
            # 获取广告类型下对应的所有广告 QuerySet
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')

        context['goods_channels'] = goods_channels
        context['contents'] = contents

        return render(request, 'index.html', context)
    else:
        return http.HttpResponseForbidden()
