import numpy as np
from multiprocessing import shared_memory, resource_tracker
import atexit
from typing import Dict, Tuple, Any

class SharedMemoryManager:
    def __init__(self, name: str, fields_config: Dict[str, Tuple[int, Any]], create: bool = True):
        self.name = name
        self.fields = {}
        offset = 0
        for f_name, (count, dtype) in fields_config.items():
            item_size = 1 if dtype == str else np.dtype(dtype).itemsize
            byte_size = count * item_size
            self.fields[f_name] = {
                'offset': offset,
                'count': count,
                'dtype': dtype,
                'byte_size': byte_size
            }
            offset += byte_size

        self.total_size = offset

        try:
            # 일단 생성
            self.shm = shared_memory.SharedMemory(name=name, create=create, size=self.total_size)
        except FileExistsError:
            # 이미 있으면 메모리 링크
            self.shm = shared_memory.SharedMemory(name=name)

        # 리소스 트래커에서 제외 (프로세스 종료 시에도 메모리 유지 목적)
        try:
            resource_tracker.unregister(self.shm._name, "shared_memory")
        except:
            pass

        atexit.register(self.close)

    def set(self, field_name: str, value: Any) -> None:
        f = self.fields[field_name]
        if f['dtype'] == str:
            # 문자열을 바이트로 변환 후 지정된 크기만큼만 복사
            encoded = str(value).encode('utf-8')[:f['byte_size']]
            # 버퍼 초기화 (이전 데이터 잔상 제거)
            self.shm.buf[f['offset'] : f['offset'] + f['byte_size']] = b'\x00' * f['byte_size']
            self.shm.buf[f['offset'] : f['offset'] + len(encoded)] = encoded
        else:
            # numpy view를 생성하여 값 복사
            arr = np.ndarray((f['count'],), dtype=f['dtype'], buffer=self.shm.buf, offset=f['offset'])
            arr[:] = value

    def get(self, field_name: str) -> Any:
        f = self.fields[field_name]
        # buf에서 해당 영역만 먼저 bytearray로 추출하여 참조를 최소화
        target_buf = self.shm.buf[f['offset'] : f['offset'] + f['byte_size']]

        if f['dtype'] == str:
            return bytes(target_buf).decode('utf-8', errors='ignore').split('\x00')[0]
        else:
            # frombuffer는 내부적으로 copy를 수행하지 않으므로 .copy() 필수
            return np.frombuffer(target_buf, dtype=f['dtype']).copy()

    def close(self) -> None:
        if hasattr(self, 'shm'):
            self.shm.close()



# --- 실행 예시 ---
def main():
    fields_config = {
        'joint': (6, np.float32), # 24
        'status': (20, str)  # 20바이트 크기 문자열
    }

    # 1. 생성 및 쓰기
    shm = SharedMemoryManager(name='test_shm2', fields_config=fields_config)
    shm.set('joint', [1.1, 2.2, 3.3, 4.4, 5.5, 6.6])
    shm.set('status', 'running')

    # 2. 읽기 (get 메서드 사용)
    joint_data = shm.get('joint')
    status_data = shm.get('status')

    print(f"Joint: {joint_data} (Type: {joint_data.dtype})")
    print(f"Status: {status_data}")

if __name__ == "__main__":
    main()