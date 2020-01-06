from django.shortcuts import render
from django import http

from goods.models import GoodsChannelGroup


def index(request):
    """ 主页 """
    if request.method == 'GET':

        context = {}
        goods_channel_group = []

        for group in GoodsChannelGroup.objects.all():
            goods_channel_group.append(group)

        context['goods_channel_group'] = goods_channel_group

        return render(request, 'index.html', context)
    else:
        return http.HttpResponseForbidden()
