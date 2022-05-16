from django.urls import path
from rest_framework.routers import DefaultRouter


# from . import views
from apps.smartshop_admin.login import admin_jwt_token
from apps.smartshop_admin.views.count_views import UserDailyActiveCountView, UserDailyOrderCountView, \
    UserMonthCountView, UserDayCountView
from apps.smartshop_admin.views.image_views import SKUImageView, SKUView
from apps.smartshop_admin.views.permission_views import PermissionView, GroupView, AdminView, ContentTypeAPIView, \
    GroupSimpleAPIView, AdminSimpleAPIView
from apps.smartshop_admin.views.sku_view import GoodsSimpleView, SKUModelViewSet, SKUCategoriesView, GoodsSpecView
from apps.smartshop_admin.views.user_view import UserListView

urlpatterns = [
    # 　添加返回ｔｏｋｅｎ的ｖｉｅｗ
    path('authorizations/', admin_jwt_token),
    # 日活用户
    path('statistical/day_active/', UserDailyActiveCountView.as_view()),
    # 日下单用户
    path('statistical/day_orders/', UserDailyOrderCountView.as_view()),
    # 月增用户统计
    path('statistical/month_increment/', UserMonthCountView.as_view()),
    # 日增用户统计
    path('statistical/day_increment/', UserDayCountView.as_view()),
    # 获取所有用户、查询用户、添加用户
    path('users/', UserListView.as_view()),
    # 获取简单的sku数据 用来添加图片
    path('skus/simple/', SKUView.as_view()),
    # 获取spu数据
    path('goods/simple/', GoodsSimpleView.as_view()),
    # 获取三级类别
    path('skus/categories/', SKUCategoriesView.as_view()),
    # 规格
    path('goods/<int:pk>/specs/', GoodsSpecView.as_view()),
    # 权限类型
    path('permission/content_types/', ContentTypeAPIView.as_view()),
    # 获取简单权限 为了添加组的时候显示列表
    path('permission/simple/', GroupSimpleAPIView.as_view()),
    # # 添加管理员的时候 获取组的数据
    path('permission/groups/simple/', AdminSimpleAPIView.as_view()),
]

# 创建router实例
router = DefaultRouter()
# 注册路由，继承视图集的
router.register(r'skus/images', SKUImageView, basename='image')
# sku管理
router.register(r'skus', SKUModelViewSet, basename='sku')
# # 权限
router.register(r'permission/perms', PermissionView, basename='perms')
# # 组管理
router.register(r'permission/groups', GroupView, basename='group')
# # 管理员管理
router.register(r'permission/admins', AdminView, basename='group')

# 将router生成的路由追加到urlpatterns中
urlpatterns += router.urls