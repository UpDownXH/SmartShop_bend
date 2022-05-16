import json
from decimal import Decimal

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from redis import Redis

from apps.goods.models import SKU
from utils.views import LoginRequiredJSONMixin


class CartsView(LoginRequiredJSONMixin, View):
    def post(self, request):
        #  - 接收参数 校验
        data_dict = json.loads(request.body)
        sku_id = data_dict.get("sku_id")
        count = data_dict.get("count")
        selected = data_dict.get("selected", True)  # 如果没有传 默认是选中

        # 判断参数是否齐全
        if not all([sku_id, count]):
            return HttpResponseBadRequest('缺少必传参数')
        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseBadRequest('商品不存在')
        # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return HttpResponseBadRequest('参数count有误')
        # 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return HttpResponseBadRequest('参数selected有误')

        user = request.user

        # - 添加数据到redis
        redis_conn: Redis = get_redis_connection('carts')
        pl = redis_conn.pipeline()
        # hincrby 这里是对key为sku_id的值 记性累加count计算
        pl.hincrby('carts_%s' % user.id, sku_id, count)  # carts_userid : {sku_id1:10, sku_id2:1,sku_id3:5}
        if selected:
            pl.sadd('selected_%s' % user.id, sku_id)
        pl.execute()

        return JsonResponse({'code': 0, 'errmsg': '添加购物车成功'})

    def get(self, request):
        user = request.user

        # - 从redis里取出skuid
        redis_conn: Redis = get_redis_connection('carts')
        # 获取hash的数据
        redis_carts = redis_conn.hgetall('carts_%s' % user.id)  # {sku_id1:10, sku_id2:1,sku_id3:5}

        # 获取set里的数据
        carts_selected = redis_conn.smembers('selected_%s' % user.id)
        print("redis_carts", redis_carts, "---carts_selected---", carts_selected)

        # 把redis取出的数据 转为字典 合并存储 方便后面获取
        cart_dict = {}  # {'skuid1':{"count":10,"selected":True},'skuid2':{"count":3,"selected":False}}
        for sku_id, count in redis_carts.items():
            # sku_id和count当前是bytes类型 直接转为int
            cart_dict[int(sku_id)] = {
                "count": int(count),
                "selected": sku_id in carts_selected
            }

        # - 根据id查询具体sku数据
        # 获取所有的skuid
        sku_ids = redis_carts.keys()
        # 获取所有的sku对象
        skus = SKU.objects.filter(id__in=sku_ids)

        cart_skus = []
        for sku in skus:
            cart_skus.append({"id": sku.id,
                              "name": sku.name,  # 名字
                              "default_image_url": sku.default_image.url,  # 图片
                              'price': sku.price,  # 单价
                              'count': cart_dict.get(sku.id).get('count'),  # 数量
                              'selected': cart_dict.get(sku.id).get('selected'),  # 是否被选中
                              })

        return JsonResponse({"cart_skus": cart_skus, 'code': 0, 'errmsg': 'ok'})

    def put(self, request):
        # - 获取数据 sku_id  count  selected
        data_dict = json.loads(request.body)
        sku_id = data_dict.get('sku_id')
        count = data_dict.get('count')
        selected = data_dict.get('selected', True)
        # - 校验
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return HttpResponseBadRequest('缺少必传参数')
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseBadRequest('商品sku_id不存在')
        # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return HttpResponseBadRequest('参数count有误')

        user = request.user
        # - redis直接修改数据
        redis_conn: Redis = get_redis_connection('carts')
        pl = redis_conn.pipeline()
        # hash    carts_userid:{sku_id5:10, sku_id6 :3}
        pl.hset('carts_%s' % user.id, sku_id, count)
        # set
        if selected:
            pl.sadd("selected_%s" % user.id, sku_id)
        else:
            pl.srem("selected_%s" % user.id, sku_id)

        pl.execute()
        # - 返回结果
        cart_sku = {
            'count': count
        }

        return JsonResponse({'code': 0, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})

    def delete(self, request):
        # print(request.body)

        # - 1接收参数sku_id
        data_dict = json.loads(request.body)
        # print(data_dict)
        # print(type(data_dict))
        sku_id = data_dict.get('sku_id')
        # print(sku_id)
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseBadRequest('商品sku_id不存在')
        # - 2从redis删除  hash  set
        user = request.user
        # - redis直接修改数据
        redis_conn: Redis = get_redis_connection('carts')
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, sku_id)
        pl.srem('selected_%s' % user.id, sku_id)
        pl.execute()
        # - 3 返回
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class CartsSelectView(LoginRequiredJSONMixin, View):
    """全选功能"""

    def put(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return HttpResponseBadRequest('参数selected有误')

        user = request.user
        # 用户已登录，操作redis购物车
        redis_conn = get_redis_connection('carts')
        cart = redis_conn.hgetall('carts_%s' % user.id)
        sku_id_list = cart.keys()
        if selected:
            # 全选
            redis_conn.sadd('selected_%s' % user.id, *sku_id_list)
        else:
            # 取消全选
            redis_conn.srem('selected_%s' % user.id, *sku_id_list)
        return JsonResponse({'code': 0, 'errmsg': '全选购物车成功'})


class CartsSimpleView(View):
    def get(self, request):
        user = request.user

        # - 从redis里取出skuid
        redis_conn: Redis = get_redis_connection('carts')
        # 获取hash的数据
        redis_carts = redis_conn.hgetall('carts_%s' % user.id)  # {sku_id1:10, sku_id2:1,sku_id3:5}

        # 获取set里的数据
        carts_selected = redis_conn.smembers('selected_%s' % user.id)
        print("redis_carts", redis_carts, "---carts_selected---", carts_selected)

        # 把redis取出的数据 转为字典 合并存储 方便后面获取
        cart_dict = {}  # {'skuid1':{"count":10,"selected":True},'skuid2':{"count":3,"selected":False}}
        for sku_id, count in redis_carts.items():
            # sku_id和count当前是bytes类型 直接转为int
            cart_dict[int(sku_id)] = {
                "count": int(count),
                "selected": sku_id in carts_selected
            }

        # - 根据id查询具体sku数据
        # 获取所有的skuid
        sku_ids = redis_carts.keys()
        # 获取所有的sku对象
        skus = SKU.objects.filter(id__in=sku_ids)

        cart_skus = []
        for sku in skus:
            cart_skus.append({"id": sku.id,
                              "name": sku.name,  # 名字
                              "default_image_url": sku.default_image.url,  # 图片
                              'count': cart_dict.get(sku.id).get('count'),  # 数量
                              })


        return JsonResponse({"cart_skus": cart_skus, 'code': 0, 'errmsg': 'ok'})
