import json

from django.core.paginator import Paginator
from django.http import JsonResponse
# Create your views here.
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from haystack.views import SearchView
from redis.client import Redis

from apps.ad.models import ContentCategory
from apps.goods.models import GoodsCategory, SKU
from utils.goodsutils import get_categories, get_breadcrumb, get_goods_specs
from utils.views import LoginRequiredJSONMixin
from apps.goods.serializers.detailGoodsSerializers import SKUModelSerializer
from apps.smartshop_admin.serializers.sku_serializers import SKUSerializer


class IndexView(View):
    def get(self, request):
        try:
            categories = get_categories()
        except Exception as e:
            print(e)
            return {'code': 1, 'errmsg': 'get data error'}

        # huo qu guanggao shuju
        contents = {}

        # - 1 ContentCategory获取所有广告的类别
        content_categories = ContentCategory.objects.all()
        # - 2 遍历所有的类别 获取每个类别下的广告
        for content_cat in content_categories:
            content_items = content_cat.content_set.filter(status=True).order_by('sequence')
            #   - 获取的时候 按照status 过滤
            #   - 按照sequence排序
            content_items_list = []
            for item_c in content_items:
                content_items_list.append(item_c.to_dict())

            contents[content_cat.key] = content_items_list

        print(contents)

        return JsonResponse({'code': 0, 'errmsg': 'ok', "categories": categories, 'contents': contents})
        # return render(request, 'index.html', context)
# 商品列表页
# list/115/skus/?page=1&page_size=5&ordering=-create_time
# 115 是分类的id   page是第几页 page_size是每页有几条  ordering是排序
class ListView(View):
    def get(self, request, category_id):

        # - 1 接收参数  校验
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        ordering = request.GET.get('ordering')

        # - 2 获取分类商品的数据
        # huoqu leibie duixiang
        try:

            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': "category query err"})

        skus = SKU.objects.filter(category=category, is_launched=True).order_by(ordering)

        #   - 2.1 分页  排序
        # canshu2 biaoshi fenye de shuliang   15
        paginator = Paginator(skus, page_size)
        page_skus = paginator.page(page)
        # zong gong you jiye
        count = paginator.num_pages

        #   - 2.2面包屑导航
        breadcrumb = get_breadcrumb(category)

        # - 热销商品数据
        # - 3把数据转为字典
        # - 4返回json
        sku_list = []
        for sku in page_skus:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
            })

        return JsonResponse({'code': 0, 'errmsg': "ok", 'count': count, "list": sku_list,
                             'breadcrumb': breadcrumb})


class HotGoodsView(View):
    """商品热销排行"""
    def get(self, request, category_id):
        """提供商品热销排行JSON数据"""
        # 根据销量倒序
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]

        # 序列化
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url if sku.default_image else "",
                'name': sku.name,
                'price': sku.price
            })

        return JsonResponse({'code': 0, 'errmsg': 'OK', 'hot_skus': hot_skus})
#
#
class MySearchView(SearchView):
    '''重写SearchView类'''

    def create_response(self):
        # 获取搜索结果
        context = self.get_context()
        data_list = []
        page_count = context['page'].paginator.num_pages
        for sku in context['page'].object_list:
            data_list.append({
                'id': sku.object.id,
                'name': sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url,
                'searchkey': context.get('query'),
                'page_nums': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count,
            })
        # 拼接参数, 返回

        return JsonResponse({"code": 0, 'errmsg': 'ok', "data_list": data_list, 'page_count': page_count}, safe=False)

#
class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        # 完善的功能
        # sku = SKU.objects.filter(spu_id=sku_id)
        # workHard = SKUSerializer(sku,many=True)
        # print(haha.data)
        sku = SKU.objects.get(id=sku_id)
        workHard = {}
        workHard['id'] = 1
        workHard['name'] = sku.name
        workHard['caption'] = sku.caption
        workHard['price'] = sku.price
        workHard['cost_price'] = sku.cost_price
        workHard['market_price'] = sku.market_price
        workHard['stock'] = sku.stock
        workHard['sales'] = sku.sales
        workHard['comments'] = sku.comments
        workHard['is_launched'] = sku.is_launched
        workHard['default_image'] = sku.default_image.url




        return JsonResponse({"code": 0, 'errmsg': 'ok','data':workHard}, safe=False)

        # 获取当前sku的信息
        # try:
        #     sku = SKU.objects.get(id=sku_id)
        # except SKU.DoesNotExist:
        #     return render(request, '404.html')
        #
        # # 查询商品频道分类
        # categories = get_categories()
        # # 查询面包屑导航
        # breadcrumb = get_breadcrumb(sku.category)
        # # 查询SKU规格信息
        # goods_specs = get_goods_specs(sku)
        #
        # # 渲染页面
        # context = {
        #     'categories': categories,
        #     'breadcrumb': breadcrumb,
        #     'sku': sku,
        #     'specs': goods_specs,
        # }
        # return render(request, 'detail.html', context)

#
class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request, category_id):
        try:
            # 1.获取当前商品
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})

        # 2.查询日期数据
        from datetime import date
        # 获取当天日期
        today_date = date.today()

        from apps.goods.models import GoodsVisitCount
        try:
            # 3.如果有当天商品分类的数据  就累加数量
            count_data = category.goodsvisitcount_set.get(date=today_date)
        except:
            # 4. 没有, 就新建之后在增加
            count_data = GoodsVisitCount()

        try:
            count_data.count += 1
            count_data.category = category
            count_data.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '新增失败'})

        return JsonResponse({'code': 0, 'errmsg': 'OK'})


class UserBrowseHistory(LoginRequiredJSONMixin, View):
    def post(self, request):
        # 获取当前登录的用户
        user = request.user

        # - - 接收参数
        data_dict = json.loads(request.body)
        sku_id = data_dict.get("sku_id")
        #   - 校验
        if not sku_id:
            return JsonResponse({'code': 400, 'errmsg': 'sku不存在'})

        # 去数据库查询校验
        try:
            SKU.objects.get(id=sku_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': 'sku不存在'})

        #   - 保存浏览数据
        redis_conn: Redis = get_redis_connection("history")
        # 获取管道
        pl = redis_conn.pipeline()
        #     - 先去重  0表示 删除所有的重复数据
        pl.lrem('history_%s' % user.id, 0, sku_id)
        #     - 存储  key包含userid 区分不同用户 的数据
        pl.lpush('history_%s' % user.id, sku_id)
        #     - 截取5个
        pl.ltrim('history_%s' % user.id, 0, 4)
        # 执行管道命令
        pl.execute()

        return JsonResponse({'code': 0, 'errmsg': 'ok'})

    def get(self, request):
        user = request.user
        try:
            # - 获取redis保存的sku的id
            redis_conn: Redis = get_redis_connection("history")
            sku_ids = redis_conn.lrange('history_%s' % user.id, 0, -1)
            # - 根据id查询商品的名字  图片  价格
            skus = []
            for sku_id in sku_ids:
                sku = SKU.objects.get(id=sku_id)
                skus.append({
                    'id': sku.id,
                    'name': sku.name,
                    'default_image_url': sku.default_image.url,
                    'price': sku.price
                })
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': 'data error'})

        return JsonResponse({'code': 0, 'errmsg': 'OK', 'skus': skus})
