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

#add_library(variant ALIAS mpark-variant)
export(
    TARGETS
        mpark-variant
    NAMESPACE
        mpark::
    FILE
        mpark-config.cmake
)

set(MPARK_LIB_BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR} CACHE PATH "")
