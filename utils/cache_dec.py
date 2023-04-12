"""
    缓存装饰器
"""
from django.core.cache import caches

def cache_check(**cache_kwargs):
    """
    :param cache_kwargs: 将装饰器的参数打包成字典
    """
    def _cache_check(func):
        """
        :param func: 被装饰的方法，谁调用装饰器就传谁
        """
        def wrapper(self, request, *args, **kwargs):
            """
            构建可传参的缓存装饰器
            :param self,request,args,kwargs:被装饰的方法的参数
            """
            if "cache" in cache_kwargs:
                CACHES = caches[cache_kwargs["cache"]]
            else:
                CACHES = caches["default"]
            key = cache_kwargs["key_prefix"] + str(kwargs["sku_id"])
            # 判断redis中有没有缓存
            resp = CACHES.get(key)
            if resp:
                print("-----redis------")
                return resp
            # redis中没有就去mysql中获取，并放入缓存中
            print("-----mysql------")
            value = func(self, request, *args, **kwargs)
            exp = cache_kwargs.get("expire", 300)
            CACHES.set(key, value, exp)
            return value
        return wrapper
    return _cache_check