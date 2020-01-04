from django.db import models


# 自关联模型: 外键指向当前模型本身
class Area(models.Model):
    """省市区"""
    name = models.CharField(max_length=20)
    parent = models.ForeignKey('self', related_name='subs', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'tb_areas'
