import os
import json
from datetime import datetime

class ReservationLog:
    def __init__(self, log_file="reservation_log.json"):
        self.log_file = log_file
        self.data = self.load()

    def load(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, FileNotFoundError):
                print("⚠️ 예약 로그 파일을 읽는 중 오류가 발생했습니다. 새로 생성합니다.")
        return {}

    def save(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_reservation(self, reservation_time, tickers, durations):
        """예약 정보를 추가합니다."""
        reservation_id = f"reservation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.data[reservation_id] = {
            'time': reservation_time.strftime('%Y-%m-%d %H:%M:%S'),
            'tickers': tickers,
            'durations': durations,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.save()
        return reservation_id

    def get_active_reservations(self, now):
        """현재 시간 기준으로 활성화된 예약을 반환합니다."""
        active_reservations = []
        
        for reservation_id, reservation_data in self.data.items():
            try:
                reservation_time = datetime.strptime(reservation_data['time'], '%Y-%m-%d %H:%M:%S')
                                                
                if now >= reservation_time:
                    active_reservations.append({
                        'id': reservation_id,
                        'time': reservation_time,
                        'tickers': reservation_data['tickers'],
                        'durations': reservation_data['durations']
                    })
            except (ValueError, KeyError) as e:
                print(f"⚠️ 예약 데이터 파싱 오류 ({reservation_id}): {e}")
                continue
        
                               
        active_reservations.sort(key=lambda x: x['time'])
        return active_reservations

    def remove_reservation(self, reservation_id):
        """예약을 삭제합니다."""
        if reservation_id in self.data:
            del self.data[reservation_id]
            self.save()
            return True
        return False

    def clear_expired_reservations(self, now):
        """만료된 예약들을 정리합니다."""
        expired_ids = []
        
        for reservation_id, reservation_data in self.data.items():
            reservation_time = datetime.strptime(reservation_data['time'], '%Y-%m-%d %H:%M:%S')
                             
            if (now - reservation_time).total_seconds() > 86400:        
                expired_ids.append(reservation_id)
        
        for reservation_id in expired_ids:
            del self.data[reservation_id]
        
        if expired_ids:
            self.save()
        
        return len(expired_ids)

    def has_active_reservations(self, now):
        """활성화된 예약이 있는지 확인합니다."""
        return len(self.get_active_reservations(now)) > 0 