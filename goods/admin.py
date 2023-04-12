from django.contrib import admin
from .models import *
from django.core.cache import caches
from utils.cache_dec import cache_check

GOODS_INDEX_CACHE = caches["goods_index"]
GOODS_DETAIL_CACHE = caches["goods_detail"]
# Register your models here.
# 注册模型类
@admin.register(SKU)
class SKUAdmin(admin.ModelAdmin):
    # 重写save_model方法
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 清除商品首页缓存
        GOODS_INDEX_CACHE.clear()
        # 清除商品详情页缓存
        key = "gd%s" % obj.id
        GOODS_DETAIL_CACHE.delete(key)

        print("更新mysql数据时，清除缓存")

    # 重写delete_model方法
    def delete_model(self, request, obj):
        super().save_model(request, obj)
        # 清除商品首页缓存
        GOODS_INDEX_CACHE.clear()
        # 清除商品详情页缓存
        key = "gd%s" % obj.id
        GOODS_DETAIL_CACHE.delete(key)

        print("更新mysql数据时，清除缓存")