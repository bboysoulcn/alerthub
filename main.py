from loguru import logger
import uvicorn
from fastapi import FastAPI, Request
from channel.feishu import FeishuChannel

app = FastAPI()


@app.post("/")
async def connect(request: Request):
    messages = await request.json()
    messages = messages["alerts"]
    try:
        for message in messages:
            print(message)
            feishu = FeishuChannel()
            await feishu.send_msg(message)
            return {"status": "ok"}
    except Exception as e:
        return {"status": "error"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
