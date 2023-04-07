"""
    权限校验的基类
"""
import json
import jwt
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from user.models import UserProfile


class BaseView(View):
    def dispatch(self, request, *args, **kwargs):
        # token校验
        # 获取token
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return JsonResponse({"code": 403, "error": "one:请登录"})

        key = settings.JWT_TOKEN_KEY
        try:
            payload = jwt.decode(token, key, algorithms="HS256")
        except Exception as e:
            return JsonResponse({"code": 403, "error": "two:请登录"})

        username = payload.get("username")
        try:
            user = UserProfile.objects.get(username=username)
        except Exception as e:
            return JsonResponse({"code": 403, "error": "three:请登录"})

        # 给所有调用过装饰器的方法的request都增加了一个myuser方法
        request.myuser = user
        data_loads = None
        if request.body:
            data_loads = json.loads(request.body)

        request.data = data_loads

        return super().dispatch(request, *args, **kwargs)