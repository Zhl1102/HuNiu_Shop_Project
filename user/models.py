import time

from django.db import models

# Create your models here.

class UserProfile(models.Model):
    username = models.CharField(max_length=11, verbose_name="用户名", unique=True)
    password = models.CharField(max_length=32)
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    is_active = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    # 修改表名
    class Meta:
        db_table = "user_user_profile"