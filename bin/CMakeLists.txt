set(CMAKE_CXX_STANDARD 11)

add_executable(dlis-describe describe.cpp)
target_link_libraries(dlis-describe dlisio)
