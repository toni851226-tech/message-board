import os
import asyncio
import logging
import traceback
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator

import httpx

from database import init_db, save_message, update_ai_content
from ai_service import format_message
from email_service import send_message_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TAIWAN_TZ = timezone(timedelta(hours=8))
PORT = int(os.environ.get("PORT", 8000))


async def _keep_alive():
    """每 8 分鐘 ping 自己，防止 Render 免費方案 15 分鐘後 sleep。
    直接 ping localhost，不依賴 PUBLIC_URL 環境變數。"""
    await asyncio.sleep(60)   # 啟動後 1 分鐘再開始（等 server 完全就緒）
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.get(f"http://localhost:{PORT}/api/health", timeout=10)
            logger.debug("keep-alive ping sent")
        except Exception as e:
            logger.warning("keep-alive ping failed: %s", e)
        await asyncio.sleep(480)  # 每 8 分鐘（遠低於 Render 15 分鐘門檻）


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(_keep_alive())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(lifespan=lifespan)


class MessageRequest(BaseModel):
    sender_name: str
    content: str
    source: str  # 'voice' or 'text'

    @validator("sender_name")
    def name_length(cls, v):
        v = v.strip()
        if len(v) > 50:
            raise ValueError("姓名不得超過 50 個字")
        return v

    @validator("content")
    def content_length(cls, v):
        v = v.strip()
        if len(v) > 2000:
            raise ValueError("留言內容不得超過 2000 個字")
        return v


@app.post("/api/messages")
async def create_message(req: MessageRequest):
    if not req.sender_name.strip():
        raise HTTPException(status_code=400, detail="請填寫姓名")
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="請填寫留言內容")
    if req.source not in ("voice", "text"):
        raise HTTPException(status_code=400, detail="無效的留言方式")

    message_id = save_message(req.sender_name.strip(), req.content.strip(), req.source)

    # Gemini 失敗時 fallback 到原始內容，email 仍正常寄出
    ai_content = await format_message(req.sender_name.strip(), req.content.strip(), req.source)
    update_ai_content(message_id, ai_content)

    now = datetime.now(tz=TAIWAN_TZ)
    try:
        await send_message_email(req.sender_name.strip(), ai_content, req.source, now)
    except Exception as exc:
        logger.error("send_message_email failed: %s\n%s", exc, traceback.format_exc())
        # Email 失敗時告知訪客，讓其可重試（不要默默丟失留言）
        raise HTTPException(
            status_code=500,
            detail="留言儲存成功，但通知信件傳送失敗，請再試一次或直接致電聯繫。"
        )

    return {"status": "ok"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
