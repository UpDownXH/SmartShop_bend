from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

from apps.smartshop_admin.serializers.user_serializers import UserModelSerializer
from apps.smartshop_admin.utils import PageNum
from apps.users.models import User


class UserListView(ListCreateAPIView):
    # 1指定查询集
    # queryset = User.objects.all()
    # 2指定序列化器
    serializer_class = UserModelSerializer
    # 3分页累
    pagination_class = PageNum


    def get_queryset(self):

        # 获取keyword的值
        keyword = self.request.query_params.get('keyword')
        if not keyword:
            # 没有数据 就查询所有内容
            queryset = User.objects.all()
        else:
            # 如果有数据 就过滤
            queryset = User.objects.filter(username=keyword)

        return queryset


