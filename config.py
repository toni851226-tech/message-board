import os
from dotenv import load_dotenv

load_dotenv()

CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
