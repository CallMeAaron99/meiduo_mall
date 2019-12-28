from django.db import models

from meiduo_mall.utils.models import BaseModel


class OAuthQQUser(BaseModel):

    # 关联了 users 应用中的 User 模型类
    user = models.ForeignKey('users.User', models.CASCADE)
    openid = models.CharField(max_length=64)

    class Meta:
        db_table = 'oauth_qq_user_tb'
