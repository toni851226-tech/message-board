import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]
RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
