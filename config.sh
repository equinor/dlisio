#!/bin/sh

function run_tests {
    set -x
    python -c "import dlisio; print(dlisio.__version__)"
}

function pre_build {
    if [ -d build-centos5 ]; then return; fi

    python -m pip install cmake pybind11

    # clean dirty files from python/, otherwise it picks up the one built
    # outside docker and symbols will be too recent for auditwheel
    git clean -dxf python

    # this is a super hack necessary because setuptools_scm really *really*
    # expects a .git-directory. The wheel building process does its work in
    # /tmp, and setuptools_scm crashes because it cannot find the .git dir
    #
    # by copying (!) the git dir into python/ this problem goes away
    cp -r .git python

    mkdir build-centos5
    pushd build-centos5

    cmake --version
    cmake .. -DBUILD_PYTHON=OFF \
             -DCMAKE_BUILD_TYPE=Release \
             -DBUILD_SHARED_LIBS=ON

    if [ -n "$IS_OSX" ];
        then sudo make install;
        else make install;
    fi

    popd
}
