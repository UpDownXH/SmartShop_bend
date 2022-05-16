from rest_framework.generics import ListAPIView
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SKU, GoodsCategory, SPU, SPUSpecification
from apps.smartshop_admin.serializers.sku_serializers import SKUSerializer, SKUCategorieSerializer, GoodsSimpleSerializer, \
    SpecsModelSerializer
from apps.smartshop_admin.utils import PageNum


class SKUModelViewSet(ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer

    # 分页
    pagination_class = PageNum
    # 添加权限限制　　DjangoModelPermission对模型类权限限制
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


# 获取所有三级类别
class SKUCategoriesView(ListAPIView):
    serializer_class = SKUCategorieSerializer
    # 或者
    queryset = GoodsCategory.objects.filter(subs=None)


# spu数据获取
class GoodsSimpleView(ListAPIView):
    serializer_class = GoodsSimpleSerializer
    queryset = SPU.objects.all()


# 规格的视图
class GoodsSpecView(ListAPIView):
    serializer_class = SpecsModelSerializer

    def get_queryset(self):
        # 获取地址里传来的spu的id  key为pk
        pk = self.kwargs.get('pk')
        # 根据spuid获取所有的规格
        return SPUSpecification.objects.filter(spu_id=pk)
