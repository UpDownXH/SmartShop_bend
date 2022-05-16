import json
import re

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from redis import Redis

# from apps.goods.models import SKU
from apps.users.models import User
from apps.users.utils import generate_verify_email_url, check_verify_email_token
from celery_tasks.email.tasks import send_email_active
from utils.views import LoginRequiredJSONMixin


# 判断用户名是否重复注册
class UsernameCountView(View):
    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


# 判断手机号是否重复注册
class MobileCountView(View):
    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


# 注册视图
class RegisterView(View):

    def post(self, request):
        body_byte = request.body
        data_dict = json.loads(body_byte)
        username = data_dict.get('username')
        password = data_dict.get('password')
        password2 = data_dict.get('password2')
        mobile = data_dict.get('mobile')
        sms_code = data_dict.get('sms_code')
        allow = data_dict.get('allow')

        if not all([username, password, password2, mobile, sms_code, allow]):
            return JsonResponse({'code': 400, 'errmsg': '数据上传错误'})

        redis: Redis = get_redis_connection('code')
        sms_code_redis = redis.get('smscode_%s' % mobile)

        if not sms_code_redis:
            return JsonResponse({'code': 400, 'errmsg': '驗證碼過期'})

        sms_code_redis = sms_code_redis.decode()
        if sms_code != sms_code_redis:
            return JsonResponse({'code': 400, 'errmsg': '驗證碼输入错误'})

        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '注册失败'})
        login(request, user)

        response = JsonResponse({"code": "0", "errmsg": "OK"})
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response

# 登录
class LoginView(View):
    def post(self, request):
        # 1 接收json数据
        body = request.body
        data_dict = json.loads(body)
        username = data_dict.get('username')
        password = data_dict.get('password')
        remembered = data_dict.get('remembered')

        # 2 验证数据是否为空  正则
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '写错了'})

        import re
        if re.match('^1[3-9]\d{9}$', username):
            # 手机号
            User.USERNAME_FIELD = 'mobile'
        else:
            # account 是用户名
            # 根据用户名从数据库获取 user 对象返回.
            User.USERNAME_FIELD = 'username'

        # 3 验证码用户名和密码是否正确
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse({'code': 400, 'errmsg': '用户名密码错误'})

        # 4 状态保持
        login(request, user)

        # 5 判断是否记住登录
        if remembered:
            # 如果记住:  设置为两周有效
            request.session.set_expiry(None)
        else:
            # 如果没有记住: 关闭立刻失效
            request.session.set_expiry(0)
        # 6 返回响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response

# 登出
class LogoutView(View):

    def delete(self, request):
        """实现退出登录逻辑"""
        # 清理session
        logout(request)
        # 退出登录，重定向到登录页
        response = JsonResponse({'code': 0,
                                 'errmsg': 'ok'})
        # 退出登录时清除cookie中的username
        response.delete_cookie('username')

        return response

# 用户信息
class UserInfoView(LoginRequiredJSONMixin, View):
    def get(self, request):
        return JsonResponse({'code': 0, 'errmsg': 'ok',
                             'info_data': {'username': request.user.username
                                 , 'mobile': request.user.mobile
                                 , 'email': request.user.email
                                 , 'email_active': request.user.email_active
                                           }})

# 添加邮箱的视图
class SaveEmailView(LoginRequiredJSONMixin, View):
    def put(self, request, sendmail=None):
        #  1 获取json数据 转为字典
        body = request.body
        data_dict = json.loads(body)

        #  2 从字典里拿到邮箱地址
        email = data_dict.get('email')
        #  3 校验
        if not email:
            return JsonResponse({'code': 300, 'errmsg': '邮箱不存在'})
        #  4 保存到数据库
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '邮箱保存失败'})

        # 异步发送认证邮件
        # 163 126  qq  sina  gmail
        verify_url = generate_verify_email_url(request.user)
        message = '<p>尊敬的用户您好！</p><p>感谢您使用美多商城。</p><p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p><p><a href="%s">点我激活</a></p>' % (
            email, verify_url)

        send_email_active.delay(email, message)

        #  5 返回相应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

# 邮箱验证视图
class EmailVerifyView(View):
    def put(self, request):
        # - 1 接收请求（PUT）数据
        # - 2 获取token
        token = request.GET.get('token')

        # - 3 对token解密 获取解密数据里的user_id
        user_id = check_verify_email_token(token)
        # - 5 如果获取不到  说明过期
        if not user_id:
            return JsonResponse({'code': 400, 'errmsg': '激活邮件已经过期'})

        # - 6 根据user_id去数据库查询
        try:
            user = User.objects.get(id=user_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 405, 'errmsg': '当前用户不存在'})

        # - 7 把查到user对象的 email_active字段 改为true  不要忘记save
        user.email_active = True
        user.save()
        return JsonResponse({'code': 0, 'errmsg': '激活成功'})
