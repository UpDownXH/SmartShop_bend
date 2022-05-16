from django.urls import path

from apps.oauth.views import *

urlpatterns = [
    path('qq/authorization/', WeiboAuthURLView.as_view()),
    # 登录用户验证的视图
    path('oauth_callback/', WeiboAuthUserView.as_view()),

]