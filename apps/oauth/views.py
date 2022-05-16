import json

from django.contrib.auth import login
from django.http import JsonResponse

# Create your views here.
from django.views import View

from apps.oauth.models import OAuthWEIBOUser
from libs.oauthlogin.weibo import OAuth_WEIBO
from Django import settings

from apps.oauth.utils import check_access_token, generate_access_token



class WeiboAuthURLView(View):
    def get(self, request):
        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        next = request.GET.get('next')
        print(next)

        # 获取weibo登录页面网址
        oauth = OAuth_WEIBO(client_id=settings.WEIBO_CLIENT_ID,
                            client_key=settings.WEIBO_CLIENT_SECRET,
                            redirect_url=settings.WEIBO_REDIRECT_URI,
                            state=next)
        # 微博登錄的地址 返回給前端
        login_url = oauth.get_auth_url()

        return JsonResponse({'code': 0, 'login_url': login_url, 'errmsg': "ok"})

class WeiboAuthUserView(View):
    #  /oauth_callback/?code=d72f30d2ff001c88ab7ea132ee46f5ad
    def get(self, request):
        """Oauth2.0认证"""

        # access_token 通过code获取的,  access_token唯一标识当前用户
        code = request.GET.get('code')
        oauth = OAuth_WEIBO(client_id=settings.WEIBO_CLIENT_ID,
                            client_key=settings.WEIBO_CLIENT_SECRET,
                            redirect_url=settings.WEIBO_REDIRECT_URI, )
        access_token = oauth.get_access_token(code)

        print(access_token)

        # 3 去数据表中根据获取的access_token查数据，如果查到了 说明绑定过了 直接返回信息（已经绑定）
        try:
            oauth_user = OAuthWEIBOUser.objects.get(access_token=access_token)
        except Exception as e:
            print(e)
            # 查询不到 未绑定 返回数据
            access_token = generate_access_token(access_token)
            print(access_token, 'jiami')
            return JsonResponse({'code': 1, 'access_token': access_token})
        else:
            # 没有异常  查到数据库
            # 登录状态保持
            login(request, oauth_user.user)
            # 在cookie里存一个username
            response = JsonResponse({'code': 0, 'errmsg': "ok"})
            response.set_cookie("username", oauth_user.user.username)

            return response

        # 处理账号的绑定

    def post(self, request):
        # password: this.password,
        # mobile: this.mobile,
        # sms_code: this.sms_code,
        # access_token: this.access_token
        # 1 接收 用户绑定信息
        body = request.body
        data_dict = json.loads(body)
        mobile = data_dict.get('mobile')
        password = data_dict.get('password')
        sms_code = data_dict.get('sms_code')
        access_token = data_dict.get('access_token')

        # 2 校验
        if not all([mobile, password, sms_code, access_token]):
            return JsonResponse({'code': 505, 'errmsg': "信息不全"})
        # 正则

        # 3 判断手机号之前有没有注册过
        try:
            from apps.users.models import User
            users = User.objects.filter(mobile=mobile)
            if not users:  # 账户不存在  就直接注册成新的账户
                user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
            else:
                # 账户存在
                user = users[0]
                if not user.check_password(password):  # 密码校验
                    return JsonResponse({'code': 101, 'errmsg': "密码错误"})

        except Exception as e:
            print(e)
            return JsonResponse({'code': 404, 'errmsg': "网络异常"})

        # 绑定
        try:
            # jiemi
            access_token = check_access_token(access_token)
            print('access_token', access_token)
            OAuthWEIBOUser.objects.create(user=user, access_token=access_token)
        except Exception as e:
            # 网络可能异常
            # 已经绑定过了
            return JsonResponse({'code': 400, 'errmsg': "账号已经绑定，无法添加"})

        # 登录状态保持
        login(request, user)

        # 在cookie里存一个username
        response = JsonResponse({'code': 0, 'errmsg': "ok"})
        response.set_cookie("username", user.username)

        return response
