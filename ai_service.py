import httpx
from config import GEMINI_API_KEY

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

SOURCE_LABELS = {"voice": "語音輸入", "text": "文字輸入"}


def format_message(sender_name: str, content: str, source: str) -> str:
    source_label = SOURCE_LABELS.get(source, source)
    prompt = f"""你是一個辦公室留言助理。訪客在員工請假期間留下以下留言（可能來自語音辨識，有錯字或語句不順）。
請修正錯誤、整理成通順的中文，保留完整語意。只輸出整理後的留言本文，不要加任何說明或前綴。

留言者：{sender_name}
留言方式：{source_label}
原始內容：{content}"""

    response = httpx.post(
        GEMINI_URL,
        params={"key": GEMINI_API_KEY},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
