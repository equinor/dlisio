cmake_minimum_required(VERSION 3.5)
project(dlisio LANGUAGES CXX)

include(CheckIncludeFile)
include(CTest)
include(GNUInstallDirs)
include(TestBigEndian)

option(BUILD_PYTHON "Build Python extension" ON)
option(BUILD_DOC    "Build documentation"    OFF)

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

# add documentation master target for other documentation sub targets to hook
# into
add_custom_target(doc ALL)

set(CMAKE_CXX_STANDARD 11)

test_big_endian(BIG_ENDIAN)

add_subdirectory(external/endianness)
add_subdirectory(external/catch2)
add_subdirectory(external/mpark)
add_subdirectory(external/fmt)

find_package(lfp REQUIRED)

if (NOT TARGET fmt)
    find_package(fmt REQUIRED)
endif ()

add_subdirectory(lib)
add_subdirectory(python)
