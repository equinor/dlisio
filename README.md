# dlisio #

[![Travis](https://img.shields.io/travis/equinor/dlisio/master.svg?label=travis)](https://travis-ci.org/equinor/dlisio)
[![Appveyor](https://ci.appveyor.com/api/projects/status/jdhagpm7jkga07j1?svg=true)](https://ci.appveyor.com/project/jokva/dlisio)
[![PyPI version](https://badge.fury.io/py/dlisio.svg)](https://badge.fury.io/py/dlisio)

## Index ##

* [Introduction](#introduction)
* [Getting started](#getting-started)
  * [Get dlisio](#get-dlisio)
  * [Build dlisio](#build-dlisio)
* [Tutorial](#tutorial)
* [Contributing](#contributing)

## Introduction ##

dlisio is an LGPL licensed library for working with well logs in Digital Log
Interchange Standard (DLIS V1), also known as
[RP66 V1](http://w3.energistics.org/rp66/v1/Toc/main.html). DLIS V2 is
out-of-scope for this project, as it is quite different and hardly in use in
the industry. It is an attempt at a powerful community-driven, portable,
easy-to-use and flexible library for well logs, that can be used to build a
wide array of applications.

Features are added as they are needed; suggestions, defect reports, and
contributions of all kinds are very welcome.

## Getting started ##

dlisio is in rapid development, and the interfaces are *not* stable. We welcome
any users and will try our best to accomodate your needs, but we currently make
no guarantees that code that works today will work tomorrow.

### Get dlisio ###

The end-user should go through the python library, as the core library is
intended for developers only. The pre-built alpha releases are available
through [pypi](https://pypi.org/project/dlisio/)

```bash
pip3 install dlisio
```

Once dlisio is stable it will also be availble as debian, fedora, and conda
packages.

### Build dlisio ###

To develop dlisio, or to build a particular revision from source, you need:

* A C++11 compatible compiler (tested daily on gcc, clang, and msvc 2015)
* [CMake](https://cmake.org/) version 3.5 or greater
* [Python](https://python.org) version 3.5 or greater
* [fmtlib](http://fmtlib.net/) tested mainly with 5.3.0
* [pybind11](https://github.com/pybind/pybind11) version 2.2 or greater
* [setuptools](https://pypi.python.org/pypi/setuptools) version 28 or greater
* python packages pytest, pytest-runner, and numpy

If you do not have pybind11 installed on your system, the easiest way to get a
working copy is to `pip3 install pybind11` (NP! pybind11, not pybind)

If you do not have fmtlib installed on your system, you can obtain a copy by
either:

* `git clone --recursive https://github.com/equinor/dlisio`
* `git submodule update --init external/fmt`

To then build and install dlisio:

```bash
mkdir dlisio/build
cd dlisio/build
cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON
make
```

dlisio follows common cmake rules and conventions, e.g. to set install prefix
use `-DCMAKE_INSTALL_PREFIX`. To build the python library it is usually a good
idea to build shared libraries. To disable python, pass `-DBUILD_PYTHON=OFF`.
By default, the python library is built.

## Tutorial ##

Tutorial, documentation and how-tos will come soon.

## Contributing ##

We welcome all kinds of contributions, including code, bug reports, issues,
feature requests, and documentation. The preferred way of submitting a
contribution is to either make an
[issue](https://github.com/equinor/dlisio/issues) on github or by forking the
project on github and making a pull request.
