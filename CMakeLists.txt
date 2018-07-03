cmake_minimum_required(VERSION 3.5)
project(dlisio LANGUAGES CXX)

include(CTest)
include(GNUInstallDirs)
include(TestBigEndian)

if (NOT MSVC)
    # assuming gcc-style options
    # add warnings in debug mode
    list(APPEND warnings-c++ -Wall
                             -Wextra
                             -pedantic
                             -Wformat-nonliteral
                             -Wcast-align
                             -Wpointer-arith
                             -Wmissing-declarations
                             -Wcast-qual
                             -Wwrite-strings
                             -Wchar-subscripts
                             -Wredundant-decls
    )
endif()

add_subdirectory(external/catch2)
add_subdirectory(lib)
