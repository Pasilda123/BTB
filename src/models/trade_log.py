import os
import json
from datetime import datetime
from config.settings import LOG_FILE
import re

class TradeLog:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file
        self.data = self.load()

    def load(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        return {}

    def save(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def update(self, ticker, now, remaining_days):
        date_str = now.strftime("%Y-%m-%d")
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # 기본 키
        base_key = f"{ticker}_{date_str}"
        self.data[base_key] = timestamp

        # 남은 일수용 키
        n_key = f"{ticker}_{date_str}-({remaining_days})"
        self.data[n_key] = timestamp

        self.save()
        return self.data

    def get_latest_schedule(self, ticker):
        latest_key = None
        latest_date = None
        latest_n = None

        for key in self.data:
            match = re.match(rf"{ticker}_(\d{{4}}-\d{{2}}-\d{{2}})-\((\d+)\)", key)
            if match:
                start_str, n_str = match.groups()
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                if not latest_date or start_date > latest_date:
                    latest_date = start_date
                    latest_n = int(n_str)
                    latest_key = key

        return latest_key, latest_date, latest_n 