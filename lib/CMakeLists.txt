add_library(dlisio src/dlisio.cpp
                   src/types.cpp
)
target_include_directories(dlisio
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
           $<INSTALL_INTERFACE:include>
)
target_compile_options(dlisio
    BEFORE
    PRIVATE $<$<CONFIG:Debug>:${warnings-c++}>
)
target_compile_definitions(dlisio
    PRIVATE $<${BIG_ENDIAN}:HOST_BIG_ENDIAN>
)

install(TARGETS dlisio
        EXPORT dlisio
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(DIRECTORY include/ DESTINATION include)
install(EXPORT dlisio DESTINATION share/dlisio/cmake FILE dlisio-config.cmake)
export(TARGETS dlisio FILE dlisio-config.cmake)

add_library(dlisio-extension src/parse.cpp
                             src/io.cpp
)
target_include_directories(dlisio-extension
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/extension>
           $<INSTALL_INTERFACE:extension>
)
target_compile_options(dlisio-extension
    BEFORE
    PRIVATE $<$<CONFIG:Debug>:${warnings-c++}>
)
target_link_libraries(dlisio-extension
    PUBLIC dlisio
           mpark-variant
           mio

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

if(NOT BUILD_TESTING)
    return()
endif()

add_executable(testsuite test/testsuite.cpp
                         test/protocol.cpp
                         test/types.cpp
                         test/sul.cpp
                         test/pack.cpp
                         test/index-records.cpp
)
target_link_libraries(testsuite dlisio dlisio-extension catch2)
add_test(NAME core COMMAND testsuite)
