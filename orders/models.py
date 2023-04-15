from django.db import models
from utils.base_model import BaseModel
from user.models import UserProfile
from goods.models import SKU

# Create your models here.

STATUS_CHOICES = (
    (1, "待付款"),
    (2, "待发货"),
    (3, "待收货"),
    (4, "订单完成")
)

class OrderInfo(BaseModel):
    # 订单表
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=64, primary_key=True, verbose_name="订单编号")
    # 订单总金额、商品总数量
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单总金额")
    total_count = models.IntegerField(verbose_name="商品总数")
    # 支付方式:1代表支付宝
    pay_method = models.SmallIntegerField(default=1, verbose_name="支付方式")
    # 运费
    freight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="运费")
    # 订单状态
    status = models.SmallIntegerField(verbose_name="订单状态", choices=STATUS_CHOICES)

    # 冗余地址字段
    receiver = models.CharField(verbose_name="收件人", max_length=10)
    address = models.CharField(verbose_name="收件地址", max_length=100)
    receiver_mobile = models.CharField(verbose_name="手机号", max_length=11)
    tag = models.CharField(verbose_name="标签", max_length=10)

    class Meta:
        db_table = "orders_order_info"

class OrderGoods(BaseModel):
    """
    订单商品表
    订单表:订单商品表 ---> 1:n
    SKU表:订单商品表 ---> 1:n
    """
    order_info = models.ForeignKey(OrderInfo, on_delete=models.CASCADE)
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)

    # 数量、单价
    count = models.IntegerField(default=1, verbose_name="数量")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")

    class Meta:
        db_table = "orders_order_goods"