import httpx
from datetime import datetime
from config import APPS_SCRIPT_URL, RECIPIENT_EMAIL

SOURCE_LABELS = {"voice": "語音輸入", "text": "文字輸入"}


def send_message_email(sender_name: str, ai_content: str, source: str, created_at: datetime):
    source_label = SOURCE_LABELS.get(source, source)
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

    response = httpx.post(
        APPS_SCRIPT_URL,
        json={
            "to": RECIPIENT_EMAIL,
            "subject": subject,
            "body": body,
        },
        timeout=30,
    )
    response.raise_for_status()
