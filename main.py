from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database import init_db, save_message, update_ai_content
from ai_service import format_message
from email_service import send_message_email

app = FastAPI()

init_db()


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

    now = datetime.now()
    send_message_email(req.sender_name.strip(), ai_content, req.source, now)

    return {"status": "ok"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
