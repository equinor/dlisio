cmake_minimum_required(VERSION 3.5)
project(mio CXX)

# https://github.com/mandreyel/mio

add_library(mio INTERFACE)
target_include_directories(mio
    SYSTEM
    INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

export(
    TARGETS
        mio
    NAMESPACE
        mio::
    FILE
        mio-config.cmake
)

set(MIO_LIB_BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR} CACHE PATH "")
