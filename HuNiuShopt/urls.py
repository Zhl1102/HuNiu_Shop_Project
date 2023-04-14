"""HuNiuShopt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from user import views as user_view
from dtoken import views as token_view
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # 注册路由
    path('v1/users', user_view.user),
    # 登录路由
    path('v1/tokens', token_view.tokens),
    # 激活路由
    path('v1/users/', include("user.urls")),
    # 商品模块
    path('v1/goods/', include('goods.urls')),
    # 购物车模块
    path('v1/carts/', include('carts.urls')),
]

# 配置静态路由
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
