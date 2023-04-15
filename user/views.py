import base64
import hashlib
import json
import random
import time
import jwt
import requests
from django.http import JsonResponse
from django.conf import settings
from .models import *
from django.core.cache import caches
from django.core.mail import send_mail
from django.db import transaction
from .tasks import *
from django.views import View
from utils.logging_dec import logging_check
from utils.base_view import BaseView
from utils.weibo_api import OauthAPI

CODE_CACHE = caches["default"]
SMS_CACHE = caches["sms"]

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
    # 短信验证码
    # verify = data.get("verify")
    #
    # expire_key = "sms_expire_%s" % phone
    # redis_code = SMS_CACHE.get(expire_key)
    #
    # if not redis_code:
    #     return JsonResponse({"code": 10109, "error": {"message": "验证码过期，请重新获取验证码"}})
    # if verify != str(redis_code):
    #     return JsonResponse({"code": 10110, "error": {"message": "验证码错误"}})

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
        return JsonResponse({"code": 10101, "error": "用户名或密码错误"})

    # 激活功能
    # 为每个用户拼接一个随机数，进行base64加密
    try:
        verify_url = get_verify_url(username)

        # 异步发送激活邮件
        async_send_active_mail.delay(verify_url, email)
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
    1、先获取查询字符串
    2、校验code
    3、激活用户
    4、清除redis中对应数据的缓存
    """
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"code": 10102, "error": "code不存在"})
    code_str = base64.urlsafe_b64decode(code.encode()).decode()
    code_num, username = code_str.split("_")

    # 与redis缓存中的code做比较
    key = "active_email_%s" % username
    redis_num = CODE_CACHE.get(key)
    print(redis_num)
    print(code_num)
    if redis_num != code_num:
        return JsonResponse({"code": 10103, "error": "激活链接有误"})

    # ORM更新
    try:
        user = UserProfile.objects.get(username=username, is_active=False)  # 查询
    except Exception as e:
        print("激活失败：", e)
        return JsonResponse({"code": 10104, "error": "用户名有误"})
    user.is_active = True   # 修改
    user.save() # 保存

    # 清除缓存
    CODE_CACHE.delete(key)

    result = {
        'code': 200,
        'data': '激活成功'
    }

    return JsonResponse(result)

class AddressView(View):

    @logging_check
    def get(self, request, username):
        """
        获取收件地址的视图
        """
        user = request.myuser
        all_address = Address.objects.filter(user_profile=user, is_active=True)

        address_list = []
        for address in all_address:
            address_dict = {
                'id':address.id,
                'address':address.address,
                'receiver':address.receiver,
                'receiver_mobile':address.receiver_phone,
                'tag':address.tag,
                'postcode':address.postcode,
                'is_default':address.is_default,
            }
            address_list.append(address_dict)
        return JsonResponse({"code": 200, "addresslist": address_list})

    @logging_check
    def post(self, request, username):
        """
        新增地址视图逻辑
        1、获取请求体数据
        2、存入数据表（如果这个地址为用户的第一个地址设为默认）
        3、返回数据
        """
        # 获取请求体数据
        data = request.data
        receiver = data.get("receiver")
        address = data.get("address")
        postcode = data.get("postcode")
        receiver_phone = data.get("receiver_phone")
        tag = data.get("tag")

        user = request.myuser

        # 获取该用户的地址列
        old_address = Address.objects.filter(user_profile=user, is_active=True)
        if not old_address:
            is_default = True
        else:
            is_default = False

        # 存入数据
        Address.objects.create(user_profile=user,
                               receiver=receiver,
                               address=address,
                               postcode=postcode,
                               receiver_phone=receiver_phone,
                               tag=tag,
                               is_default=is_default,
                               )

        return JsonResponse({"code": 200, "data": "新增地址成功！"})

    @logging_check
    def put(self, request, username, id):
        """
        修改地址的视图逻辑
        1、获取请求体数据
        2、查询需要修改的地址的[id user]
        3、修改数据
        4、组织返回数据
        :param id: 地址的id
        """
        data = request.data
        tag = data.get("tag")
        receiver_phone = data.get("receiver_phone")
        receiver = data.get("receiver")
        address = data.get("address")

        user = request.myuser
        address_query = Address.objects.get(user_profile=user, id=id)
        if not address_query:
            return JsonResponse({"code": 10107, "error": "用户没有该地址"})

        address_query.tag = tag
        address_query.receiver_phone = receiver_phone
        address_query.receiver = receiver
        address_query.address = address
        address_query.save()

        return JsonResponse({"code": 200, "data": "修改成功"})

    @logging_check
    def delete(self, request, username, id):
        """
        删除地址的视图逻辑
        1、获取请求体数据
        2、查询需要修改的地址的[id user]
        3、修改数据
        4、组织返回数据
        :param id: 地址的id
        """
        data = request.data
        address_id = data.get("id")

        user = request.myuser
        try:
            address = Address.objects.get(user_profile=user, id=address_id, is_active=True)
        except Exception as e:
            print("删除失败：", e)
            return JsonResponse({"code": 10105, "error": "地址不存在"})

        if address.is_default:
            return JsonResponse({"code": 10106, "error": "默认地址不允许删除"})

        address.is_active = False
        address.save()

        return JsonResponse({"code": 200, "data": "删除成功"})

class DefaultAddressView(BaseView):
    # @logging_check
    # 装饰器和基类可以二选一
    def post(self, request, username):
        """
        设置默认视图逻辑
        1、获取请求体数据
        2、查询、修改、保存
        3、组织返回数据
        """
        data = request.data
        user = request.myuser
        uid = data.get("id")

        # 开启事务
        with transaction.atomic():
            # 创建存储点
            sid = transaction.savepoint()
            try:
                # 将原来的地址设置为非默认
                old_default = Address.objects.get(user_profile=user, is_default=True, is_active=True)
                old_default.is_default = False
                old_default.save()
                # 将现在的地址设置为默认地址
                new_default = Address.objects.get(user_profile=user, id=uid, is_active=True)
                new_default.is_default = True
                new_default.save()
            except Exception as e:
                print("默认地址设置失败：", e)
                transaction.savepoint_rollback(sid)
                return JsonResponse({"code": 10107, "error": "设置默认地址失败"})

            transaction.savepoint_commit(sid)

        return JsonResponse({"code": 200, "data": "设为默认地址成功！"})

def sms_view(request):
    """
    短信验证视图逻辑
    """
    data = json.loads(request.body)
    phone = data.get("phone")

    code = random.randint(100000, 999999)

    # 调用短信接口，判断验证码是否存在
    key = "sms_%s" % phone
    redis_code = SMS_CACHE.get(key)
    if redis_code:
        return JsonResponse({"code": 10108, "error": {"message": "三分钟内只能发送一次短信验证码"}})
    # 使用celery异步发送短信
    async_send_message.delay(phone, code)
    # 控制验证码发送频率
    SMS_CACHE.set(key, code, 180)
    # 控制验证码有效期
    expire_key = "sms_expire_%s" % phone
    SMS_CACHE.set(expire_key, code, 600)

    return JsonResponse({"code": 200, "data": "发送成功"})

class OauthUrlView(View):
    def get(self, request):
        """
        授权登录视图逻辑，获取微博登录code
        """
        weibo_api = OauthAPI(**settings.WEIBO_CONFIG)
        oauth_url = weibo_api.get_grant_url()

        # 获取到重定向的url，返回给前端
        return JsonResponse({"code": 200, "oauth_url": oauth_url})

class OauthView(View):
    def get(self, request):
        """
        获取access_token逻辑
        """
        code = request.GET.get("code")
        if not code:
            return JsonResponse({"code": 10111, "error": "没有授权码"})

        post_url = "https://api.weibo.com/oauth2/access_token"
        post_data = {
            "client_id": settings.WEIBO_CONFIG.get("app_key"),
            "client_secret": settings.WEIBO_CONFIG.get("app_secret"),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.WEIBO_CONFIG.get("redirect_uri"),
        }

        access_html = requests.post(url=post_url, data=post_data).json()

        # 绑定注册流程
        wuid = access_html.get("uid")
        access_token = access_html.get("access_token")

        try:
            weibo_user = WeiBoProfile.objects.get(wuid=wuid)
        except Exception as e:
            print("获取微博用户失败：", e)
            # 第一次扫码登录，添加数据
            WeiBoProfile.objects.create(wuid=wuid, access_token=access_token)
            return JsonResponse({"code": 201, "uid": wuid})

        user = weibo_user.user_profile
        if user:
            return JsonResponse({"code": 200, "username": user.username, "token": make_token(user.username)})

        return JsonResponse({"code": 201, "uid": wuid})

        # return JsonResponse({"code": 200})

    def post(self, request):
        """
        绑定注册视图逻辑
        """
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        phone = data.get("phone")
        wuid = data.get("uid")

        pwd_md5 = md5_token(password)

        try:
            user = UserProfile.objects.get(username=username)
            return JsonResponse({"code": 10112, "error": "用户名已存在"})
        except Exception as e:
            with transaction.atomic():
                sid = transaction.savepoint()
                try:
                    # 添加用户
                    user = UserProfile.objects.create(username=username, password=pwd_md5, email=email, phone=phone)
                    # 更新外键
                    weibo_user = WeiBoProfile.objects.get(wuid=wuid)
                    weibo_user.user_profile = user
                    user.save()
                    weibo_user.save()
                except Exception as e:
                    print("用户添加/更新失败：", e)
                    transaction.savepoint_rollback(sid)
                    return JsonResponse({"code": 10113, "error": "绑定注册失败"})
                transaction.savepoint_commit(sid)

            # 注册成功发送激活邮件
            verify_url = get_verify_url(username)
            async_send_active_mail(verify_url, email)

            token = make_token(username)

            return JsonResponse({"code": 200, "username": username, "token": token})

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

def get_verify_url(username):
    # 发送激活邮件
    code_num = "%d" % random.randint(1000, 9999)
    code = "%s_%s" % (code_num, username)
    code = base64.urlsafe_b64encode(code.encode()).decode()

    # 存储随机数
    key = "active_email_%s" % username
    CODE_CACHE.set(key, code_num, 86400 * 3)

    # 用户激活链接
    verify_url = "http://127.0.0.1:9999/huniushop/templates/active.html?code=" + code

    return verify_url

# def send_active_mail(verify_url, email):
#     subject = "虎妞商城激活邮件"
#     html_message = """
#     尊敬的用户您好，请点击激活链接进行激活
#     <a href="%s" target="_blank">点击此处</a>
#     """ % verify_url
#     send_mail(subject, "", "1533938229@qq.com", [email], html_message=html_message)