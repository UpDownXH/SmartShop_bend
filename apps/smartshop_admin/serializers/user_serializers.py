from rest_framework.serializers import ModelSerializer

from apps.users.models import User


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email','password')

    def create(self, validated_data):
        #创建用户对象 create_user会给密码加密
        user = User.objects.create_user(**validated_data)
        return user
