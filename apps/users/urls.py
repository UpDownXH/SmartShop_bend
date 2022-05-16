from django.urls import path
from . import views

urlpatterns = [
    # 判断用户名是否重复
    path('usernames/<username:username>/count/',views.UsernameCountView.as_view()),
    # 判断手机号是否重复
    path('mobiles/<mobile:mobile>/count/',views.MobileCountView.as_view()),
    # 注册的视图
    path('register/', views.RegisterView.as_view()),
    # 登录
    path('logout/', views.LogoutView.as_view()),
    # 登出
    path('login/', views.LoginView.as_view()),
    # 用户信息
    path('info/', views.UserInfoView.as_view()),
    # 邮箱接口
    path('emails/', views.SaveEmailView.as_view()),
    # 邮箱验证接口
    path('emails/verification/', views.EmailVerifyView.as_view()),
]