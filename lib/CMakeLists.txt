set(DLISIO_LIB_BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR} CACHE PATH "")

add_library(dlisio src/dlisio.cpp
                   src/types.cpp
)
target_include_directories(dlisio
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
           $<INSTALL_INTERFACE:include>
    PRIVATE
        # Work-around as described in [1]. Even privately linked interface
        # libraries must be exported, because cmake does not check if anything
        # other than include-paths are set. The build-local export file is
        # given to the python build script, so endianness must also be
        # exported.
        #
        # in time, this hack should go away, either by promotoing endianness to
        # a library in its own right, or hard-code the include path
        # (effectively what is done now)
        # [1] https://gitlab.kitware.com/cmake/cmake/issues/18049
        $<TARGET_PROPERTY:endianness::endianness,INTERFACE_INCLUDE_DIRECTORIES>
)
target_compile_options(dlisio
    BEFORE
    PRIVATE
        $<$<CONFIG:Debug>:${warnings-c++}>
        $<$<CXX_COMPILER_ID:MSVC>:/EHsc>
)

install(TARGETS dlisio
        EXPORT dlisio
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(DIRECTORY include/ DESTINATION include)
install(EXPORT dlisio DESTINATION share/dlisio/cmake FILE dlisio-config.cmake)

add_library(dlisio-extension src/parse.cpp
                             src/io.cpp
)
target_include_directories(dlisio-extension
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/extension>
           $<INSTALL_INTERFACE:extension>
)
target_compile_options(dlisio-extension
    BEFORE
    PRIVATE
        $<$<CONFIG:Debug>:${warnings-c++}>
        $<$<CXX_COMPILER_ID:MSVC>:/EHsc>
)
target_compile_definitions(dlisio
    PRIVATE
    $<$<BOOL:${BIG_ENDIAN}>:HOST_BIG_ENDIAN>
    $<$<NOT:$<BOOL:${BIG_ENDIAN}>>:HOST_LITTLE_ENDIAN>
)
target_link_libraries(dlisio-extension
    PUBLIC dlisio
           mpark::variant
           endianness
           lfp::lfp

    PRIVATE fmt-header-only
)

# for now, also install the -extension targets, however, they're not publically
# supported and they're considered private.
install(TARGETS dlisio-extension
        EXPORT dlisio-extension
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(DIRECTORY extension/ DESTINATION include)
export(
    TARGETS
        dlisio
        dlisio-extension
        variant
        fmt-header-only
        endianness
    FILE
        dlisio-config.cmake
)

if(NOT BUILD_TESTING)
    return()
endif()

add_executable(testsuite test/testsuite.cpp
                         test/protocol.cpp
                         test/types.cpp
                         test/sul.cpp
                         test/pack.cpp
)
target_link_libraries(testsuite dlisio dlisio-extension catch2)
add_test(NAME core COMMAND testsuite)
