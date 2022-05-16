import json

from ronglian_sms_sdk import SmsSDK


class SmsUtil:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.smsSdk = SmsSDK(accId='8aaf07087de13e49017df66ef9910411',
                                accToken='ab7ee364f6a54e1487aeecb502de4429',
                                appId='8aaf07087de13e49017df66efa900418')

        return cls.__instance

    def send_message(self, mobile='17857658376', tid='1', code='1234'):

        sendback = self.smsSdk.sendMessage(tid=tid, mobile=mobile, datas=(code, 5))
        # 把返回值转为字典
        sendback = json.loads(sendback)
        # "statusCode": "000000"
        if sendback.get("statusCode") == "000000":
            print("发送成功")
        else:
            print("发送失败")