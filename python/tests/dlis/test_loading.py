"""
Testing general loading functionality
"""

import pytest

import shutil
import os

import dlisio
from dlisio import dlis

def test_filehandles_closed(tmpdir):
    # Check that we don't leak open filehandles
    #
    # This test uses the fact that os.remove fails on windows if the file is in
    # use as a proxy for testing that dlisio doesn't leak filehandles.  From the
    # python docs [1]:
    #
    #   On Windows, attempting to remove a file that is in use causes an
    #   exception to be raised; on Unix, the directory entry is removed but the
    #   storage allocated to the file is not made available until the original
    #   file is no longer in use.
    #
    # On linux on the other hand, os.remove does not fail even if there are
    # open filehandles, hence this test only makes sense on Windows.
    #
    # [1] https://docs.python.org/3/library/os.html

    # Copy the test file to a tmpdir in order to make this test reliable.
    tmp = str(tmpdir.join('206_05a-_3_DWL_DWL_WIRE_258276498.DLIS'))
    shutil.copyfile('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS', tmp)

    many_logical = str(tmpdir.join('many_logical'))
    shutil.copyfile('data/chap4-7/many-logical-files.dlis', many_logical)

    offsets_error_escape = str(tmpdir.join('error_escape_zeroed'))
    shutil.copyfile('data/chap2/zeroed-in-1st-lr.dlis', offsets_error_escape)

    with dlis.load(tmp) as _:
        pass

    with dlis.load(many_logical) as fls:
        assert len(fls) == 3

    # error happens in 1st LF, but is escaped
    errorhandler = dlisio.common.ErrorHandler(
        critical=dlisio.common.Actions.LOG_ERROR)
    with dlis.load(offsets_error_escape, error_handler=errorhandler):
        pass

    os.remove(tmp)
    os.remove(many_logical)
    os.remove(offsets_error_escape)

def test_filehandles_closed_when_load_fails(tmpdir):
    # Check that we don't leak open filehandles on failure
    #
    # This test uses the fact that os.remove fails on windows if the file is in
    # use as a proxy for testing that dlisio doesn't leak filehandles. From the
    # python docs [1]:
    #
    #   On Windows, attempting to remove a file that is in use causes an
    #   exception to be raised; on Unix, the directory entry is removed but the
    #   storage allocated to the file is not made available until the original
    #   file is no longer in use.
    #
    # On linux on the other hand, os.remove does not fail even if there are
    # open filehandles, hence this test only makes sense on Windows.
    #
    # [1] https://docs.python.org/3/library/os.html

    # Copy the test files to a tmpdir in order to make this test reliable.
    findvrl = str(tmpdir.join('findvrl'))
    shutil.copyfile('data/chap2/nondlis.txt', findvrl)

    offsets = str(tmpdir.join('offsets'))
    shutil.copyfile('data/chap2/wrong-lrhs.dlis', offsets)

    extract = str(tmpdir.join('extract'))
    shutil.copyfile('data/chap2/padbytes-bad.dlis', extract)

    fdata = str(tmpdir.join('fdata'))
    shutil.copyfile('data/chap3/implicit/fdata-broken-obname.dlis', fdata)

    many_logical = str(tmpdir.join('many_logical'))
    shutil.copyfile('data/chap4-7/many-logical-files-error-in-last.dlis',
                    many_logical)

    # dlis.load fails at findvrl
    with pytest.raises(RuntimeError):
        _ =  dlis.load(findvrl)

    # dlis.load fails at core.findoffsets
    with pytest.raises(RuntimeError):
        _ =  dlis.load(offsets)

    # dlis.load fails at core.stream.extract
    with pytest.raises(RuntimeError):
        _ =  dlis.load(extract)

    # dlis.load fails at core.findfdata
    with pytest.raises(RuntimeError):
        _ =  dlis.load(fdata)

    # dlis.load fails, but 1 LF was already processed successfully
    with pytest.raises(RuntimeError):
        _ =  dlis.load(many_logical)

    # If dlisio has properly closed the files, removing them should work.
    os.remove(findvrl)
    os.remove(offsets)
    os.remove(extract)
    os.remove(fdata)
    os.remove(many_logical)

def test_context_manager():
    path = 'data/chap4-7/many-logical-files.dlis'
    batch = dlis.load(path)
    f, *_ = batch
    _ = f.fileheader
    batch.close()

    files = dlis.load(path)
    for f in files:
        _ = f.fileheader
        f.close()

    f, *files = dlis.load(path)
    _ = f.fileheader
    f.close()
    for g in files:
        _ = g.fileheader
        g.close()

def test_context_manager_with():
    path = 'data/chap4-7/many-logical-files.dlis'
    with dlis.load(path) as (f, *_):
        _ = f.fileheader

    with dlis.load(path) as files:
        for f in files:
            _ = f.fileheader

    with dlis.load(path) as (f, *files):
        _ = f.fileheader
        for g in files:
            _ = g.fileheader

def test_load_nonexisting_file():
    with pytest.raises(OSError) as exc:
        _ = dlis.load("this_file_does_not_exist.dlis")
    msg = "'this_file_does_not_exist.dlis' is not an existing regular file"
    assert msg in str(exc.value)

def test_load_directory():
    with pytest.raises(OSError) as exc:
        _ = dlis.load(".")
    msg = "'.' is not an existing regular file"
    assert msg in str(exc.value)

def test_invalid_attribute_in_load():
    # Error in one attribute shouldn't prevent whole file from loading
    # This is based on common enough error in creation time property in origin.
    path = 'data/chap4-7/invalid-date-in-origin.dlis'
    with dlis.load(path) as files:
        for f in files:
            f.load()
