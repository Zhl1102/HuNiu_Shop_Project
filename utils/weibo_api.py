"""
    第三方微博登录接口
"""
# 为url进行编码
from urllib.parse import urlencode

class OauthAPI:

    def __init__(self, app_key, app_secret, redirect_uri):
        self.app_key = app_key
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri    # 回调地址

    def get_grant_url(self):
        """
        获取微博授权登录页的url地址
        :return: url
        """
        params = {
            "client_id": self.app_key,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        return "https://api.weibo.com/oauth2/authorize?" + urlencode(params)

if __name__ == '__main__':
    config = {
        "app_key": "3329558176",
        "app_secret": "f0af13e26b8d2a27f91ce251a2ee1df6",
        "redirect_uri": "http://localhost:9999/huniushop/templates/callback.html",
    }
    api = OauthAPI(**config)
    print(api.get_grant_url())