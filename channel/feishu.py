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

    async def send_msg(self, alert):
        # 多台机器的时候处理
        status = alert["status"]
        alertname = alert["labels"]["alertname"]
        instance = alert["labels"]["instance"]
        severity = alert["labels"]["severity"]
        description = alert["annotations"]["description"]
        summary = alert["annotations"]["summary"]
        startsAt = alert["startsAt"]
        endsAt = alert["endsAt"]
        message = f"🚨**告警名称**: {alertname}\n" \
                  f"📌**告警状态**:  {status}\n" \
                  f"📍**告警实例**:  {instance}\n" \
                  f"⚠️**告警等级**:  {severity}\n" \
                  f"⏰**开始时间**:  {startsAt}\n" \
                  f"⏳**结束时间**:  {endsAt}\n" \
                  f"📋**告警摘要**:  {summary}\n" \
                  f"📝**告警描述**:  {description}\n"

        if status == "firing":
            template = "red"
            title_content = "🚨  告警来了  🚨"
        elif status == "resolved":
            template = "green"
            title_content = "✅  告警恢复  ✅"
        else:
            template = "blue"
            title_content = "不知道是什么状态的告警"

        timestamp = int(time.time())
        # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, self.sign)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        headers = {'Content-Type': 'application/json;charset=utf-8'}

        body = {
            "msg_type": "interactive",
            "timestamp": timestamp,
            "sign": sign,
            "card": {
                "elements": [
                    {
                        "tag": "markdown",
                        "content": message
                    },
                    {
                        "tag": "hr"
                    }
                ],
                "header": {
                    "template": template,
                    "title": {
                        "content": title_content,
                        "tag": "plain_text"
                    }
                }
            }
        }
        httpx.post(self.bot_url, json=body, headers=headers)
