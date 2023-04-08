from django.urls import path
from . import views

urlpatterns = [
    # 分布式激活路由
    path('activation/', views.active_view),
    # 地址管理[新增、查询]
    path('<str:username>/address', views.AddressView.as_view()),
    # 地址管理[修改、删除]
    path('<str:username>/address/<int:id>', views.AddressView.as_view()),
    # 设置默认地址
    path('<str:username>/address/default', views.DefaultAddressView.as_view()),
    # 注册短信验证
    path('sms/code', views.sms_view),
]