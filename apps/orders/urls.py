from django.urls import path

from apps.orders.views import OrderSettlementView, OrderCommitView

urlpatterns = [
    # 订单结算页面数据
    path('orders/settlement/', OrderSettlementView.as_view()),
    # 提交订单
    path('orders/commit/', OrderCommitView.as_view()),

]
