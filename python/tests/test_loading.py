"""
Testing general loading functionality
"""

import pytest

import shutil
import os

import dlisio

def test_filehandles_closed(tmpdir):
    # Check that both the memory mapping and regular filehandle is closed
    # property. This test uses the fact that os.remove fails on windows if the
    # file is in use as a proxy for testing that dlisio dont leak filehandles.
    # From the python docs [1]:
    #
    #   On Windows, attempting to remove a file that is in use causes an
    #   exception to be raised; on Unix, the directory entry is removed but the
    #   storage allocated to the file is not made available until the original
    #   file is no longer in use.
    #
    # On linux on the other hand, os.remove does not fail even if there are
    # open filehandles, hence this test only makes sence on Windows.
    #
    # [1] https://docs.python.org/3/library/os.html

    # Copy the test file to a tmpdir in order to make this test reliable.
    tmp = str(tmpdir.join('206_05a-_3_DWL_DWL_WIRE_258276498.DLIS'))
    shutil.copyfile('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS', tmp)

    with dlisio.load(tmp) as _:
        pass

    os.remove(tmp)

def test_filehandles_closed_when_load_fails(tmpdir):
    # Check that both the memory mapping and regular filehandle is closed
    # property. This test uses the fact that os.remove fails on windows if the
    # file is in use as a proxy for testing that dlisio dont leak filehandles.
    # From the python docs [1]:
    #
    #   On Windows, attempting to remove a file that is in use causes an
    #   exception to be raised; on Unix, the directory entry is removed but the
    #   storage allocated to the file is not made available until the original
    #   file is no longer in use.
    #
    # On linux on the other hand, os.remove does not fail even if there are
    # open filehandles, hence this test only makes sence on Windows.
    #
    # [1] https://docs.python.org/3/library/os.html

    # Copy the test files to a tmpdir in order to make this test reliable.
    offsets = str(tmpdir.join('offsets'))
    shutil.copyfile('data/chap2/too-small-record.dlis', offsets)

    extract = str(tmpdir.join('extract'))
    shutil.copyfile('data/chap2/padbytes-bad.dlis', extract)

    fdata = str(tmpdir.join('fdata'))
    shutil.copyfile('data/chap3/implicit/fdata-encrypted.dlis', fdata)

    # dlisio.load fails at core.findoffsets
    with pytest.raises(RuntimeError):
        _ =  dlisio.load(offsets)

    # dlisio.load fails at core.stream.extract
    with pytest.raises(RuntimeError):
        _ =  dlisio.load(extract)

    # dlisio.load fails at core.findfdata
    with pytest.raises(UnicodeDecodeError):
        _ =  dlisio.load(fdata)

    # If dlisio have properly closed the files, removing them should work.
    os.remove(offsets)
    os.remove(extract)
    os.remove(fdata)

def test_context_manager(multifpath):
    f, *_ = dlisio.load(multifpath)
    _ = f.fileheader
    f.close()

    files = dlisio.load(multifpath)
    for f in files:
        _ = f.fileheader
        f.close()

    f, *files = dlisio.load(multifpath)
    _ = f.fileheader
    for g in files:
        _ = g.fileheader
        g.close()

def test_context_manager_with(multifpath):
    with dlisio.load(multifpath) as (f, *_):
        _ = f.fileheader

    with dlisio.load(multifpath) as files:
        for f in files:
            _ = f.fileheader

    with dlisio.load(multifpath) as (f, *files):
        _ = f.fileheader
        for g in files:
            _ = g.fileheader

