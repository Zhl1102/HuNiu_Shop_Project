import base64
import hashlib
import json
import random
import time
import jwt
from django.http import JsonResponse
from django.conf import settings
from .models import UserProfile
from django.core.cache import caches
from django.core.mail import send_mail

CODE_CACHE = caches["default"]

# Create your views here.
def user(request):
    """
    注册功能视图逻辑
    """
    # 获取请求体数据
    data = json.loads(request.body)
    username = data.get("uname")
    password = data.get("password")
    email = data.get("email")
    phone = data.get("phone")

    # 数据库查询数据
    old_user = UserProfile.objects.filter(username=username)
    if old_user:
        return JsonResponse({"code": 10100, "error": "用户名已存在"})

    # 对密码进行加密
    pwd_md5 = md5_token(password)

    # 存储数据，考虑并发
    try:
        user = UserProfile.objects.create(username=username, password=pwd_md5, email=email, phone=phone)
    except:
        return JsonResponse({"code": 10100, "error": "用户名已存在"})

    # 激活功能
    # 为每个用户拼接一个随机数，进行base64加密
    try:
        code_num = random.randint(1000, 9999)
        code = "%s_%s" % (code_num, username)
        code = base64.urlsafe_b64encode(code.encode()).decode()

        # 存储随机数
        key = "active_email_%s", username
        CODE_CACHE.set(key, code_num, 86400*3)

        # 用户激活链接
        verify_url = "http://127.0.0.1:9999/huniushop/templates/active.html?code=" + code

        # 发送激活邮件
        send_active_mail(verify_url, email)
    except Exception as e:
        print("发送激活邮件失败", e)

    # 签发token
    token = make_token(username)

    # 组织返回数据
    result = {
        'code': 200,
        'username': username,
        'data': { 'token': token },
        'carts_count': 0
    }

    return JsonResponse(result)

def active_view(request):
    """
    邮件激活视图逻辑
    """
    pass

def md5_token(string):
    """
    密码加密
    """
    m = hashlib.md5()
    m.update(string.encode())

    return m.hexdigest()

def make_token(username, expire=86400):
    """
    将密码生成为token
    """
    payload={
        "exp": int(time.time()) + expire,
        "username": username
    }
    key = settings.JWT_TOKEN_KEY
    return jwt.encode(payload, key, algorithm="HS256")

def send_active_mail(verify_url, email):
    subject = "虎妞商城激活邮件"
    html_message = """
    尊敬的用户您好，请点击激活链接进行激活
    <a href="%s" target="_blank">点击此处</a>
    """ % verify_url
    send_mail(subject, "", "1533938229@qq.com", [email], html_message=html_message)