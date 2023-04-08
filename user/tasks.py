from django.conf import settings
from HuNiuShopt.celery import app
from django.core.mail import send_mail
from utils.sms import YunTongXunAPI

@app.task
def async_send_active_mail(verify_url, email):
    subject = "虎妞商城激活邮件"
    html_message = """
    尊敬的用户您好，请点击激活链接进行激活
    <a href="%s" target="_blank">点击此处</a>
    """ % verify_url
    send_mail(subject, "", "1533938229@qq.com", [email], html_message=html_message)

@app.task
def async_send_message(phone, code):
    sms_api = YunTongXunAPI(**settings.SMS_CONFIG)
    sms_api.run(phone, code)