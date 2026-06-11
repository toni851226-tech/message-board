import httpx
import logging
from datetime import datetime, timezone, timedelta
from config import APPS_SCRIPT_URL, RECIPIENT_EMAIL

SOURCE_LABELS = {"voice": "語音輸入", "text": "文字輸入"}
TPE = timezone(timedelta(hours=8))
logger = logging.getLogger(__name__)


async def send_message_email(sender_name: str, ai_content: str, source: str, created_at: datetime):
    source_label = SOURCE_LABELS.get(source, source)
    # 確保以台灣時間（UTC+8）顯示，無論傳入的是 naive UTC 還是有時區的 datetime
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc).astimezone(TPE)
    else:
        created_at = created_at.astimezone(TPE)
    time_str = created_at.strftime("%Y/%m/%d %H:%M")

    subject = f"📬 {sender_name} 留言給您｜{time_str}"

    body = f"""您好，

{sender_name} 在您請假期間留下了一則留言：

──────────────────────
留言者：{sender_name}
時　間：{time_str}
方　式：{source_label}
──────────────────────

{ai_content}

──────────────────────
此郵件由辦公室留言系統自動發送"""

    logger.info("Sending email via GAS url=...%s to=%s subject=%s",
                APPS_SCRIPT_URL[-20:], RECIPIENT_EMAIL, subject)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            APPS_SCRIPT_URL,
            json={
                "to": RECIPIENT_EMAIL,
                "subject": subject,
                "body": body,
            },
            timeout=30,
            follow_redirects=True,
        )
    logger.info("GAS response status: %s, body: %s", response.status_code, response.text[:200])
    response.raise_for_status()
