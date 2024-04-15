import httpx
import hashlib
import base64
import hmac
import time
import os


class FeishuChannel:
    def __init__(self):
        self.bot_url = os.getenv("FEISHU_BOT_URL")
        self.sign = os.getenv("FEISHU_SIGN")

    async def send_msg(self, message):
        timestamp = int(time.time())
        # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, self.sign)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        body = {
            "msg_type": "text",
            "timestamp": timestamp,
            "sign": sign,
            "content": {
                "text": message
            }
        }
        httpx.post(self.bot_url, json=body, headers=headers)
