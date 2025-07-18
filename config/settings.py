import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITHUMB_API_KEY")
SECRET_KEY = os.getenv("BITHUMB_SECRET_KEY")
API_URL = "https://api.bithumb.com"
API_URL_V1 = f"{API_URL}/v1"

PAYMENT_CURRENCY = "KRW"
BUY_AMOUNT_KRW = 5100

LOG_FILE = "trade_log.json"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137.0.0.0 Safari/537.36" 