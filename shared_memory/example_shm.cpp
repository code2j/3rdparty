#include <atomic>
#include <functional>
#include <thread>
#include <iostream>
#include "shared_memory.hpp"

using namespace std;

// 공유 메모리 예제
int main() {
    std::cout << "[EXAMPLE] Shared Memory\n";

    struct fields_config {
        float joint[6];    // 24 bytes
        char status[20];   // 20 bytes
    };

    // 공유 메모리 생성
    SharedMemory<fields_config> sm("test_shm2");

    // 쓰기
    fields_config data;
    data.joint[0] = 1.0;
    data.joint[1] = 2.0;
    data.joint[2] = 3.0;
    data.joint[3] = 4.0;
    data.joint[4] = 5.0;
    data.joint[5] = 6.0;
    data.status[0] = 'O';
    data.status[1] = 'K';
    data.status[2] = '\0';

    sm.set(data);

    // 읽기
    fields_config data2 = sm.get();
    cout << "Read data: joint[0] = " << data2.joint[0] << ", status = " << data2.status << endl;


    // 직접 호출 하지 않으면 시스템 재부팅 전까지 메모리가 유지됨
    // SharedMemory<fields_config>::unlink("test_shm");

    return 0;
}
