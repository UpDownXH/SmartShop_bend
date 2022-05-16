import json
import traceback
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection
from redis import Redis

from apps.areas.models import Address
from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from utils.views import LoginRequiredJSONMixin


class OrderSettlementView(LoginRequiredJSONMixin, View):
    """订单结算页面显示"""

    def get(self, request):
        user = request.user
        # - 1 从redis查询所有的购物车数据  过滤出已经选中的
        # - 从redis里取出skuid
        redis_conn: Redis = get_redis_connection('carts')
        # 获取hash的数据
        redis_carts = redis_conn.hgetall('carts_%s' % user.id)  # {sku_id1:10, sku_id2:1,sku_id3:5}
        # 获取set里的数据
        carts_selected = redis_conn.smembers('selected_%s' % user.id)

        # 　把选中的sku的数据 重新 放到一个新的字典里  值是他的数量
        cart_data = {}
        for sku_id in carts_selected:
            cart_data[int(sku_id)] = int(redis_carts[sku_id])

        skus = SKU.objects.filter(id__in=cart_data.keys())
        sku_list = []
        for sku in skus:
            sku_list.append({
                "id": sku.id,
                "default_image_url": sku.default_image.url,
                "name": sku.name,
                "price": sku.price,
                "count": cart_data[sku.id],  # 获取数量
            })
        print('sku_list', sku_list)

        # - 2 运费  这里固定为10元
        freight = Decimal('10.00')  # 运费
        # - 3 获取所有的用户的地址信息
        addrs = Address.objects.filter(user=user, is_deleted=False)

        addrs_list = []
        for addr in addrs:
            addrs_list.append({
                "province": addr.province.name,
                "city": addr.city.name,
                "district": addr.district.name,
                "place": addr.place,
                "receiver": addr.receiver,
                "province": addr.mobile,
                "id": addr.id,
            })
        # - 4 拼接json返回

        context = {
            "skus": sku_list,
            'freight': freight,
            "addresses": addrs_list,
            'default_address_id': request.user.default_address,
        }

        return JsonResponse({"context": context, 'code': 0, 'errmsg': 'ok'})


class OrderCommitView(LoginRequiredJSONMixin, View):

    def post(self, request):
        # - 1 接收参数   地址id和支付方式   address_id: 5, pay_method: 2
        data_dict = json.loads(request.body)
        address_id = data_dict.get("address_id")
        pay_method = data_dict.get("pay_method")

        # - 2 校验
        # 校验参数
        if not all([address_id, pay_method]):
            return HttpResponseBadRequest('缺少必传参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return HttpResponseBadRequest('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return HttpResponseBadRequest('参数pay_method错误')

        user = request.user

        # 开启事务

        # 3生成订单编号：年月日时分秒+用户编号
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        # 　开启事务
        with transaction.atomic():
            # 创建回滚点
            save_id = transaction.savepoint()

            try:
                # -4  保存订单对象 OrderInfo
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,  # 商品数量
                    total_amount=0,  # 商品总金额
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM["UNSEND"] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        "CASH"] else
                    OrderInfo.ORDER_STATUS_ENUM["UNPAID"]
                )

                # - 5  从redis里获取购物车商品信息   过滤被勾选的数据
                redis_conn: Redis = get_redis_connection('carts')
                # 获取hash的数据
                redis_carts = redis_conn.hgetall('carts_%s' % user.id)  # {sku_id1:10, sku_id2:1,sku_id3:5}
                # 获取set里的数据
                carts_selected = redis_conn.smembers('selected_%s' % user.id)

                # 　把选中的sku的数据 重新 放到一个新的字典里  值是他的数量
                cart_data = {}
                for sku_id in carts_selected:
                    cart_data[int(sku_id)] = int(redis_carts[sku_id])

                # - 6 遍历所有的商品id
                sku_ids = cart_data.keys()
                for sku_id in sku_ids:

                    while True:
                        #   - 查询每一个商品的SKU数据
                        sku = SKU.objects.get(id=sku_id)

                        # 读取原始库存
                        origin_stock = sku.stock  # 10
                        origin_sales = sku.sales

                        # 获取当前这件商品的购买数量
                        sku_count = cart_data[sku.id]
                        # 判断数量和库存
                        if sku_count > sku.stock:
                            # 又错误 要回滚
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'code': 400, 'errmsg': '库存不足'})

                        print(user.username, '库存没有问题')
                        # import time
                        # time.sleep(5)
                        # update tb_sku set stock = 7 where id = sku.id  and stock = origin_stock

                        # 商品的销量累加
                        # sku.sales += sku_count
                        # 商品的库存减少
                        # sku.stock -= sku_count
                        # print(user.username, 'sku.stock', sku.stock)
                        # sku.save()

                        # 乐观锁更新库存和销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)
                        if result == 0:
                            continue

                        # - 7 生成订单商品对象  OrderGoods
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )

                        # - 8 把sku的数量和价格累加到订单对象里面
                        order.total_count += sku_count
                        order.total_amount += (sku_count * sku.price)

                        break

                # - 9 总价格添加运费  然后save
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                traceback.print_exc()  # 会打印原始红色的异常数据
                # 回滚
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code': 400, 'errmsg': '下单失败'})

            # 提交事务
            transaction.savepoint_commit(save_id)

        # - 10 清空购物车的所有数据  注意只删除选中的数据
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *carts_selected)
        pl.srem('selected_%s' % user.id, *carts_selected)
        pl.execute()

        # - 11返回json
        # 响应提交订单结果
        return JsonResponse({'code': 0, 'errmsg': '下单成功', 'order_id': order.order_id})
