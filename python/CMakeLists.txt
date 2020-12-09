if (SKBUILD)
    # invoked as a part of scikit-build, so this is just a proxy for the python
    # extension cmake. this works around the fundamental limitation in cmake
    # that it looks only for directories with a CMakeLists.txt in it, not for a
    # named file
    include(setup-CMakeLists.txt)
    return ()
endif ()

cmake_minimum_required(VERSION 3.5.0)
project(dlisio-python)

if(NOT BUILD_PYTHON)
    return()
endif()

find_package(PythonInterp REQUIRED)

if(NOT PYTHON_EXECUTABLE)
    message(WARNING "Could not find python - skipping python bindings")
    message(WARNING "Select specific python distribution with "
                    "-DPYTHON_EXECUTABLE=bin/python")
    return()
endif()

set(python ${PYTHON_EXECUTABLE})
set(setup.py ${CMAKE_CURRENT_SOURCE_DIR}/setup.py)

if (CMAKE_BUILD_TYPE)
    # use the cmake_build_type of the source project, unless it has been
    # specifically overriden
    set(DLISIO_PYTHON_BUILD_TYPE
        --build-type=${CMAKE_BUILD_TYPE}
        CACHE STRING "override CMAKE_BUILD_TYPE in python extension"
    )
endif ()

# is set when target platform was provided by user
if (CMAKE_GENERATOR_PLATFORM)
    set(DLISIO_GENERATOR_PLATFORM -A ${CMAKE_GENERATOR_PLATFORM})
endif ()

add_custom_target(
    dlisio-python ALL
    COMMENT "Building python library with setup.py"
    SOURCES ${setup.py}
    DEPENDS ${setup.py}
    VERBATIM
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}

    COMMAND ${python} ${setup.py}
        # build the extension inplace (really, once its built, copy it to the
        # source tree) so that post-build, the directory can be used to run
        # tests against
        build_ext --inplace
        build # setup.py build args
            --cmake-executable ${CMAKE_COMMAND}
            --generator ${CMAKE_GENERATOR}
            ${DLISIO_PYTHON_BUILD_TYPE}
        -- # cmake to the extension
            -Ddlisio_DIR=${DLISIO_LIB_BINARY_DIR}
            # "install" to the python/dlisio dir with rpath, so there's no need
            # to fiddle with environment in ctest to load the core library from
            # the build tree
            -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON
            -DCMAKE_INSTALL_RPATH=$<TARGET_FILE_DIR:dlisio>
            -DCMAKE_INSTALL_NAME_DIR=$<TARGET_FILE_DIR:dlisio>
            ${DLISIO_GENERATOR_PLATFORM}
)

add_dependencies(dlisio-python dlisio dlisio-extension)

install(CODE "
    if (DEFINED ENV{DESTDIR})
        get_filename_component(abs-destdir \"\$ENV{DESTDIR}\" ABSOLUTE)
        set(root_destdir --root \${abs-destdir})
    endif()

    execute_process(
        COMMAND ${python} ${setup.py}
            install
                \${root_destdir}
                --single-version-externally-managed
                --record record.txt
                --cmake-executable \"${CMAKE_COMMAND}\"
                --generator \"${CMAKE_GENERATOR}\"
                ${DLISIO_PYTHON_BUILD_TYPE}
            --
                ${DLISIO_GENERATOR_PLATFORM}
                -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=OFF
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )"
)

option(BUILD_PYDOC "Build python documentation" OFF)

if(BUILD_DOC)
    set(BUILD_PYDOC ON)
endif()

if(BUILD_PYDOC)
    find_program(sphinx sphinx-build)

    if(NOT sphinx)
        message(WARNING "Could not find sphinx, skipping python documentation")
        set(BUILD_PYDOC OFF)
    endif()

endif()

if(BUILD_PYDOC AND sphinx)
    # use the -d argument to avoid putting cache dir in docs/, because that
    # directory will be install'd
    add_custom_target(pydoc
        COMMAND ${sphinx}
            -d ${CMAKE_CURRENT_BINARY_DIR}/.doctrees
            ${SPHINX_ARGS}
            ${CMAKE_CURRENT_SOURCE_DIR}/docs
            ${CMAKE_CURRENT_BINARY_DIR}/docs
        DEPENDS docs/conf.py
                docs/index.rst
                docs/dlisio.rst
        COMMENT "Building python documentation with sphinx"
    )
    add_dependencies(doc pydoc)

    install(
        DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/docs/
        DESTINATION ${CMAKE_INSTALL_DATADIR}/doc/dlisio
    )
endif()

# run tests with setup.py test
# this is very slow compared to invoking pytest directly, but setuptools will
# copy the built extension into the tree as it sees fit
#
# use --skip-cmake, otherwise running the tests would trigger a build with
# different args to setup.py, rebuilding the python lib (and wrongly so as it
# either won't find dlisio or picked up on a system installed one)
add_test(NAME python.unit
    COMMAND ${python} ${setup.py} --skip-cmake test
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
