from rest_framework.serializers import ModelSerializer

from apps.goods.models import SKU


class SKUModelSerializer(ModelSerializer):
    class Meta:
        model = SKU
        fields = '__all__'

