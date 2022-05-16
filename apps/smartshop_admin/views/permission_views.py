from django.contrib.auth.models import Permission
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.smartshop_admin.serializers.permission_serializers import PermissionSerialzier, ContentTypeSerialzier, \
    GroupSerialzier, AdminSerializer
from apps.smartshop_admin.utils import PageNum

# 权限
from apps.users.models import User


class PermissionView(ModelViewSet):
    serializer_class = PermissionSerialzier
    queryset = Permission.objects.order_by('id')
    pagination_class = PageNum


from django.contrib.auth.models import ContentType


# 权限类型
class ContentTypeAPIView(ListAPIView):
    serializer_class = ContentTypeSerialzier
    # 　权限类型的所有数据
    queryset = ContentType.objects.all()

    def get(self, request):
        return self.list(request)


from django.contrib.auth.models import Group


# 组管理
class GroupView(ModelViewSet):
    serializer_class = GroupSerialzier
    queryset = Group.objects.all()
    pagination_class = PageNum


from django.contrib.auth.models import Permission


# 获取简单权限 为了添加组的时候显示列表
class GroupSimpleAPIView(ListAPIView):
    serializer_class = PermissionSerialzier
    queryset = Permission.objects.all()

    def get(self, request):
        return self.list(request)


# 管理员管理
class AdminView(ModelViewSet):
    serializer_class = AdminSerializer
    # 获取管理员用户
    queryset = User.objects.filter(is_staff=True)
    pagination_class = PageNum


# 添加管理员的时候 获取组的数据
class AdminSimpleAPIView(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerialzier

    def get(self, request):
        return self.list(request)
