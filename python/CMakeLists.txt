cmake_minimum_required(VERSION 3.18)
project(dlisio-python LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_VISIBILITY_PRESET "hidden")
set(CMAKE_C_VISIBILITY_PRESET   "hidden")

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

if(NOT Python_EXECUTABLE)
    message(WARNING "Could not find python - skipping python bindings")
    message(WARNING "Select specific python distribution with "
                    "-DPython_EXECUTABLE=bin/python")
    return()
endif()

find_package(mpark_variant    REQUIRED)
find_package(lfp              REQUIRED)
find_package(fmt              REQUIRED)

# pybind11 is not easily discovered by CMake in virtual environments
# https://github.com/pybind/pybind11/issues/3445
find_package(pybind11 CONFIG REQUIRED HINTS "${Python_SITELIB}")

# If we execute CMake via a scikit-build-core, i.e., `python -m build`, `pip
# install` etc., we expect that the dlisio library is available on the system.
if (SKBUILD)
    find_package(dlisio REQUIRED)
endif()

python_add_library(core MODULE WITH_SOABI
    dlisio/ext/core.cpp
    dlisio/ext/lis.cpp
    dlisio/ext/dlis.cpp
)
target_link_libraries(core PRIVATE dlisio mpark_variant pybind11::headers)

if (MSVC)
    target_compile_options(core
        BEFORE
        PRIVATE
            /EHsc
    )
endif ()

# is set when target platform was provided by user
if (CMAKE_GENERATOR_PLATFORM)
    set(DLISIO_GENERATOR_PLATFORM -A ${CMAKE_GENERATOR_PLATFORM})
endif ()


if (SKBUILD)
    set(DLISIO_PYTHON_INSTALL_DIR dlisio)
else()
    # CMake defines Python_SITELIB that points to the system path for Python
    # libraries, but we cannot use it here. In case of a non-empty installation
    # prefix, CMake would merge the installation path into something like
    # ${CMAKE_INSTALL_PREFIX}/${Python_SITELIB} which would lead to the wrong
    # full path. For example, it could look like this:
    #
    # /usr/local/usr/lib/python3.12/site-packages
    #   PREFIX  |          SITELIB
    #
    # This is not a path one would expect the Python library to be in.
    set(DLISIO_PYTHON_INSTALL_DIR lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages/dlisio)
endif()

install(TARGETS core LIBRARY DESTINATION ${DLISIO_PYTHON_INSTALL_DIR})

# Emulate in-place build behavior of invoking `python setup.py build_ext -i`.
# This places the binding library into the `python/dlisio/` directory. Doing so
# allows the usage of `ctest` to test the core library, but also the Python
# package.
if (MSVC)
    # On Windows, setting the target properties does not work. Whatever is
    # built on Windows does not fullfil CMake's definition of "library",
    # "archive" or other outputs that for which we could set the output
    # directory as target property. Therefore, we copy the library into the
    # correct location.
    add_custom_command(TARGET core POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:core> ${CMAKE_CURRENT_SOURCE_DIR}/dlisio
    )
else()
    set_target_properties(core PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dlisio
    )
endif()

# If CMake is run via a scikit-build-core, we have set up everything needed and
# we can return from this file. The installation and collection of relevant
# files is handled by scikit-build-core. Other options, like building the
# documentation, are not available via scikit-build-core.
if (SKBUILD)
    return()
endif()

# Explicitly install Python files to avoid copying files that are not required,
# e.g., core.cpp or folder like __pycache__ that exist if the tests were run
# via ctest.
install(
    DIRECTORY dlisio/
    DESTINATION ${DLISIO_PYTHON_INSTALL_DIR}
    FILES_MATCHING PATTERN "*.py"
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
        COMMENT "Building python documentation with sphinx"
    )
    add_dependencies(doc pydoc)

    install(
        DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/docs/
        DESTINATION ${CMAKE_INSTALL_DATADIR}/doc/dlisio
    )
endif()

set(python ${Python_EXECUTABLE})

# run tests with setup.py test
# this is very slow compared to invoking pytest directly, but setuptools will
# copy the built extension into the tree as it sees fit
#
# use --skip-cmake, otherwise running the tests would trigger a build with
# different args to setup.py, rebuilding the python lib (and wrongly so as it
# either won't find dlisio or picked up on a system installed one)
add_test(NAME python.unit
    COMMAND ${python} -m pytest tests
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
