from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import caches
from django.conf import settings
from utils.base_view import BaseView
from goods.models import *

# Create your views here.
CARTS_CACHE = caches["carts"]

class CartsView(BaseView):
    def get(self, request, username):
        """
        查询购物车视图逻辑
        """
        user = request.myuser
        skus_list = self.get_carts_list(user.id)
        result = {
            'code': 200,
            'data': skus_list,
            'base_url': settings.PIC_URL
        }

        return JsonResponse(result)

    def post(self, request, username):
        """
        添加购物车视图逻辑
        1、获取请求体数据
        2、检查上下架状态
        3、校验数据库
        4、存入redis数据库
        5、组织数据返回
        """
        data = request.data
        sku_id = data.get("sku_id")
        count = int(data.get("count"))
        # 校验上下架状态和库存
        try:
            sku = SKU.objects.get(id=sku_id, is_launched=True)
        except Exception as e:
            print("商品已下架：", e)
            return JsonResponse({"code": 10400, "error": "该商品已下架"})
        if count > sku.stock:
            return JsonResponse({"code": 10401, "error": "库存不足"})
        # 存入redis数据库
        # 获取该用户购物车所有数据
        user = request.myuser
        cache_key = self.get_cache_key(user.id)
        carts_data = self.get_cats_all_data(cache_key)
        # 数据合并
        if not carts_data:
            # 购物车为空时
            li = [count, 1]
        else:
            li = carts_data.get(sku_id)
            if not li:
                # 购物车不为空，但没有要添加的商品
                li = [count, 1]
            else:
                # 购物车不为空，有要添加的商品
                old_count = li[0]
                new_count = count + old_count
                if new_count > sku.stock:
                    return JsonResponse({"code": 10401, "error": "库存不足"})
                li = [new_count, 1]
        # 存入数据库
        carts_data[sku_id] = li
        CARTS_CACHE.set(cache_key, carts_data)

        result = {
            'code': 200,
            'data':
            {
                'carts_count': len(carts_data)
            },
            'base_url': settings.PIC_URL
        }

        return JsonResponse(result)

    def get_cache_key(self, user_id):
        """
        功能函数：生成key
        :param user_id: 用户id
        :return:
        """
        return "carts_%s" % user_id

    def get_cats_all_data(self, cache_key):
        """
        功能函数：获取用户所有数据
        :return:
        """
        data = CARTS_CACHE.get(cache_key)
        if not data:
            return {}

        return data

    def get_carts_list(self, uid):
        """
        订单页商品列表
        """
        carts_key = self.get_cache_key(uid)
        carts_data = self.get_cats_all_data(carts_key)
        skus_query = SKU.objects.filter(id__in=carts_data.keys())
        skus_list = []
        for sku in skus_query:
            value_query = sku.sale_attr_value.all()
            sku_dict = {
                "id": sku.id,
                "name": sku.name,
                "count": carts_data[str(sku.id)][0],
                "selected": carts_data[str(sku.id)][1],
                "default_image_url": str(sku.default_image_url),
                "price": sku.price,
                "sku_sale_attr_name": [i.spu_sale_attr.name for i in value_query],
                "sku_sale_attr_val": [i.name for i in value_query]
            }
            skus_list.append(sku_dict)
        return skus_list

    def get_carts_dict(self, id):
        # 功能函数：筛选购物车中选中的商品
        carts_key = self.get_cache_key(id)
        carts_data = self.get_cats_all_data(carts_key)
        return {k:v for k,v in carts_data.items() if v[1] == 1}

    def del_carts_dict(self, id):
        # 清除购物车数据
        carts_key = self.get_cache_key(id)
        carts_data = self.get_cats_all_data(carts_key)
        for k,v in list(carts_data.items()):
            if v[1] == 1:
                del carts_data[k]
        # 将结果更新到redis
        CARTS_CACHE.set(carts_key, carts_data)
        return len(carts_data)