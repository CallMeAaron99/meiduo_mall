from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings


def serialize(expires_in, **kwargs):
    serializer = Serializer(secret_key=settings.SECRET_KEY, expires_in=expires_in)
    # 将对象加密并返回一个 bytes 类型
    return serializer.dumps(kwargs)


def deserialize(data):
    serializer = Serializer(secret_key=settings.SECRET_KEY)
    try:
        # 将数据解密并返回
        return serializer.loads(data)
    except BadData:
        # 解密失败
        return None


if __name__ == '__main__':
    pass
