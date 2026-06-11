import os
import asyncio
import logging
import traceback
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx

from database import init_db, save_message, update_ai_content
from ai_service import format_message
from email_service import send_message_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TAIWAN_TZ = timezone(timedelta(hours=8))
PUBLIC_URL = os.environ.get("PUBLIC_URL", "").rstrip("/")


async def _keep_alive():
    """每 10 分鐘 ping 自己，防止 Render 免費方案 15 分鐘後 sleep。"""
    if not PUBLIC_URL:
        return
    await asyncio.sleep(300)  # 第一次先等 5 分鐘再開始
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.get(f"{PUBLIC_URL}/api/health", timeout=10)
        except Exception:
            pass
        await asyncio.sleep(600)  # 每 10 分鐘 ping 一次


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    asyncio.create_task(_keep_alive())
    yield


app = FastAPI(lifespan=lifespan)


class MessageRequest(BaseModel):
    sender_name: str
    content: str
    source: str  # 'voice' or 'text'


@app.post("/api/messages")
async def create_message(req: MessageRequest):
    if not req.sender_name.strip():
        raise HTTPException(status_code=400, detail="請填寫姓名")
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="請填寫留言內容")
    if req.source not in ("voice", "text"):
        raise HTTPException(status_code=400, detail="無效的留言方式")

    message_id = save_message(req.sender_name.strip(), req.content.strip(), req.source)

    ai_content = format_message(req.sender_name.strip(), req.content.strip(), req.source)
    update_ai_content(message_id, ai_content)

    now = datetime.now(tz=TAIWAN_TZ)
    try:
        send_message_email(req.sender_name.strip(), ai_content, req.source, now)
    except Exception as exc:
        logger.error("send_message_email failed: %s\n%s", exc, traceback.format_exc())

    return {"status": "ok"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
