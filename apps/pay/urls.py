from django.urls import path

from apps.pay.views import PaymentView, PaymentStatusView

urlpatterns = [
    # 订单结算页面数据
    path('payment/<int:order_id>/', PaymentView.as_view()),

    path('payment/status/', PaymentStatusView.as_view()),

]
