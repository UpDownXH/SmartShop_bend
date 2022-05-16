from django.db import transaction
from rest_framework import serializers

from apps.goods.models import SKU, GoodsCategory, SPU, SPUSpecification, SpecificationOption, SKUSpecification


class SKUSpecificationSerialzier(serializers.ModelSerializer):
    """
        SKU规格表序列化器
    """
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification  # SKUSpecification中sku外键关联了SKU表
        fields = ("spec_id", 'option_id')


class SKUSerializer(serializers.ModelSerializer):

    # 添加2个字段来接收 category_id 和 spu_id
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    # 自己定义spu和category字段为 StringRelatedField
    spu = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    # 定义specs字段来接收规格信息  规格信息是一个列表 many=Tue
    # 规格信息 spec_id 和 option_id 和 SKUSpecification 对应
    # 于是我们定义 SKUSpecificationSerialzier
    # 期望 SKUSpecificationSerialzier 序列化器帮助我们实现 反序列化操作
    specs = SKUSpecificationSerialzier(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        # validated_data是前段传来的所有数据

        # 1先把规格数据 获取到 并从字典里删除
        specs = validated_data.pop('specs')

        with transaction.atomic():
            save_point = transaction.savepoint()  # 获取保存点
            try:
                # 2先保存sku
                sku = SKU.objects.create(**validated_data)
                # 3循环specs保存规格
                for spec in specs:
                    SKUSpecification.objects.create(sku=sku, **spec)
            except Exception as e:
                print(e)
                transaction.savepoint_rollback(save_point)  # 回滚到save_point创建的位置
            else:
                transaction.savepoint_commit(save_point)

        # 返回sku数据
        return sku

    def update(self, instance, validated_data):
        # 1先把规格数据 获取到 并从字典里删除
        specs = validated_data.pop('specs')
        # 2 调用父类的update方法
        super().update(instance, validated_data)
        # # 3循环specs更新规格的选项值
        for spec in specs:
            # 获取新数据里的规格id
            new_spec_id = spec.get('spec_id')
            # 获取新数据里的选项值的id
            new_option_id = spec.get('option_id')
            SKUSpecification.objects.filter(sku=instance, spec_id=new_spec_id).update(option_id=new_option_id)
        return instance


# 获取三级类别的序列化器
class SKUCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


# spu数据
class GoodsSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = '__all__'


# 选项的序列化器
class GoodsOptineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ('id', 'value')


# 规格的序列化器
class SpecsModelSerializer(serializers.ModelSerializer):
    options = GoodsOptineSerializer(many=True)
    # 返回的数据规定 spu是名字  spu_id才是id
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'
