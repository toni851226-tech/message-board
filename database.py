import sqlite3
from datetime import datetime

DB_PATH = "messages.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_name  TEXT NOT NULL,
                raw_content  TEXT NOT NULL,
                ai_content   TEXT,
                source       TEXT NOT NULL,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_message(sender_name: str, raw_content: str, source: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO messages (sender_name, raw_content, source) VALUES (?, ?, ?)",
            (sender_name, raw_content, source),
        )
        conn.commit()
        return cursor.lastrowid


def update_ai_content(message_id: int, ai_content: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE messages SET ai_content = ? WHERE id = ?",
            (ai_content, message_id),
        )
        conn.commit()
