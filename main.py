import time
from datetime import datetime, timedelta

from src.api.bithumb_api import BithumbAPI
from src.crawler.notice_crawler import NoticeCrawler
from src.models.trade_log import TradeLog
from src.services.trading_service import TradingService
from src.services.schedule_service import ScheduleService
from src.utils.display_utils import DisplayUtils
from config.settings import API_KEY, SECRET_KEY

def execute_trading_cycle(now, api, trade_log, trading_service, schedule_service, notice_crawler, display_utils, is_reservation=False):
    if not is_reservation:
        print(f"\n🕐 {now.strftime('%Y-%m-%d %H:%M')} 자동 루프 실행됨\n")
    
    try:
                        
        reservation_info = display_utils.check_reservation(now)
        if reservation_info:
            print(f"\n🎯 예약된 거래를 실행합니다!")
            print(f"⏰ 예약 시간: {reservation_info['time'].strftime('%Y-%m-%d %H:%M')}")
            print(f"🎯 거래 티커: {', '.join(reservation_info['tickers'])}")
            print(f"📅 거래 기간: {', '.join(map(str, reservation_info['durations']))}일")
            
                       
            trading_service.process_trades(
                reservation_info['tickers'], 
                reservation_info['durations'], 
                now, 
                is_user_input=True
            )
            print("\n✅ 예약된 거래가 완료되었습니다.\n")
            return True
        
        display_utils.display_progress_bar()
        notices = notice_crawler.get_notices(open_browser=True)
        
                  
        if notices:
                                         
            if not hasattr(execute_trading_cycle, 'last_notice_time') or \
               (now - execute_trading_cycle.last_notice_time).total_seconds() > 1800:
                execute_trading_cycle.last_notice_time = now
                print("\n📊 남은 거래일정")
                schedule_service.print_schedule_before_trade(now)
                if not display_utils.handle_user_input(now, trading_service, trade_log):
                    display_utils.print_waiting_message()
                    return True
                print("\n📊 남은 거래일정")
                schedule_service.print_schedule_after_trade(now)
                if schedule_service.all_latest_n_values_are_1():
                    print("\n📆 다음 스케줄이 없습니다")
                else:
                    print(f"\n📆 다음 거래는 {(now + timedelta(days=1)).strftime('%m월 %d일')} 00시 00분 부터 가능합니다")
                display_utils.print_waiting_message()
                return True
            else:
                                           
                print("\n📊 남은 거래일정")
                schedule_service.print_schedule_before_trade(now)
                
                tickers, durations = schedule_service.get_auto_schedule(now)
                
                if tickers:
                    print("\n🚀 오토 트레이딩 시작\n")
                    if not trading_service.process_trades(tickers, durations, now):
                                                   
                        if not display_utils.handle_user_input(now, trading_service, trade_log):
                            display_utils.print_waiting_message()
                            return True
                    else:
                        print("\n✅ 오늘 모든 티커 거래 완료")
                else:
                    if not schedule_service.check_trade_records(now):
                        if not display_utils.handle_user_input(now, trading_service, trade_log):
                            display_utils.print_waiting_message()
                            return True
                    else:
                        print("\n✅ 오늘 모든 티커 거래 완료")
                
                print("\n📊 남은 거래일정")
                schedule_service.print_schedule_after_trade(now)
                
                if schedule_service.all_latest_n_values_are_1():
                    print("\n📆 다음 스케줄이 없습니다")
                else:
                    print(f"\n📆 다음 거래는 {(now + timedelta(days=1)).strftime('%m월 %d일')} 00시 00분 부터 가능합니다")
                
                display_utils.print_waiting_message()
                return True
        else:
                                   
            print("\n📊 남은 거래일정")
            schedule_service.print_schedule_before_trade(now)
            
            tickers, durations = schedule_service.get_auto_schedule(now)
            
            if tickers:
                print("\n🚀 오토 트레이딩 시작\n")
                if not trading_service.process_trades(tickers, durations, now):
                                               
                    if not display_utils.handle_user_input(now, trading_service, trade_log):
                        display_utils.print_waiting_message()
                        return True
                else:
                    print("\n✅ 오늘 모든 티커 거래 완료")
            else:
                if not schedule_service.check_trade_records(now):
                    if not display_utils.handle_user_input(now, trading_service, trade_log):
                        display_utils.print_waiting_message()
                        return True
                else:
                    print("\n✅ 오늘 모든 티커 거래 완료")
            
            print("\n📊 남은 거래일정")
            schedule_service.print_schedule_after_trade(now)
            
            if schedule_service.all_latest_n_values_are_1():
                print("\n📆 다음 스케줄이 없습니다")
            else:
                print(f"\n📆 다음 거래는 {(now + timedelta(days=1)).strftime('%m월 %d일')} 00시 00분 부터 가능합니다")
            
            display_utils.print_waiting_message()
        return True
    except Exception as e:
        print(f"\n⚠️ 오류 발생: {str(e)}")
        print("30분 후 다시 시도합니다.")
        return True

def get_next_check_time(now, display_utils, is_reservation_executed=False):
    """다음 확인 시간을 계산합니다."""
                    
    active_reservations = display_utils.reservation_log.get_active_reservations(now)
    
    if active_reservations and not is_reservation_executed:
                                          
        return now + timedelta(seconds=10)
    else:
                                       
        return now + timedelta(minutes=30)

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
        
                     
        next_check_time = get_next_check_time(now, display_utils)
        
        while True:
            try:
                now = datetime.now()
                
                                
                active_reservations = display_utils.reservation_log.get_active_reservations(now)
                
                if active_reservations:
                                   
                    print(f"\n⏰ 예약된 일정 실행")
                    if not execute_trading_cycle(now, api, trade_log, trading_service, schedule_service, notice_crawler, display_utils, is_reservation=True):
                        return
                    
                                                      
                    next_check_time = get_next_check_time(now, display_utils, is_reservation_executed=True)
                elif now >= next_check_time:
                                       
                    if not execute_trading_cycle(now, api, trade_log, trading_service, schedule_service, notice_crawler, display_utils):
                        return
                    
                                  
                    next_check_time = get_next_check_time(now, display_utils)
                
                                      
                wait_seconds = min(60, (next_check_time - now).total_seconds())
                if wait_seconds > 0:
                    time.sleep(wait_seconds)
                
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                return
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        return

if __name__ == "__main__":
    main() 