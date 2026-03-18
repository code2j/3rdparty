from multiprocessing import shared_memory, resource_tracker
import atexit

class SharedMemory:
    def __init__(self, name: str, fields_config: Dict[str, Tuple[int, Any]]):
        self.name = name
        self.fields = {}
        offset = 0
        for f_name, (count, dtype) in fields_config.items():
            item_size = 1 if dtype == str else np.dtype(dtype).itemsize
            byte_size = count * item_size
            self.fields[f_name] = {'offset': offset, 'count': count, 'dtype': dtype, 'byte_size': byte_size}
            offset += byte_size
        self.total_size = offset

        try:
            self.shm = shared_memory.SharedMemory(name=name, create=True, size=self.total_size)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=name)

        try:
            resource_tracker.unregister(self.shm._name, "shared_memory")
        except: pass
        atexit.register(self.close)

    def set(self, field_name: str, value: Any) -> None:
        f = self.fields[field_name]
        if f['dtype'] == str:
            encoded = str(value).encode('utf-8')[:f['byte_size']]
            self.shm.buf[f['offset'] : f['offset'] + len(encoded)] = encoded
        else:
            arr = np.ndarray((f['count'],), dtype=f['dtype'], buffer=self.shm.buf, offset=f['offset'])
            arr[:] = value

    def close(self) -> None:
        if hasattr(self, 'shm'): self.shm.close()


def main():
    fields_config = {
        'joint': (6, np.float32),
        'status': (20, str)
    }

    # 생성
    shm = SharedMemory(name='movej', fields_config=fields_config)

    # 쓰기
    shm.set('joint', [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    shm.set('status', 'success')


    # 읽기
    joint = shm.fields['joint']
    status = shm.fields['status']

    print(f"Joint: {joint['dtype']}, {joint['count']} elements")
    print(f"Status: {status['dtype']}, {status['count']} characters")