from django.http import JsonResponse
from django.conf import settings
from django.views import View
from goods.models import *
from utils.cache_dec import cache_check

# Create your views here.
class GoodsIndexView(View):
    def get(self, request):
        """
        首页展示视图逻辑
        """
        data = []
        # 获取商品类表中的所有种类
        all_catalog = Catalog.objects.all()
        # 循环遍历出每个种类，并加到字典中
        for cata in all_catalog:
            cata_dict = {}
            cata_dict["catalog_id"] = cata.id
            cata_dict["catalog_name"] = cata.name
            cata_dict["sku"] = []

            # 由于分类表中没有sku字段，去其他表中获取
            spu_ids = SPU.objects.filter(catalog=cata).values("id")
            sku_list = SKU.objects.filter(spu__in=spu_ids)[:3]
            for one_sku in sku_list:
                d = {
                    "skuid": one_sku.id,
                    "caption": one_sku.caption,
                    "name": one_sku.name,
                    "price": one_sku.price,
                    "image": str(one_sku.default_image_url)
                }
                cata_dict["sku"].append(d)
            data.append(cata_dict)
        result = {
            "code": 200,
            "data": data,
            "base_url": settings.PIC_URL,
        }
        return JsonResponse(result)

class GoodsDetailView(View):
    @cache_check(key_prefix="gd", key_param="sku_id", cache="goods_detail", expire=60)
    def get(self, request, sku_id):
        """
        详情页展示视图
        """
        try:
            sku_item = SKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({"code": 10300, "error": "没有此商品"})

        data = {}
        # catalog相关数据
        sku_catalog = sku_item.spu.catalog
        data["catalog_id"] = sku_catalog.id
        data["catalog_name"] = sku_catalog.name
        # sku相关数据
        data["name"] = sku_item.name
        data["caption"] = sku_item.caption
        data["price"] = sku_item.price
        data["image"] = str(sku_item.default_image_url)
        data["spu"] = sku_item.spu_id
        # 详情页图片
        img_query = SKUImage.objects.filter(sku=sku_item.id)
        if img_query:
            data["detail_image"] = img_query[0]
        else:
            data["detail_image"] = ""
        # 销售属性值
        attr_value_query = sku_item.sale_attr_value.all()
        data["sku_sale_attr_val_id"] = [i.id for i in attr_value_query]
        data["sku_sale_attr_val_names"] = [i.name for i in attr_value_query]
        # 销售属性名
        attr_name_value = SPUSaleAttr.objects.filter(spu=sku_item.spu)
        data["sku_sale_attr_id"] = [i.id for i in attr_name_value]
        data["sku_sale_attr_names"] = [i.name for i in attr_name_value]
        # 两者的关系
        sku_all_sale_attr_vals_id = {}
        sku_all_sale_attr_vals_name = {}
        for id in data["sku_sale_attr_id"]:
            sku_all_sale_attr_vals_id[id] = []
            sku_all_sale_attr_vals_name[id] = []
            item_query = SaleAttrValue.objects.filter(spu_sale_attr=id)
            for item in item_query:
                sku_all_sale_attr_vals_id[id].append(item.id)
                sku_all_sale_attr_vals_name[id].append(item.name)
        data["sku_all_sale_attr_vals_id"] = sku_all_sale_attr_vals_id
        data["sku_all_sale_attr_vals_name"] = sku_all_sale_attr_vals_name
        # 规格属性
        spec = {}
        spec_query = SKUSpecValue.objects.filter(sku=sku_item)
        for spec_obj in spec_query:
            key = spec_obj.spu_spec.name
            value = spec_obj.name
            spec[key] = value
        data["spec"] = spec

        result = {
            "code": 200,
            "data": data,
            "base_url": settings.PIC_URL,
        }
        return JsonResponse(result)