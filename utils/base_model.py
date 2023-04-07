"""
    抽象模型类：为普通模型类补充字段
"""
from django.db import models

class BaseModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        # 声明此类为抽象模型类
        abstract = True