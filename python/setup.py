#!/usr/bin/env python3

from setuptools import setup, Extension

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
          include_dirs = ['../lib/include'],
          libraries = ['dlisio'],
        )
    ],
    platforms = 'any',
    install_requires = ['numpy'],
    setup_requires = ['setuptools >= 28', 'pytest-runner'],
    tests_require = ['pytest'],
)
