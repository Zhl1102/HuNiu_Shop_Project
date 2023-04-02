import hashlib
import json
import time
import jwt
from django.conf import settings
from django.http import JsonResponse
from user.models import UserProfile

# Create your views here.
def tokens(request):
    """
    登录功能视图逻辑
    """
    # 获取请求体数据
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    # 从数据库中查找数据
    try:
        user = UserProfile.objects.get(username=username)
    except Exception as e:
        print("获取用户异常：", e)
        return JsonResponse({"code": 10200, "error": "用户名错误"})

    # 校验密码
    pwd_md5 = md5_token(password)
    if pwd_md5 != user.password:
        return JsonResponse({"code": 10200, "error": "密码错误"})

    # 签发token
    token = make_token(username)

    # 返回数据
    result = {
        'code': 200,
        'username': username,
        'data': {'token': token},
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