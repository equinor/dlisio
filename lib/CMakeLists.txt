set(CMAKE_CXX_STANDARD 11)

add_library(dlisio src/dlisio.cpp)
target_include_directories(dlisio
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
           $<INSTALL_INTERFACE:include>
)
target_compile_options(dlisio
    BEFORE
    PRIVATE $<$<CONFIG:Debug>:${warnings-c++}>
)

if(NOT BUILD_TESTING)
    return()
endif()

add_executable(testsuite test/testsuite.cpp
                         test/storage-unit-label.cpp
)
target_link_libraries(testsuite dlisio catch2)
add_test(NAME core COMMAND testsuite)
