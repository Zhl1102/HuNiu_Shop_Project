from django.urls import path
from . import views

urlpatterns = [
    path("<str:username>/advance", views.AdvanceView.as_view()),
    # 订单生成页
    path("<str:username>", views.OrderInfoView.as_view())
]