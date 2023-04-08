import time

from django.db import models
from utils.base_model import BaseModel

# Create your models here.

class UserProfile(BaseModel):
    username = models.CharField(max_length=11, verbose_name="用户名", unique=True)
    password = models.CharField(max_length=32)
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    is_active = models.BooleanField(default=False)

    # 修改表名
    class Meta:
        db_table = "user_user_profile"

class Address(BaseModel):
    # 外键【用户表:地址表 1:n】
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    receiver = models.CharField(max_length=10, verbose_name="收件人")
    address = models.CharField(max_length=100, verbose_name="地址")
    postcode = models.CharField(max_length=6, verbose_name="邮编")
    receiver_phone = models.CharField(max_length=11, verbose_name="手机号")
    tag = models.CharField(max_length=11, verbose_name="标签")
    is_default = models.BooleanField(default=False, verbose_name="是否为默认地址")
    # 伪删除
    is_active = models.BooleanField(default=True, verbose_name="是否删除")

    # 修改表名
    class Meta:
        db_table = "user_address"

class WeiBoProfile(BaseModel):
    # 存放微博用户表
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=True)
    wuid = models.CharField(max_length=10, verbose_name="微博用户id", db_index=True, unique=True)
    access_token = models.CharField(max_length=32, verbose_name="微博的授权令牌")

    class Meta:
        db_table = "user_weibo_profile"
