#!/usr/bin/env python3

import os
import skbuild
import setuptools

class get_pybind_include(object):
    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        # postpone importing pybind11 until building actually happens
        import pybind11
        return pybind11.get_include(self.user)

def src(x):
    root = os.path.dirname( __file__ )
    return os.path.abspath(os.path.join(root, x))

def getversion():
    pkgversion = { 'version': '0.0.0' }
    versionfile = 'dlisio/version.py'

    if not os.path.exists(versionfile):
        return {
            'use_scm_version': {
                # look for git in ../
                'root': '..',
                'relative_to' : __file__,
                # write to ./python
                'write_to'    : os.path.join(src(''), versionfile),
            }
        }

    import ast
    with open(versionfile) as f:
        root = ast.parse(f.read())

    for node in ast.walk(root):
        if not isinstance(node, ast.Assign): continue
        if len(node.targets) == 1 and node.targets[0].id == 'version':
            pkgversion['version'] = node.value.s

    return pkgversion

pybind_includes = [
    str(get_pybind_include()),
    str(get_pybind_include(user = True))
]

skbuild.setup(
    name = 'dlisio',
    description = 'DLIS v1',
    long_description = 'DLIS v1',
    url = 'https://github.com/equinor/dlisio',
    packages = ['dlisio', 'dlisio.dlis', 'dlisio.lis', 'dlisio.common', 'dlisio.dlis.utils'],
    license = 'LGPL-3.0',
    platforms = 'any',
    install_requires = ['numpy'],
    setup_requires = ['setuptools >= 28',
                      'pybind11 >= 2.3',
                      'setuptools_scm',
                      'pytest-runner',
    ],
    tests_require = ['pytest'],
    # we're building with the pybind11 fetched from pip. Since we don't rely on
    # a cmake-installed pybind there's also no find_package(pybind11) -
    # instead, the get include dirs from the package and give directly from
    # here
    cmake_args = [
        '-DPYBIND11_INCLUDE_DIRS=' + ';'.join(pybind_includes),
        # we can safely pass OSX_DEPLOYMENT_TARGET as it's ignored on
        # everything not OS X. We depend on C++11, which makes our minimum
        # supported OS X release 10.9
        '-DCMAKE_OSX_DEPLOYMENT_TARGET=10.9',
    ],
    # skbuild's test imples develop, which is pretty obnoxious instead, use a
    # manually integrated pytest.
    cmdclass = { 'test': setuptools.command.test.test },
    **getversion()
)
