from loguru import logger
import uvicorn
from fastapi import FastAPI, Request
from channel.feishu import FeishuChannel

app = FastAPI()


# 处理从alertmanager接收过来的信息
async def message_handler(message):
    message = eval(message)
    alerts = message["alerts"]
    alert_message = []
    # 多台机器的时候处理
    for i in range(len(alerts)):
        alert = alerts[i]
        alert = eval(str(alert))
        status = alert["status"]
        labels = alert["labels"]
        annotations = alert["annotations"]
        startsAt = alert["startsAt"]
        endsAt = alert["endsAt"]
        alertname = eval(str(labels))["alertname"]
        instance = eval(str(labels))["instance"]
        status = eval(str(labels))["status"]
        description = eval(str(annotations))["description"]
        message = "------------------------------" + '\n' \
                  + "           告警来了" + '\n' \
                  + "------------------------------" + '\n' \
                  + "状态: " + status + '\n' \
                  + "告警名字: " + alertname + '\n' \
                  + "告警实例: " + instance + '\n' \
                  + "告警等级: " + status + '\n' \
                  + "告警描述: " + description + '\n' \
                  + "开始时间: " + startsAt + '\n' \
                  + "结束时间: " + endsAt + '\n' \
                  + "------------------------------"
        alert_message.append(message)
    return alert_message


# alertmanager post请求处理函数
@app.post("/")
async def connect(request: Request):
    messages = await request.json()
    logger.debug(messages)
    try:
        messages = await message_handler(messages)
        for message in messages:
            feishu = FeishuChannel()
            await feishu.send_msg(message)
    except Exception as e:
        logger.debug(e)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
