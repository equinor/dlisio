project(dlisio-python)

if(NOT BUILD_PYTHON)
    return()
endif()

find_package(PythonInterp REQUIRED)

if(NOT PYTHON_EXECUTABLE)
    message(WARNING "Could not find python - skipping python bindings")
    return()
endif()

set(python ${PYTHON_EXECUTABLE})
set(setup.py ${CMAKE_CURRENT_SOURCE_DIR}/setup.py)

if (NOT WIN32)
    # setuptools on microsoft compilers doesn't support the --library-dir or
    # --build-dir flag and crashes, so only pass it on non-microsoft platforms
    set(build_ext build_ext --library-dirs ${CMAKE_CURRENT_SOURCE_DIR})
endif()

add_custom_target(
    dlisio-python ALL
    COMMENT "Building python library with setup.py"
    SOURCES ${setup.py}
    DEPENDS ${setup.py}
    VERBATIM
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}

    # setuptools on windows breaks spectacularly when the library isn't
    # available in the same directory, and build_ext --library-dirs is not
    # support on msvc is not supported, so we must copy out the libsegyio core
    # object and put it here
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:dlisio>
                                     $<TARGET_FILE_NAME:dlisio>

    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_LINKER_FILE:dlisio>
                                     $<TARGET_LINKER_FILE_NAME:dlisio>

    COMMAND ${python} ${setup.py} ${build_ext} build
)

add_dependencies(dlisio-python dlisio)

if(NOT BUILD_TESTING)
    return()
endif()

add_test(NAME python.unit
         COMMAND ${python} -m pytest tests/
         WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
