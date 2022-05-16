from rest_framework.serializers import ModelSerializer

from apps.goods.models import SKUImage, SKU


# 图片的序列化类
class SKUImageSerializer(ModelSerializer):
    class Meta:
        model = SKUImage
        fields = '__all__'

# 添加视频的序列化器
class SKUSerializer(ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name')
