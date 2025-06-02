import os
from dotenv import load_dotenv

load_dotenv()

# API 설정
API_KEY = os.getenv("BITHUMB_API_KEY")
SECRET_KEY = os.getenv("BITHUMB_SECRET_KEY")
API_URL = "https://api.bithumb.com"
API_URL_V1 = f"{API_URL}/v1"

# 거래 설정
PAYMENT_CURRENCY = "KRW"
BUY_AMOUNT_KRW = 5100

# 파일 설정
LOG_FILE = "trade_log.json"

# 브라우저 설정
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137.0.0.0 Safari/537.36" 