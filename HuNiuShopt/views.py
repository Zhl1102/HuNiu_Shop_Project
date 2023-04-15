import redis
from django.http import JsonResponse
from goods.models import SKU

pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
r = redis.Redis(connection_pool=pool)
def stock_view(request):
    # 测试redis 分布式锁
    with r.lock("huniushopt:stock", blocking_timeout=5) as lock:
        sku = SKU.objects.get(id=1)
        sku.stock -= 1
        sku.save()

    return JsonResponse({"code": 200})