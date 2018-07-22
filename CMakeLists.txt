cmake_minimum_required(VERSION 3.5)
project(dlisio LANGUAGES C CXX)

include(CheckIncludeFile)
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

check_include_file(arpa/inet.h  HAVE_ARPA_INET)
check_include_file(netinet/in.h HAVE_NETINET_IN)
check_include_file(winsock2.h   HAVE_WINSOCK2)

if(HAVE_ARPA_INET)
    list(APPEND htons HAVE_ARPA_INET)
elseif(HAVE_NETINET_IN)
    list(APPEND htons HAVE_NETINET_IN)
elseif(HAVE_WINSOCK2)
    set(ws2 ws2_32)
    list(APPEND htons HAVE_WINSOCK2)
else()
    message(FATAL_ERROR "Could not find known ntohs headers")
endif()

add_subdirectory(external/catch2)
add_subdirectory(lib)
add_subdirectory(bin)
