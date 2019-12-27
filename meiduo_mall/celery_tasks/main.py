from celery import Celery
import os

# 加载 django 配置文件
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.development")

# 创建 Celery 对象
celery_object = Celery('meiduo')

# 加载 celery 配置
celery_object.config_from_object('celery_tasks.config')

# 注册 celery 任务
celery_object.autodiscover_tasks(['celery_tasks.sms'])
