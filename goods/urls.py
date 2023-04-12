from django.urls import path
from goods import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    # 主页展示
    path("index", cache_page(300, cache="goods_index")(views.GoodsIndexView.as_view())),
    # 详情页路由
    path("detail/<int:sku_id>", views.GoodsDetailView.as_view()),
]