import re
from datetime import datetime, timedelta

class ScheduleService:
    def __init__(self, trade_log):
        self.trade_log = trade_log

    def get_auto_schedule(self, now):
        auto_tickers = []
        auto_durations = []
        today = now.date()
        today_str = now.strftime('%Y-%m-%d')
        seen = set()

        for key in self.trade_log.data:
            match = re.match(r"([A-Z]+)_(\d{4}-\d{2}-\d{2})-\((\d+)\)", key)
            if match:
                ticker, start_str, n_str = match.groups()
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                n = int(n_str)
                if ticker in seen:
                    continue
                date_range = [start_date + timedelta(days=i) for i in range(n)]
                if today in date_range and f"{ticker}_{today_str}" not in self.trade_log.data:
                    auto_tickers.append(ticker)
                    auto_durations.append(n)
                    seen.add(ticker)

        return auto_tickers, auto_durations

    def print_schedule_before_trade(self, now):
        upcoming = {}

        for key in self.trade_log.data:
            match = re.match(r"([A-Z]+)_(\d{4}-\d{2}-\d{2})-\((\d+)\)", key)
            if match:
                ticker, start_str, n_str = match.groups()
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                n = int(n_str)
                remaining_dates = [start_date + timedelta(days=i) for i in range(n)]
                valid = [d for d in remaining_dates if d >= now.date()]
                if valid:
                    if ticker not in upcoming or max(valid) > max(upcoming[ticker]):
                        upcoming[ticker] = valid

        if upcoming:
            for t in sorted(upcoming):
                dates = ' '.join(d.strftime("%m.%d") for d in sorted(upcoming[t]))
                print(f"{t:<6}| {dates}")
        else:
            print("📝 새로운 거래를 시작해주세요")

    def print_schedule_after_trade(self, now):
        print("\n📊 남은 거래일정")
        schedule = {}
        completed = {}

        for key in self.trade_log.data:
            match = re.match(r"([A-Z]+)_(\d{4}-\d{2}-\d{2})-\((\d+)\)", key)
            if match:
                ticker, start_str, n_str = match.groups()
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                n = int(n_str)
                remaining_days = (start_date + timedelta(days=n - 1)) - now.date()
                if remaining_days.days > 0:
                    schedule[ticker] = remaining_days.days
                elif remaining_days.days == 0:
                    if n == 1:
                        completed[ticker] = self.get_final_n(ticker)
                    else:
                        schedule[ticker] = n

        max_token_len = max([len(t) for t in list(schedule.keys()) + list(completed.keys())] + [4])

        if completed:
            for t in sorted(completed):
                print(f"🎉 {t:<{max_token_len}} | {completed[t]}일 연속 거래 완료")

        if completed and schedule:
            print()

        if schedule:
            for t in sorted(schedule):
                print(f"⏳ {t:<{max_token_len}} | {schedule[t]}일 남음")
        elif not completed:
            print("📝 새로운 거래를 시작해주세요")

        return {**schedule, **completed}

    def get_final_n(self, ticker):
        max_n = 0
        for key in self.trade_log.data:
            match = re.match(rf"{ticker}_(\d{{4}}-\d{{2}}-\d{{2}})-\((\d+)\)", key)
            if match:
                _, n_str = match.groups()
                max_n = max(max_n, int(n_str))
        return max_n

    def all_latest_n_values_are_1(self):
        latest_n_per_ticker = {}

        for key in self.trade_log.data:
            match = re.match(r"([A-Z]+)_(\d{4}-\d{2}-\d{2})-\((\d+)\)", key)
            if match:
                ticker, date_str, n_str = match.groups()
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                n = int(n_str)

                if ticker not in latest_n_per_ticker or date > latest_n_per_ticker[ticker]["date"]:
                    latest_n_per_ticker[ticker] = {"date": date, "n": n}

        return all(info["n"] == 1 for info in latest_n_per_ticker.values())

    def check_trade_records(self, now):
        for key in self.trade_log.data:
            match = re.match(r"([A-Z]+)_(\d{4}-\d{2}-\d{2})-\((\d+)\)", key)
            if match:
                ticker, start_str, n_str = match.groups()
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                n = int(n_str)
                active_days = [start_date + timedelta(days=i) for i in range(n)]
                if now.date() in active_days:
                    return True
        return False 