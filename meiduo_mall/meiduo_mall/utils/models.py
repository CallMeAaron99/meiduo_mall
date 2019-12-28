from django.db import models


# 公用模型类
class BaseModel(models.Model):

    # insert 时会写入当前时间
    create_time = models.DateTimeField(auto_now_add=True)
    # insert or update 时会写入当前时间
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        # 该模型类是抽象类, 不会建表
        abstract = True
