cmake_minimum_required(VERSION 3.5)
project(mpark-variant CXX)

# backport of the C++17 variant for C++11
# https://github.com/mpark/variant

add_library(mpark-variant INTERFACE)
target_include_directories(mpark-variant
    SYSTEM
    INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}
)
