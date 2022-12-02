<p align="center">
  <img src="https://raw.githubusercontent.com/equinor/dlisio/master/dlisio-logo.svg" alt="dlisio logo" width="400"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/dlisio/">
    <img src="https://badge.fury.io/py/dlisio.svg" alt="PyPI version"/>
  </a>
  <a href="https://github.com/equinor/dlisio/actions/workflows/wheels.yaml">
    <img src="https://github.com/equinor/dlisio/actions/workflows/wheels.yaml/badge.svg" alt="Github Actions"/>
  </a>
  <a href="http://dlisio.readthedocs.io/">
    <img src="https://img.shields.io/readthedocs/dlisio" alt="Read the Docs"/>
  </a>
</p>

## Introduction ##

dlisio is an LGPL licensed library for reading well logs in Digital Log
Interchange Standard (DLIS V1), also known as [RP66
V1](http://w3.energistics.org/rp66/v1/Toc/main.html), and Log Information
Standard 79 ([LIS79](http://w3.energistics.org/LIS/lis-79.pdf)).

dlisio is designed as a general purpose library for reading well logs in a
simple and easy-to-use manner. Its main focus is making all the data and
metadata accessible while putting few assumptions on how the data is to be
used. This makes it suitable as a building block for higher level applications
as well as for being used directly.

dlisio focuses above all on correctness, performance and robustness. Its core,
which does all the heavy lifting, is implemented in C++. Both the C++ core and
the python wrappers are backed by an extensive test-suite. It strives to be
robust against files that do not strictly adhere to the specifications, which
is a widespread issue with both DLIS and LIS files. dlisio tries to account for
many of the known specification violations out there, but only when it can do
so without compromising correctness. It will not do any guess work on your
behalf when such violations pose any ambiguity.

## Installation ##

dlisio supplies pre-built python wheels for a variety of platforms and
architectures. The wheels are hosted through [PyPi](https://pip.pypi.io) and
can be installed with:

```bash
pip install dlisio
```


|   | macOS Intel | Windows 64bit | Windows 32bit | manylinux x86_64 | manylinux aarch64 |
|---------------|----|-----|-----|----|----|
| CPython 3.6   | ✅ | ✅  | ✅  | ✅ | ✅ |
| CPython 3.7   | ✅ | ✅  | ✅  | ✅ | ✅ |
| CPython 3.8   | ✅ | ✅  | ✅  | ✅ | ✅ |
| CPython 3.9   | ✅ | ✅  | ✅  | ✅ | ✅ |
| CPython 3.10  | ✅ | ✅  | -   | ✅ | ✅ |
| CPython 3.11  | ✅ | ✅  | -   | ✅ | ✅ |

See [Build dlisio](#Build-dlisio) for building dlisio from source.

## Getting started ##

dlisio's documentation is hosted on
[readthedocs](https://dlisio.readthedocs.io/en/stable/). Please refer there for
proper introduction to dlisio and the file-formats DLIS and LIS. Here is a
motivating example showcasing how to read the curve-data from a DLIS-file:

```python
from dlisio import dlis

with dlis.load('myfile.dlis') as files:
    for f in files:
        for frame in f.frames:
            curves = frame.curves()
            # Do something with the curves

```
and from a LIS-file:

```python
from dlisio import lis

with lis.load('myfile.lis') as files:
    for f in files:
        for format_spec in f.data_format_specs():
            curves = lis.curves(f, format_spec)
            # Do something with the curves
```

In both cases the curves are returned as [structured
numpy.ndarray](https://numpy.org/doc/stable/user/basics.rec.html) with the
curve mnemonics as field names (column names).

## Build dlisio ##

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

## Contributing ##

We welcome all kinds of contributions, including code, bug reports, issues,
feature requests, and documentation. The preferred way of submitting a
contribution is to either make an
[issue](https://github.com/equinor/dlisio/issues) on github or by forking the
project on github and making a pull request.
