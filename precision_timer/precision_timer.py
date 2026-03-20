import time

class PrecisionTimer:
    """
    고정밀 루프 실행을 위한 타이머 클래스
    Drift Correction(오차 누적 방지) 및 Hybrid Waiting(Sleep + Busy-wait) 기법 적용
    """
    def __init__(self, target_hz: float, busy_threshold: float = 0.002):
        self.target_hz = target_hz
        self.interval = 1.0 / target_hz
        self.busy_threshold = busy_threshold
        self.start_time = None
        self.prev_time = None
        self.loop_count = 0
        self._reset()

    def _reset(self):
        self.start_time = time.perf_counter()
        self.prev_time = self.start_time
        self.loop_count = 0

    def sleep(self) -> tuple[float, float]:
        """
        다음 루프 주기까지 정밀하게 대기하고 dt와 error를 반환합니다.
        """
        self.loop_count += 1
        target_time = self.start_time + (self.loop_count * self.interval)

        # 1. 하이브리드 대기 (Hybrid Waiting)
        while True:
            remaining = target_time - time.perf_counter()
            if remaining <= 0:
                break
            if remaining > self.busy_threshold:
                time.sleep(remaining - self.busy_threshold)
            else:
                pass # Busy-waiting

        # 2. 시간 측정 및 결과 반환
        current_time = time.perf_counter()
        dt = current_time - self.prev_time
        error = current_time - target_time
        self.prev_time = current_time

        # 3. 지연 발생 시 기준점 재설정 (Drift Reset)
        if current_time > target_time + self.interval:
            self._reset()

        return dt, error


ptimer = PrecisionTimer(target_hz=30)
def SLEEP():
    ptimer.sleep()

# --- 사용 예제 ---
if __name__ == "__main__":
    start_time = time.time()
    try:
        while True:
            SLEEP() # 30 hz

            # 측정
            dt = time.time() - start_time
            start_time = time.time()
            print(f"실행 dt: {dt:.6f}s")

            # 가장 작업 부하
            time.sleep(0.030)

    except KeyboardInterrupt:
        print("\n[Ctrl+C] 종료")
    finally:
        pass
    print("-" * 50)
    print("테스트 종료.")