cmake_minimum_required(VERSION 3.10)
cmake_policy(SET CMP0167 NEW)

project(3rdparty)

# 옵션
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -ffast-math") # Eigen 최적화



if (PROJECT_IS_TOP_LEVEL)
    # 공유 메모리 Shared Memory
    add_executable(example_shared_memory shared_memory/example_shm.cpp)

    # yaml
    add_executable(example_yaml yaml/example_yaml.cpp)

    # socket server
    add_executable(example_server socket/example_server.cpp)

    # socket client
    add_executable(example_client socket/example_client.cpp)
endif()
