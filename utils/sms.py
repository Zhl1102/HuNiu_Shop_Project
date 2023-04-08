"""
    对接第三方短信接口
"""
import requests
import time
import base64
import hashlib
import random

class YunTongXunAPI:

    def __init__(self, account_sid, auth_token, app_id, template_id):
        """

        :param account_sid: 账户id
        :param auth_token: 授权令牌
        :param app_id: 应用id
        :param template_id: 模版短信id
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.app_id = app_id
        self.template_id = template_id

    def get_url(self):
        """
        获取请求的url地址
        :return:
        """
        return f"https://app.cloopen.com:8883/2013-12-26/Accounts/{self.account_sid}/SMS/TemplateSMS?sig={self.get_sig()}"

    def get_headers(self):
        """
        获取请求头
        :return:
        """
        s = self.account_sid + ':' +  time.strftime("%Y%m%d%H%M%S")
        auth = base64.b64encode(s.encode()).decode()

        return {
            "Accept": "application/json",
            "Content-Type": "application/json;charset=utf-8",
            # "Content-Length": 256,
            "Authorization": auth,
        }

    def get_body(self, phone, code):
        """
        获取请求体
        :return:
        """
        return {
            "to": phone,
            "appId": self.app_id,
            "templateId": self.template_id,
            "datas": [code, '10']
        }

    def get_sig(self):
        """
        生成请求地址中的查询字符串sig
        :return:
        """
        s = self.account_sid + self.auth_token + time.strftime("%Y%m%d%H%M%S")
        m = hashlib.md5()
        m.update(s.encode())

        return m.hexdigest().upper()

    def run(self, phone, code):
        """
        程序入口函数
        :return:
        """
        url = self.get_url()
        headers = self.get_headers()
        data = self.get_body(phone, code)

        return requests.post(url=url, headers=headers, json=data).json()

if __name__ == '__main__':
    config = {
        "account_sid": "2c94811c870df4c801875bd0d1760c56",
        "auth_token": "1900fe58c2354ba8b4e236ce31c748f7",
        "app_id": "2c94811c870df4c801875bd0d26b0c5d",
        "template_id": "1",
    }
    ytx = YunTongXunAPI(**config)
    phone = "18847339790"
    code = random.randint(100000, 999999)
    print(code)
    print(ytx.run(phone, code))