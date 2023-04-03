from django.urls import path
from . import views

urlspattern = [
    # 分布式激活路由
    path('activation/', views.active_view),
]