from django.shortcuts import render
from django import http
from django.core.cache import cache

from .models import Area
from meiduo_mall.utils.response_code import RETCODE


def area(request):
    """ 省市区视图 """

    if request.method == 'GET':
        area_id = request.GET.get('area_id')

        # 获取保存省市区数据的 redis 客户端对象
        # redis_connection = get_redis_connection('area')

        # 省数据
        if area_id is None:

            # 从 redis 中获取省数据
            # province_list2 = pickle.loads(redis_connection.get('province_list'))
            province_list = cache.get('province_list')

            # redis 中没有省数据
            if province_list is None:
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

                # 将省数据缓存到 redis
                # redis_connection.setex('province_list', 3600, pickle.dumps(province_list))
                cache.set('province_list', province_list, 3600)

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok", 'province_list': province_list})

        # 市区县数据
        else:

            # 从 redis 中获取市区数据
            sub_data = cache.get('sub_data')

            # redis 中没有市区数据
            if sub_data is None:

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

                # 将市区数据缓存到 redis
                cache.set('sub_data', sub_data, 3600)

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok", 'sub_data': sub_data})
    else:
        http.HttpResponseForbidden()

