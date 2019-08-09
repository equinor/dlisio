cmake_minimum_required(VERSION 3.5)
project(endianness VERSION 0.1.0)

add_library(endianness INTERFACE)
add_library(endianness::endianness ALIAS endianness)
target_include_directories(endianness
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

#
# install & export
#
install(TARGETS endianness
        EXPORT endianness-export
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(DIRECTORY include/ DESTINATION include)
install(
    EXPORT endianness-export
    NAMESPACE endianness::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/endianness/cmake
    FILE endianness-config.cmake
)
export(TARGETS endianness FILE endianness-config.cmake)
