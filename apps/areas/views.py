import json

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.areas.models import Area, Address
from utils.views import LoginRequiredJSONMixin


class AreasView(View):
    def get(self, request):
        # - 1 django提供了cache这个模块 做缓
        # - 2 存的是字段数据
        # - 3 在数据库查询前 先去缓存查找

        province_list = cache.get('provinces')
        if not province_list:
            print("省市区没有缓存")

            # 1  去数据库查询所有的省份数据
            try:
                areas = Area.objects.filter(parent=None)
            except Exception as e:
                print(e)
                return JsonResponse({'code': 400, 'errmsg': "获取省份失败，网络异常"})

            province_list = []

            for a in areas:
                province_list.append({"id": a.id, "name": a.name})
            # - 4 如果缓存是空 去mysql查  查完后在存入缓存
            cache.set('provinces', province_list, 3600 * 24 * 30)
            # - 5 如果缓存有，直接返回

        # 2  返回
        return JsonResponse({'code': 0, 'province_list': province_list})


class SubAreasView(View):
    def get(self, request, area_id):
        # 1 获取路径中的上一级的地区的id
        # 正则校验area_id

        # 去缓存找
        subs = cache.get('cities_%s' % area_id)

        if not subs:
            print('没有市区的缓存')
            # 2 根据上一级的id获取下一级的数据(数据库操作)
            try:
                subareas = Area.objects.filter(parent_id=area_id)
            except Exception as e:
                print(e)
                return JsonResponse({'code': 400, 'errmsg': "获取市区失败，网络异常"})

            # 3 把下一级数据 做拼接
            subs = []
            for a in subareas:
                subs.append({'id': a.id, 'name': a.name})

            # 把数据存到缓存里
            cache.set('cities_%s' % area_id, subs, 3600 * 24 * 30)

        # data.sub_data.subs

        # 4 返回给前端
        return JsonResponse({'code': 0, 'sub_data': {'subs': subs}})


class AddressView(LoginRequiredJSONMixin, View):
    def post(self, request):
        # - - 1 获取传来的参数
        body = request.body
        data_dict = json.loads(body)
        receiver = data_dict.get('receiver')
        province_id = data_dict.get('province_id')
        city_id = data_dict.get('city_id')
        district_id = data_dict.get('district_id')
        place = data_dict.get('place')
        mobile = data_dict.get('mobile')
        tel = data_dict.get('tel')
        email = data_dict.get('email')

        # - 2 校 验
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400, 'errmsg': "数据不全"})
        # - 3  使用Address模型类 添加数据
        try:
            address = Address.objects.create(user=request.user,
                                             title=receiver,
                                             receiver=receiver,
                                             province_id=province_id,
                                             city_id=city_id,
                                             district_id=district_id,
                                             place=place,
                                             mobile=mobile,
                                             tel=tel,
                                             email=email)

            # 设置address为默认地址
            request.user.default_address = address.id
            request.user.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 505, 'errmsg': "保存失败"})

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # - 4 返回成功信息
        return JsonResponse({'code': 0, 'errmsg': "ok", 'address': address_dict})

    def get(self, request):

        # - 1 获取用户对象
        user = request.user
        # - 2获取所有地址
        # addresses = Address.objects.all(user=user)
        try:
            addresses = user.addresses.all().filter(is_deleted=False)

            # 创建一个空列表 存地址的字典数据
            address_dict_list = []
            # 循环拼接字典 添加到列表里
            for address in addresses:
                address_dict = {
                    "id": address.id,
                    "title": address.title,
                    "receiver": address.receiver,
                    "province": address.province.name,
                    "city": address.city.name,
                    "district": address.district.name,
                    "place": address.place,
                    "mobile": address.mobile,
                    "tel": address.tel,
                    "email": address.email
                }
                # - 3拼接列表
                address_dict_list.insert(0, address_dict)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 501, 'errmsg': '查询失败'})

        # - 4 返回
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'addresses': address_dict_list,
                             'default_address_id': request.user.default_address})


class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""
        pass

    def delete(self, request, address_id):
        """删除地址"""
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return JsonResponse({'code': 0, 'errmsg': '删除地址成功'})
