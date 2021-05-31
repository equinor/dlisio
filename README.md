<p align="center">
  <img src="dlisio-logo.svg" alt="dlisio logo" width="400"/>
</p>

<p align="center">
  <a href="https://travis-ci.com/equinor/dlisio">
    <img src="https://travis-ci.com/equinor/dlisio.svg?branch=master" alt="Travis"/>
  </a>
  <a href="https://circleci.com/gh/equinor/dlisio/tree/master">
    <img src="https://circleci.com/gh/equinor/dlisio/tree/master.svg?style=svg" alt="CircleCI"/>
  </a>
  <a href="https://ci.appveyor.com/project/jokva/dlisio/branch/master">
    <img src="https://ci.appveyor.com/api/projects/status/jdhagpm7jkga07j1?svg=true" alt="Appveyor"/>
  </a>
  <a href="https://pypi.org/project/dlisio/">
    <img src="https://badge.fury.io/py/dlisio.svg" alt="PyPI version"/>
  </a>
  <a href="http://dlisio.readthedocs.io/">
    <img src="https://img.shields.io/readthedocs/dlisio" alt="Read the Docs"/>
  </a>
</p>

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

As of version 0.3.0, dlisio is extended to also read Log Information Standard
79 ([LIS79](http://w3.energistics.org/LIS/lis-79.pdf)). An extended version of
the LIS79 standard called LIS84/Enhanced LIS exists, but this version is
currently not supported by dlisio.

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

Once dlisio is stable it will also be available as debian, fedora, and conda
packages.

### Build dlisio ###

To develop dlisio, or to build a particular revision from source, you need:

* A C++11 compatible compiler (tested daily on gcc, clang, and msvc 2015)
* [CMake](https://cmake.org/) version 3.5 or greater
* [Python](https://python.org) version 3.6 or greater
* [fmtlib](http://fmtlib.net/) tested mainly with 7.3.1
* [mpark_variant](https://github.com/mpark/variant)
* [pybind11](https://github.com/pybind/pybind11) version 2.6 or greater
* [setuptools](https://pypi.python.org/pypi/setuptools) version 28 or greater
* [layered-file-protocols](https://github.com/equinor/layered-file-protocols)
* python packages pytest, pytest-runner, and numpy

If you do not have pybind11 installed on your system, the easiest way to get a
working copy is to `pip3 install pybind11` (NP! pybind11, not pybind)

layered-file-protocols has to be installed from source if you don't already
have it on your system:

```bash
git clone https://github.com/equinor/layered-file-protocols.git
mkdir layered-file-protocols/build
cd layered-file-protocols/build
cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON
-DLFP_FMT_HEADER_ONLY=ON
make
make install
```

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

dlisio's documentation is hosted on
[readthedocs](https://dlisio.readthedocs.io/en/stable/). Please refer there for
proper introduction to dlisio, and the file-formats DLIS and LIS. With dlisio
it is easy to read the curve-data from DLIS-files:

```python
from dlisio import dlis

with dlis.load('myfile.dlis') as files:
    for f in files:
        for frame in f.frames:
            curves = f.curves()
            # Do something with the curves

```
and from LIS-files:

```python
from dlisio import lis

with lis.load('myfile.lis') as files:
    for f in files:
        for format_spec in f.data_format_specs:
            curves = lis.curves(f, format_spec)
            # Do something with the curves
```

In both cases the curves are returned as [structured
numpy.ndarray](https://numpy.org/doc/stable/user/basics.rec.html) with the
curve mnemonics as field names (column names).

## Contributing ##

We welcome all kinds of contributions, including code, bug reports, issues,
feature requests, and documentation. The preferred way of submitting a
contribution is to either make an
[issue](https://github.com/equinor/dlisio/issues) on github or by forking the
project on github and making a pull request.
