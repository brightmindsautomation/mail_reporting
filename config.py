# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Automatically loads .env

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Default port
RECIPIENT_EMAILS = os.getenv("RECIPIENT_EMAILS", "").split(",")
FILE_PATH = os.getenv("FILE_PATH")
