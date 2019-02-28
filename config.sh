#!/bin/sh

function run_tests {
    set -x
    python -c "import dlisio; print(dlisio.__version__)"
}

function pre_build {
    if [ -d build-centos5 ]; then return; fi

    python -m pip install cmake pybind11

    curl -sL https://dl.bintray.com/boostorg/release/1.66.0/source/boost_1_66_0.tar.gz | tar xz

    mkdir build-centos5
    pushd build-centos5

    cmake --version
    cmake .. -DBUILD_PYTHON=OFF \
             -DCMAKE_BUILD_TYPE=Release \
             -DBUILD_SHARED_LIBS=ON \
             -DBOOST_ROOT=boost_1_66_0

    if [ -n "$IS_OSX" ]; then
        sudo make install;
        sudo cp -r ../external/mpark/mpark /usr/local/include;
        sudo cp -r ../external/mio/mio     /usr/local/include;
    else
        make install;
        cp -r ../external/mpark/mpark /usr/local/include;
        cp -r ../external/mio/mio /usr/local/include;
    fi

    popd

    # clean dirty files from python/, otherwise it picks up the one built
    # outside docker and symbols will be too recent for auditwheel.
    # setuptools_scm really *really* expects a .git-directory. As the wheel
    # building process does its work in /tmp, setuptools_scm crashes because it
    # cannot find the .git dir. Leave version.py so that setuptools can obtain
    # the version from it
    git clean -dxf python --exclude python/dlisio/version.py
}
