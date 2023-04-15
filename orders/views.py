from django.db import transaction
from django.http import JsonResponse
from django.conf import settings
from orders.models import OrderInfo, OrderGoods
from utils.base_view import BaseView
from user.models import Address
from carts.views import CartsView
from goods.models import *
import time

# Create your views here.

class AdvanceView(BaseView):

    def get(self, request, username):
        """
        确认订单页视图逻辑
        """
        # 获取地址列表
        user = request.myuser
        addresses = self.get_addresses(user.id)

        # 获取商品列表
        typ = request.GET.get("settlement_type")    # 获取url中查询字符串的数据

        if typ == "0":
            # 从购物车中去结算
            sku_list = self.get_carts_sku_list(user.id)
        else:
            # 从订单详情页去结算
            sku_id = request.GET.get("sku_id")
            buy_num = request.GET.get("buy_num")
            if not all([sku_id, buy_num]):
                return JsonResponse({"code": 10500, "error": "商品参数有误"})
            sku_list = self.get_sku_list(sku_id, buy_num)

        result = {
            "code": 200,
            "data": {
                "addresses": addresses,
                "sku_list": sku_list,
            },
            "base_url": settings.PIC_URL
        }

        return JsonResponse(result)

    def get_addresses(self, uid):
        """
        获取用户所有的地址
        """
        all_address = Address.objects.filter(user_profile_id=uid, is_active=True)
        addresses = []
        for address in all_address:
            add_dict = {
                "id": address.id,
                "name": address.receiver,
                "mobile": address.receiver_phone,
                "title": address.tag,
                "address": address.address
            }
            if address.is_default:
                addresses.insert(0, add_dict)
            else:
                addresses.append(add_dict)
        return addresses

    def get_carts_sku_list(self, uid):
        """
        获取订单确认页商品数据
        """
        # 获取到所有商品
        sku_list = CartsView().get_carts_list(uid)
        # 过滤掉没有被选中的商品

        for sku in sku_list:
            if sku["selected"] == 0:
                sku_list.remove(sku)    # 删除列表中的字典 list.remove(dict)
        return sku_list

    def get_sku_list(self, sku_id, buy_num):
        """
        立即购买商品订单确认页
        """
        try:
            sku = SKU.objects.get(id=sku_id, is_launched=True)
        except Exception as e:
            return JsonResponse({"code": 10501, "error": "该商品已下架"})
        value_query = sku.sale_attr_value.all()
        sku_list = [
            {
                "id": sku.id,
                "name": sku.name,
                "count": int(buy_num),
                "selected": 1,
                "default_image_url": str(sku.default_image_url),
                "price": sku.price,
                "sku_sale_attr_name": [i.spu_sale_attr.name for i in value_query],
                "sku_sale_attr_val": [i.name for i in value_query]
            }
        ]

        return sku_list

class OrderInfoView(BaseView):
    def post(self, request, username):
        """
        生成订单视图逻辑
        1、获取请求体数据
        2、订单表中插入数据
        3、更新库存和销量
        4、订单商品表中插入数据
        """
        data = request.data
        address_id = data.get("address_id")
        user = request.myuser
        # 生成订单编号
        order_id = time.strftime("%Y%m%d%H%M%S") + str(user.id)
        total_amount = 0
        total_count = 0
        # 地址
        try:
            add = Address.objects.get(id=address_id, user_profile=user, is_active=True)
        except Exception as e:
            return JsonResponse({"code": 10503, "error": "地址异常"})
        # 开启事务
        with transaction.atomic():
            sid = transaction.savepoint()
            # 订单表插入数据
            order = OrderInfo.objects.create(
                user_profile=user,
                order_id=order_id,
                total_amount=total_amount,
                total_count=total_count,
                pay_method=1,
                freight=1,
                status=1,
                receiver=add.receiver,
                address=add.address,
                receiver_mobile=add.receiver_phone,
                tag=add.tag,
            )
            # 更新库存和销量
            carts_dict = self.get_carts_dict(user.id)
            skus = SKU.objects.filter(id__in=carts_dict.keys())
            for sku in skus:
                while True:
                    count = carts_dict[str(sku.id)][0]
                    if count > sku.stock:
                        transaction.savepoint_rollback()
                        return JsonResponse({"code": 10504, "error": "抱歉，库存不足"})
                    # 更新库存销量
                    old_version = sku.version
                    result = SKU.objects.filter(id=sku.id).update(
                        stock=sku.stock - count,
                        sales=sku.sales + count,
                        version=old_version + 1,
                    )
                    if result == 0:
                        continue
                    else:
                        break
                # 插入订单商品表
                OrderGoods.objects.create(
                    order_info_id=order_id,
                    sku_id=sku.id,
                    price=sku.price,
                    count=count,
                )
                total_amount += sku.price * count
                total_count += count
            # 更新订单表的总价和总数量
            order.total_amount = total_amount
            order.total_count = total_count
            order.save()
            # 提交事务
            transaction.savepoint_commit(sid)
        # 清除购物车中已转化为有效订单商品数据
        carts_count = CartsView().del_carts_dict(user.id)
        data = {
            "code": 200,
            "data": {
                'saller': '虎妞商城',
                'total_amount': total_amount,
                'order_id': order_id,
                'carts_count': carts_count,
                'pay_url': ''
            }
        }
        return JsonResponse(data)

    def get_carts_dict(self, id):
        # 功能函数：筛选购物车中选中的商品
        return CartsView().get_carts_dict(id)