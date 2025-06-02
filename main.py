import time
from datetime import datetime

from src.api.bithumb_api import BithumbAPI
from src.crawler.notice_crawler import NoticeCrawler
from src.models.trade_log import TradeLog
from src.services.trading_service import TradingService
from src.services.schedule_service import ScheduleService
from src.utils.display_utils import DisplayUtils
from config.settings import API_KEY, SECRET_KEY

def execute_trading_cycle(now, api, trade_log, trading_service, schedule_service, notice_crawler, display_utils):
    print(f"\n🕐 {now.strftime('%Y-%m-%d %H:%M')} 자동 루프 실행됨\n")
    
    display_utils.display_progress_bar()
    notices = notice_crawler.get_notices(open_browser=True)
    
    if notices:
        print("\n📊남은 거래일정")
        schedule_service.print_schedule_before_trade(now)
        if not display_utils.handle_user_input(now, trading_service, trade_log):
            display_utils.print_waiting_message()
            return True
    else:
        print("\n📊남은 거래일정")
        schedule_service.print_schedule_before_trade(now)
        
        tickers, durations = schedule_service.get_auto_schedule(now)
        
        if tickers:
            print("\n🚀오토 트레이딩 시작\n")
            trading_service.process_trades(tickers, durations, now)
            print("\n✅ 오늘 모든 티커 거래 완료")
            print("\n✅ 오토 트레이딩 스케줄 없음")

            after_schedule = schedule_service.print_schedule_after_trade(now)
            has_only_completed = all(v == "완료" for v in after_schedule.values())

            if schedule_service.all_latest_n_values_are_1():
                print("\n📆 다음 스케줄이 없습니다")
            else:
                print(f"\n📆 다음 거래는 {(now + timedelta(days=1)).strftime('%m월 %d일')} 00시 00분 부터 가능합니다")
            
            display_utils.print_waiting_message()
        else:
            if not schedule_service.check_trade_records(now):
                if not display_utils.handle_user_input(now, trading_service, trade_log):
                    display_utils.print_waiting_message()
                    return True
            else:
                print("\n✅ 오늘 모든 티커 거래 완료")
                print("\n✅ 오토 트레이딩 스케줄 없음")
            
            display_utils.print_waiting_message()
    
    return True

def main():
    try:
        api = BithumbAPI(API_KEY, SECRET_KEY)
        trade_log = TradeLog()
        trading_service = TradingService(api, trade_log)
        schedule_service = ScheduleService(trade_log)
        notice_crawler = NoticeCrawler()
        display_utils = DisplayUtils()
        
        now = datetime.now()
        if not execute_trading_cycle(now, api, trade_log, trading_service, schedule_service, notice_crawler, display_utils):
            return
        
        while True:
            try:
                time.sleep(1800)  # 30분 대기
                
                now = datetime.now()
                if not execute_trading_cycle(now, api, trade_log, trading_service, schedule_service, notice_crawler, display_utils):
                    return
                
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                return
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        return

if __name__ == "__main__":
    main() 