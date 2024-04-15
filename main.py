from loguru import logger
import uvicorn
from fastapi import FastAPI, Request
from channel.feishu import FeishuChannel

app = FastAPI()


# 处理从alertmanager接收过来的信息
async def message_handler(message):
    alerts = message["alerts"]
    alert_message = []
    # 多台机器的时候处理
    for alert in alerts:
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
    alert_message.append(message)
    return alert_message


# alertmanager post请求处理函数
@app.post("/")
async def connect(request: Request):
    messages = await request.json()
    try:
        messages = await message_handler(messages)
        for message in messages:
            print(message)
            feishu = FeishuChannel()
            await feishu.send_msg(message)
            return {"status": "ok"}
    except Exception as e:
        return {"status": "error"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
