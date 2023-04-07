import os
from celery import Celery
from django.conf import settings

# 为celery设置环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HuNiuShopt.settings")

# 创建应用
app = Celery("HuNiuShopt", broker='redis://@127.0.0.1:6379/1')

# 设置app自动加载任务
app.autodiscover_tasks(settings.INSTALLED_APPS)