import time
from datetime import datetime, timedelta
from config.settings import PAYMENT_CURRENCY, BUY_AMOUNT_KRW

class TradingService:
    def __init__(self, api, trade_log):
        self.api = api
        self.trade_log = trade_log

    def process_trades(self, tickers, durations, now, is_user_input=False):
        today = now.date()
        today_str = now.strftime('%Y-%m-%d')
        traded_count = 0
        
        for t, d in zip(tickers, durations):
                                                
            if f"{t}_{today_str}" in self.trade_log.data:
                print(f"⏩ {t} 이미 거래됨")
                continue

            if is_user_input:
                new_key = f"{t}_{today_str}-({d})"
                new_day_key = f"{t}_{today_str}"
                print()
                success = self.run_bot(t, new_key, now)
                if success:
                    self.trade_log.update(t, now, d)
                    traded_count += 1
            else:
                latest_key, latest_date, latest_n = self.trade_log.get_latest_schedule(t)
                if not latest_key:
                    print(f"❌ {t} 스케줄 없음 - 자동매매 대상 제외")
                    continue

                active_days = [latest_date + timedelta(days=i) for i in range(latest_n)]
                if today not in active_days:
                    print(f"⏩ {t} 오늘은 자동매매 스케줄 아님")
                    continue

                days_passed = (today - latest_date).days
                remaining_n = latest_n - days_passed
                if remaining_n <= 0:
                    print(f"⏩ {t} 자동매매 기간 종료")
                    continue

                new_key = f"{t}_{today_str}-({remaining_n})"
                new_day_key = f"{t}_{today_str}"
                success = self.run_bot(t, new_key, now)
                if success:
                    self.trade_log.update(t, now, remaining_n)
                    traded_count += 1
        
        print(f"\n🔍 거래 완료된 티커 수: {traded_count}")
        return traded_count > 0

    def run_bot(self, ticker, key, now):
        while True:
            print(f"{ticker}/KRW 매매 시작")
            orderbook = self.api.get_orderbook(ticker, PAYMENT_CURRENCY)
            if not orderbook:
                print("호가 정보 불러오기 실패")
                return False

            sell_price = float(orderbook['asks'][0]['price'])
            buy_price = float(orderbook['bids'][0]['price'])

            if sell_price - buy_price < 0.01:
                print("틱 차이 너무 적음. 재시도.")
                time.sleep(1)
                continue          

            krw_balance = self.api.get_balance("KRW")
            if krw_balance is None or krw_balance < BUY_AMOUNT_KRW:
                print("잔고 부족 또는 불러오기 실패")
                return False

            units = round(BUY_AMOUNT_KRW / sell_price, 4)
            if units < 0.0001:
                print("최소 매수 단위 미달")
                return False

            print(f"[매수] {sell_price}원에 {units}개 지정가 주문")
            buy_result = self.api.place_order(ticker, PAYMENT_CURRENCY, units, "bid", "limit", price_to_send=sell_price)
            if not buy_result or 'uuid' not in buy_result:
                print("매수 실패:", buy_result)
                return False

            print("⏳ 매도 체결 대기 중...")
            for _ in range(10):
                time.sleep(1)
                coin_bal = self.api.get_balance(ticker)
                if isinstance(coin_bal, float) and coin_bal >= units:
                    available = round(coin_bal, 4)
                    print(f"[매도] 시장가로 {available}개 매도")
                    sell_result = self.api.place_order(ticker, PAYMENT_CURRENCY, available, "ask", "market")
                    if sell_result and 'uuid' in sell_result:
                        print("✅ 시장가 매도 완료")
                        return True
                    else:
                        print("❌ 시장가 매도 실패:", sell_result)
                        return False
                print("잔고 반영 대기 중...")
            print("❌ 10초 내 매수 체결되지 않아 매도 생략")
            return False 