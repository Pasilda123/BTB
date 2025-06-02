import time
import msvcrt

class DisplayUtils:
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
        print("\n\n🕐 30분 후 공지를 다시 확인합니다")
        print("🔄 프로그램을 종료하려면 Ctrl+C를 누르세요")
        print("\033[?25l", end="")
        print("\n" + "─" * 50)

    @staticmethod
    def handle_user_input(now, trading_service, trade_log):
        print("\n")
        print("🎯 거래할 티커(토큰 심볼)를 입력해주세요")
        print("여러 토큰인인 경우 띄어쓰기로 구분해주세요  | 예시: BTC ETH XRP")
        print("입력: ", end='', flush=True)
        
        start_time = time.time()
        
        while time.time() - start_time < 30:
            try:
                if msvcrt.kbhit():
                    tickers = input().upper().split()
                    if tickers:
                        print("📅 각 토큰을 며칠간 거래하실 건가요? (오늘 포함, 하루 2번 기준)")
                        print("여러 토큰인 경우 띄어쓰기로 구분해주세요 | 예시: 3 5 7")
                        print("입력: ", end='')
                        durations = list(map(int, input().split()))
                        if len(tickers) == len(durations):
                            trading_service.process_trades(tickers, durations, now, is_user_input=True)
                            return True
                        else:
                            print("\n❌ 티커 수와 기간 수가 일치하지 않습니다.")
                            print("🎯 거래할 티커(토큰 심볼)를 입력해주세요")
                            print("여러 토큰인 경우 띄어쓰기로 구분해주세요  | 예시: BTC ETH XRP")
                            print("입력: ", end='')
                time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                return False
            except:
                print("\n❌ 올바른 형식으로 입력해주세요.")
                print("🎯 거래할 티커(토큰 심볼)를 입력해주세요")
                print("여러 토큰인 경우 띄어쓰기로 구분해주세요  | 예시: BTC ETH XRP")
                print("입력: ", end='')
                time.sleep(0.1)
        return False 