from django.contrib.auth.models import Permission
from rest_framework import serializers

from apps.users.models import User


class PermissionSerialzier(serializers.ModelSerializer):
    """
    用户权限表序列化器
    """

    class Meta:
        model = Permission
        fields = "__all__"


from django.contrib.auth.models import ContentType


class ContentTypeSerialzier(serializers.ModelSerializer):
    """
    权限类型序列化器
    """

    class Meta:
        model = ContentType
        fields = ('id', 'name')


from django.contrib.auth.models import Group


# 组管理
class GroupSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


# 管理员管理
class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required':False
            }
        }

    def create(self, validated_data):
        # 1 调用父类方法创建 用户对象
        user = super().create(validated_data)
        # 2 从validated_data取出密码
        password = validated_data.get('password')
        # 3 调用set_password设置密码，会给密码加密
        user.set_password(password)
        # 4 设置is_staff属性为1
        user.is_staff = 1
        # 5 保存
        user.save()
        # 6 返回对象
        return user

    def update(self, instance, validated_data):
        # - 1 调用父类方法 更新数据
        super().update(instance, validated_data)
        # - 2 获取密码
        password = validated_data.get('password')
        # - 3如果密码存在 对密码加密保存
        if password:
            instance.set_password(password)
            instance.save()
        # - 4 返回 数据
        return instance
