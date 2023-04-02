import hashlib
import json
import time
import jwt
from django.http import JsonResponse
from django.conf import settings
from .models import UserProfile

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

def md5_token(string):
    """
    密码加密
    """
    m = hashlib.md5()
    m.update(string.encode())

    return m.hexdigest()

def make_token(username, expire=86400):
    payload={
        "exp": int(time.time()) + expire,
        "username": username
    }
    key = settings.JWT_TOKEN_KEY
    return jwt.encode(payload, key, algorithm="HS256")