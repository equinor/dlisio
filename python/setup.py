#!/usr/bin/env python3

from setuptools import setup, Extension

class get_pybind_include(object):
    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        # postpone importing pybind11 until building actually happens
        import pybind11
        return pybind11.get_include(self.user)

setup(
    name = 'dlisio',
    description = 'DLIS v1',
    long_description = 'DLIS v1',
    url = 'https://github.com/Statoil/dlisio',
    packages = ['dlisio'],
    license = 'LGPL-3.0',
    ext_modules = [
        Extension('dlisio.core',
            sources = ['dlisio/core.cpp'],
            include_dirs = ['../lib/include',
                            get_pybind_include(),
                            get_pybind_include(user=True),
            ],
            libraries = ['dlisio'],
        )
    ],
    platforms = 'any',
    install_requires = ['numpy'],
    setup_requires = ['setuptools >= 28', 'pytest-runner', 'pybind11'],
    tests_require = ['pytest'],
)
