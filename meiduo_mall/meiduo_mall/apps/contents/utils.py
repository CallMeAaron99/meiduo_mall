from goods.models import GoodsChannel


def get_goods_channels():
    """ 获取频道信息 """
    goods_channels = {}

    for channel in GoodsChannel.objects.order_by('group_id', 'sequence'):

        # 新建一个字典保存频道对象 和二级类别对象
        goods_channels.setdefault(channel.group_id, {'channels': [], 'sub_cats': []})

        # 保存频道对象
        goods_channels[channel.group_id]['channels'].append(channel)

        # 每个频道对象下的二级类别对象
        for cat2 in channel.category.subs.all():
            goods_channels[channel.group_id]['sub_cats'].append(cat2)

    return goods_channels