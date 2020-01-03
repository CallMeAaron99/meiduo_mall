from celery_tasks import main
from meiduo_mall.libs.yuntongxun.sms import CCP


# 需要经过 celery 对象的 task 方法装饰的函数才会添加到 broker
@main.celery_object.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    CCP().send_template_sms(to=mobile, datas=[sms_code, 10], temp_id=1)
