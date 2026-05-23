import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL

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

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
