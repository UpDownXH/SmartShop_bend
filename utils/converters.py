# 用户名验证的转换器
class UsernameConverter:
    regex = '[a-zA-Z0-9]{5,20}'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)

class MobileConverter:
    """自定义路由转换器去匹配手机号"""
    # 定义匹配手机号的正则表达式
    regex = '1[3-9]\d{9}'

    def to_python(self, value):
        # to_python：将匹配结果传递到视图内部时使用
        return str(value)

class UUIDConverter:
    """自定义路由转换器去匹配uuid"""
    # 定义UUID的正则表达式
    regex = '[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
