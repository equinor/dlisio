#!/usr/bin/env python3

import os
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class get_pybind_include(object):
    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        # postpone importing pybind11 until building actually happens
        import pybind11
        return pybind11.get_include(self.user)


class BuildExt(build_ext):
    """
    A custom build extension for adding compiler-specific, taken from
    https://github.com/pybind/python_example/blob/master/setup.py
    """
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': ['-std=c++11'],
    }

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])

        distver = self.distribution.get_version()
        if ct == 'unix':
            opts.append('-DVERSION_INFO="{}"'.format(distver))
            opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"{}\\"'.format(distver))

        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


def getversion():
    pkgversion = { 'version': '0.0.0' }
    versionfile = 'dlisio/version.py'

    if not os.path.exists(versionfile):
        return {
            'use_scm_version': {
                'relative_to' : os.path.dirname(os.path.abspath(__file__)),
                'write_to'    : versionfile
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


setup(
    name = 'dlisio',
    description = 'DLIS v1',
    long_description = 'DLIS v1',
    url = 'https://github.com/equinor/dlisio',
    packages = ['dlisio', 'dlisio.objects'],
    license = 'LGPL-3.0',
    ext_modules = [
        Extension('dlisio.core',
            sources = [
                'dlisio/ext/core.cpp',
            ],
            include_dirs = ['../lib/include',
                            '../lib/extension',
                            '../external/mpark',
                            '../external/mio',
                            get_pybind_include(),
                            get_pybind_include(user=True),
            ],
            libraries = ['dlisio', 'dlisio-extension'],
        )
    ],
    platforms = 'any',
    install_requires = ['numpy'],
    setup_requires = ['setuptools >= 28',
                      'pytest-runner',
                      'pybind11 >= 2.2',
                      'setuptools_scm',
    ],
    tests_require = ['pytest'],
    cmdclass = { 'build_ext': BuildExt },
    **getversion()
)
