cmake_minimum_required(VERSION 3.5)
project(mio CXX)

# https://github.com/mandreyel/mio

add_library(mio INTERFACE)
target_include_directories(mio
    SYSTEM
    INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}
)
