from itsdangerous import TimedJSONWebSignatureSerializer as TimeSerializer
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings

def generate_verify_email_url(user):
    """
    生成邮箱验证链接
    :param user: 当前登录用户
    :return: verify_url
    """
    serializer = TimeSerializer(settings.SECRET_KEY, expires_in=600)
    # 组装加密的数据
    data = {'user_id': user.id}
    # 把data加密  转为字符串
    token = serializer.dumps(data).decode()
    # 把链接地址后面拼接上加密的数据
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url


def check_verify_email_token(token):
    """
    验证token并提取user
    :param token: 用户信息签名后的结果
    :return: user, None
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=600)
    try:
        data = serializer.loads(token)
    except BadData:
        print("获取用户数据失败，激活邮件过期")
        return None
    else:
        user_id = data.get('user_id')
        return user_id