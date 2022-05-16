import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

# /image_codes/4f6e4050-d273-4e5c-8d32-690e25faa887/
from django_redis import get_redis_connection
from redis import Redis
from ronglian_sms_sdk import SmsSDK

from celery_tasks.sms.tasks import send_sms_code
from libs.captcha.captcha import captcha
from utils.smsutils import SmsUtil


class ImageCodeView(View):

    def get(self, request, uuid):
        # - 1 接收前端请求  uuid
        #  - 2 生成验证码
        text, image = captcha.generate_captcha()
        print(text)

        #  - 3 用uuid为key 验证码为value 存到redis
        redis = get_redis_connection('code')
        # redis.set(uuid, text)
        # 验证码添加有效期  这个是300秒
        redis.setex(uuid, 300, text)
        #  - 4 把验证码的图片 返回给前端

        return HttpResponse(image, content_type='image/jpeg')


class SmsView(View):

    def get(self, request, mobile):
        # - 2 校验手机号格式是否正确
        if not mobile:
            return JsonResponse({'code': 300, "errmsg": "手机号为空"})
        # 正则验证
        # - 3 校验图片验证码是否正确
        # /sms_codes/15506373808/?image_code=wnqx&image_code_id=fdd7fe8e-9012-42a3-a535-205df14751ce
        # 用户发过来的图片验证码image_code
        image_code: str = request.GET.get('image_code')
        print('image_code', image_code)
        image_code_uuid = request.GET.get('image_code_id')
        try:
            # 获取保存都在redis里的图片验证码
            redis: Redis = get_redis_connection('code')
            print(redis)
            image_code_redis = redis.get(image_code_uuid)
            if not image_code_redis:
                return JsonResponse({'code': 400, "errmsg": "验证码过期"})

            image_code_redis = image_code_redis.decode()
            print('image_code_redis', image_code_redis)

            if image_code.lower() != image_code_redis.lower():
                return JsonResponse({'code': 500, "errmsg": "图片验证码错了"})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 600, "errmsg": "网络异常"})

        # - 4 给这个手机号发送短信  第三方
        print("发送短信给", mobile)

        # - 1 先 根据key: flag_手机号 ，获取值
        flag_send = redis.get('flag_%s' % mobile)

        # - 2 如果值存在 ，返回错误响应  过于频繁发送
        if flag_send:
            return JsonResponse({'code': 110, "errmsg": "短信已经发送，请稍后再试"})

        # - 3 如果不存在 就可以继续发送短信验证码

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        print('sms_code=', sms_code)

        # 同步发短信
        # SmsUtil().send_message(mobile=mobile, code=sms_code)

        # 异步发短信
        print('发短信111')
        send_sms_code.delay(mobile=mobile, code=sms_code)
        print('发短信222')

        # - 1创建redis的管道 pipline 对象
        pl = redis.pipeline()

        # - 2 把redis的操作请求 添加到管道
        pl.setex('smscode_%s' % mobile, 60 * 3, sms_code)
        pl.setex('flag_%s' % mobile, 120, 1)
        # - 3 执行所有操作
        pl.execute()
        # key  smscode_15512344321    value  1234   4321  5678
        # redis.setex('smscode_%s' % mobile, 60 * 3, sms_code)

        # - 4 发送完  保存  key: flag_手机号    value:1  有效期 60秒（和前端的倒计时一致）
        # redis.setex('flag_%s' % mobile, 120, 1)
        # - 5 返回响应0

        return JsonResponse({'code': 0, "errmsg": "ok"})
