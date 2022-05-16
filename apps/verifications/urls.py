from django.contrib import admin
from django.urls import path, include

from apps.users.views import UsernameCountView, RegisterView
from apps.verifications.views import ImageCodeView, SmsView

urlpatterns = [
    # 获取验证码图片
    path('image_codes/<uuid:uuid>/', ImageCodeView.as_view()),

    # 发送短信验证码的路由
    path('sms_codes/<mobile>/', SmsView.as_view()),

]
