"""
Testing general loading functionality
"""

import pytest

import shutil
import os

import dlisio

def test_context_manager():
    path = 'data/chap4-7/many-logical-files.dlis'
    f, *_ = dlisio.load(path)
    _ = f.fileheader
    f.close()

    files = dlisio.load(path)
    for f in files:
        _ = f.fileheader
        f.close()

    f, *files = dlisio.load(path)
    _ = f.fileheader
    for g in files:
        _ = g.fileheader
        g.close()

def test_context_manager_with():
    path = 'data/chap4-7/many-logical-files.dlis'
    with dlisio.load(path) as (f, *_):
        _ = f.fileheader

    with dlisio.load(path) as files:
        for f in files:
            _ = f.fileheader

    with dlisio.load(path) as (f, *files):
        _ = f.fileheader
        for g in files:
            _ = g.fileheader

@pytest.mark.xfail(strict=False)
def test_invalid_attribute_in_load():
    # Error in one attribute shouldn't prevent whole file from loading
    # This is based on common enough error in creation time property in
    # origin.
    # It loads just fine on python 3.5, but fails in higher versions
    path = 'data/chap4-7/invalid-date-in-origin.dlis'
    with dlisio.load(path):
        pass
