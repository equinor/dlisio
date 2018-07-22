set(CMAKE_CXX_STANDARD 11)

add_executable(dlis-describe describe.cpp)
target_link_libraries(dlis-describe dlisio)

install(TARGETS dlis-describe
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
