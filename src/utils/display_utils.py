import time
import sys
import os
from datetime import datetime, timedelta
from src.models.reservation_log import ReservationLog

if os.name == 'nt':           
    import msvcrt
else:               
    import termios
    import tty

class DisplayUtils:
    def __init__(self):
        self.reservation_log = ReservationLog()

    @staticmethod
    def display_progress_bar():
        print("\n📱 최신 에어드랍 공지 확인 중...")
        for i in range(26):
            bar = '█' * i + ' ' * (25 - i)
            print(f"\r[{bar}] {int(i / 25 * 100)}%", end='', flush=True)
            time.sleep(0.04)
        print("\r[██████████████████████████████] 100%")

    @staticmethod
    def print_waiting_message():
        divider = "─" * 30
        print("\n\n🕐 30분 후 공지를 다시 확인합니다")
        print("🔄 프로그램을 종료하려면 Ctrl+C를 누르세요")
        print("\033[?25l", end="")
        print(f"\n{divider} Made by Pasilda")

    @staticmethod
    def get_char():
        if os.name == 'nt':           
            return msvcrt.getch()
        else:               
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    def handle_user_input(self, now, trading_service, trade_log):
        print("\n")
        print("⏰ 예약 거래를 설정하시겠습니까? (Y/N)")
        print("Y: 예약 거래 설정, N: 즉시 거래")
        print("입력: ", end='', flush=True)
        
        start_time = time.time()
        today_str = now.strftime('%Y-%m-%d')
        
        while time.time() - start_time < 30:          
            try:
                if os.name == 'nt':           
                    if msvcrt.kbhit():
                        reservation = input().upper().strip()
                else:               
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:                 
                        reservation = input().upper().strip()
                    else:
                        continue
                
                if reservation in ['Y', 'N']:
                    if reservation == 'Y':
                                                     
                        print("\n⏰ 몇 시간 몇 분 후에 거래하시겠습니까?")
                        print("형식: 시간 분 (예: 2 30 = 2시간 30분 후, 0 30 = 30분 후)")
                        print("입력: ", end='')
                        
                        try:
                            time_input = input().split()
                            if len(time_input) == 2:
                                hours, minutes = map(int, time_input)
                                if hours < 0 or minutes < 0 or minutes >= 60:
                                    print("\n❌ 올바른 시간을 입력해주세요.")
                                    continue
                            else:
                                print("\n❌ 올바른 형식으로 입력해주세요. (예: 2 30 또는 0 30)")
                                continue
                            
                                      
                            reservation_time = now + timedelta(hours=hours, minutes=minutes)
                            print(f"\n⏰ 예약 시간: {reservation_time.strftime('%Y-%m-%d %H:%M')}")
                            
                                     
                            print("\n🎯 거래할 티커(토큰 심볼)를 입력해주세요")
                            print("여러 토큰인 경우 띄어쓰기로 구분해주세요  | 예시: BTC ETH XRP")
                            print("입력: ", end='')
                            tickers = input().upper().split()
                            
                            if not tickers:
                                print("\n❌ 티커를 입력해주세요.")
                                continue
                            
                                          
                            already_traded = []
                            for ticker in tickers:
                                if f"{ticker}_{today_str}" in trade_log.data:
                                    already_traded.append(ticker)
                            
                            if already_traded:
                                print(f"\n❌ 다음 티커는 이미 오늘 거래되었습니다: {', '.join(already_traded)}")
                                continue
                            
                                     
                            print("\n📅 각 토큰을 며칠간 거래하실 건가요? (오늘 포함, 하루 2번 기준)")
                            print("여러 토큰인 경우 띄어쓰기로 구분해주세요 | 예시: 3 5 7")
                            print("입력: ", end='')
                            durations = list(map(int, input().split()))
                            
                            if len(tickers) != len(durations):
                                print("\n❌ 티커 수와 기간 수가 일치하지 않습니다.")
                                continue
                            
                                                
                            reservation_id = self.reservation_log.add_reservation(reservation_time, tickers, durations)
                            
                            print(f"\n✅ 예약이 설정되었습니다!")
                            print(f"⏰ 예약 시간: {reservation_time.strftime('%Y-%m-%d %H:%M')}")
                            print(f"🎯 거래 티커: {', '.join(tickers)}")
                            print(f"📅 거래 기간: {', '.join(map(str, durations))}일")
                            print("예약 시간에 자동으로 거래가 시작됩니다.")
                            return True
                            
                        except ValueError as e:
                            print(f"\n❌ 올바른 형식으로 입력해주세요. (오류: {e})")
                            continue
                    else:
                                            
                        print("\n🎯 거래할 티커(토큰 심볼)를 입력해주세요")
                        print("여러 토큰인 경우 띄어쓰기로 구분해주세요  | 예시: BTC ETH XRP")
                        print("입력: ", end='', flush=True)
                        
                        start_time = time.time()
                        
                        while time.time() - start_time < 30:          
                            try:
                                if os.name == 'nt':           
                                    if msvcrt.kbhit():
                                        tickers = input().upper().split()
                                else:               
                                    import select
                                    if select.select([sys.stdin], [], [], 0.1)[0]:                 
                                        tickers = input().upper().split()
                                    else:
                                        continue
                                
                                if tickers:
                                                  
                                    already_traded = []
                                    for ticker in tickers:
                                        if f"{ticker}_{today_str}" in trade_log.data:
                                            already_traded.append(ticker)
                                    
                                    if already_traded:
                                        print(f"\n❌ 다음 티커는 이미 오늘 거래되었습니다: {', '.join(already_traded)}")
                                        print("\n🎯 거래할 티커(토큰 심볼)를 입력해주세요")
                                        print("여러 토큰인 경우 띄어쓰기로 구분해주세요  | 예시: BTC ETH XRP")
                                        print("입력: ", end='')
                                        continue

                                    print("\n📅 각 토큰을 며칠간 거래하실 건가요? (오늘 포함, 하루 2번 기준)")
                                    print("여러 토큰인 경우 띄어쓰기로 구분해주세요 | 예시: 3 5 7")
                                    print("입력: ", end='')
                                    durations = list(map(int, input().split()))
                                    if len(tickers) == len(durations):
                                        trading_service.process_trades(tickers, durations, now, is_user_input=True)
                                        return True
                                    else:
                                        print("\n❌ 티커 수와 기간 수가 일치하지 않습니다.")
                                        print("\n🎯 거래할 티커(토큰 심볼)를 입력해주세요")
                                        print("여러 토큰인 경우 띄어쓰기로 구분해주세요  | 예시: BTC ETH XRP")
                                        print("입력: ", end='')
                            except KeyboardInterrupt:
                                print("\n\n프로그램을 종료합니다.")
                                return False
                            except:
                                print("\n❌ 올바른 형식으로 입력해주세요.")
                                print("\n🎯 거래할 티커(토큰 심볼)를 입력해주세요")
                                print("여러 토큰인 경우 띄어쓰기로 구분해주세요  | 예시: BTC ETH XRP")
                                print("입력: ", end='')
                                time.sleep(0.1)
                        return False
                else:
                    print("\n❌ Y 또는 N을 입력해주세요.")
                    print("\n⏰ 예약 거래를 설정하시겠습니까? (Y/N)")
                    print("입력: ", end='')
                    continue
                    
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                return False
            except:
                print("\n❌ 올바른 형식으로 입력해주세요.")
                print("\n⏰ 예약 거래를 설정하시겠습니까? (Y/N)")
                print("입력: ", end='')
                time.sleep(0.1)
        
        return False

    def check_reservation(self, now):
        """예약된 거래가 있는지 확인하고 실행"""
                   
        self.reservation_log.clear_expired_reservations(now)
        
                    
        active_reservations = self.reservation_log.get_active_reservations(now)
        
        if active_reservations:
                            
            reservation = active_reservations[0]
            print(f"\n⏰ 예약 시간이 되었습니다! ({reservation['time'].strftime('%Y-%m-%d %H:%M')})")
            print("🎯 예약된 거래를 시작합니다.")
            
                   
            self.reservation_log.remove_reservation(reservation['id'])
            
                       
            return {
                'time': reservation['time'],
                'tickers': reservation['tickers'],
                'durations': reservation['durations']
            }
        
                         
        return None 