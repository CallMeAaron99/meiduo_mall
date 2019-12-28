from django.contrib.auth.backends import ModelBackend
from django.db.models.query_utils import Q

from users.models import User


# 继承 ModelBackend 类, ModelBackend 中的 authenticate 方法会被 user 对象中的 authenticate 方法调用
class UserModelBackend(ModelBackend):

    # 重写父类方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
