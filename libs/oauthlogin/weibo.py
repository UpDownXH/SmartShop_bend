import json
import urllib.parse


class OAuth_Base(object):  # 基类，将相同的方法写入到此类中
    def __init__(self, client_id, client_key, redirect_url, state=None):  # 初始化，载入对应的应用id、秘钥和回调地址
        self.client_id = client_id
        self.client_key = client_key
        self.redirect_url = redirect_url
        self.state = state

    def _get(self, url, data):  # get方法
        request_url = '%s?%s' % (url, urllib.parse.urlencode(data))
        response = urllib.request.urlopen(request_url)
        return response.read()

    def _post(self, url, data):  # post方法
        request = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(encoding='UTF8'))  # 1
        response = urllib.request.urlopen(request)
        return response.read()


# 微博类
class OAuth_WEIBO(OAuth_Base):
    def get_auth_url(self):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_url,
            # 'scope':'email',
            'state': self.state
        }
        url = 'https://api.weibo.com/oauth2/authorize?%s' % urllib.parse.urlencode(params)
        return url

    def get_access_token(self, code):
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_key,
            'code': code,
            'redirect_uri': self.redirect_url
        }
        response = self._post('https://api.weibo.com/oauth2/access_token', params)
        result = json.loads(response.decode('utf-8'))
        self.access_token = result["access_token"]
        # self.openid = result["uid"]
        return self.access_token


if __name__ == '__main__':
    oauth = OAuth_WEIBO(client_id='1319853025',
                        client_key='23d5c0f50c838585a8d8b23259318e29',
                        redirect_url='http://www.meiduo.com:8080/oauth_callback.html',
                        )
    login_url = oauth.get_auth_url()
    print(login_url)
