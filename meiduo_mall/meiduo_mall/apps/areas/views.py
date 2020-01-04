from django.shortcuts import render
from django import http

from .models import Area
from meiduo_mall.utils.response_code import RETCODE


def area(request):
    """ 省市区视图 """

    if request.method == 'GET':
        area_id = request.GET.get('area_id')

        # 省数据
        if area_id is None:
            # 所有省
            provinces = Area.objects.filter(parent=None)

            province_list = []

            # 将 QuerySet 内所有 Area 对象的值以字典类型追加到 list
            for province in provinces:
                # json.dumps 不能转换 QuerySet 或者 Area 对象
                province_list.append({
                    'id': province.id,
                    'name': province.name
                })

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok", 'province_list': province_list})

        # 市区县数据
        else:

            # 获取单个省或者市的对象
            cities_parent = Area.objects.get(id=area_id)

            # 将 id 和 name 赋值以便以后需要
            sub_data = {
                'parent_id': cities_parent.id,
                'parent_name': cities_parent.name,
                'subs': []
            }

            # 查询出所有子级数据
            for city in cities_parent.subs.all():
                sub_data['subs'].append({
                    'id': city.id,
                    'name': city.name
                })

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok", 'sub_data': sub_data})
    else:
        http.HttpResponseForbidden()

