from django.urls import path

from apps.carts.views import CartsView, CartsSelectView, CartsSimpleView

urlpatterns = [
    # 购物车增删改查
    path('carts/', CartsView.as_view()),
    #　全选
    path('carts/selection/', CartsSelectView.as_view()),
    # 简单购物车
    path('carts/simple/', CartsSimpleView.as_view()),

]
