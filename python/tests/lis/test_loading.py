"""
Testing general loading functionality. For more information on tests refer to
same tests in dlis section
"""

import pytest

import shutil
import os

from dlisio import lis

def test_filehandles_closed(tmpdir):
    # Copy the test file to a tmpdir in order to make this test reliable.
    tmp = str(tmpdir.join('file'))
    shutil.copyfile('data/lis/layouts/layout_tif_01.lis', tmp)

    with lis.load(tmp) as files:
        assert len(files) == 4

    os.remove(tmp)

def test_filehandles_closed_when_load_fails(tmpdir, assert_error):
    # TODO: add test files for every step that can fail, as in dlis

    tmp = str(tmpdir.join('file'))
    shutil.copyfile('data/lis/layouts/truncated_15.lis', tmp)

    # file is truncated, but 2 LFs was already processed successfully
    with lis.load(tmp) as files:
        assert len(files) == 2
    # TODO: change for explicit raise here as assert_error is nor reliable
    assert_error("Indexing failed")

    os.remove(tmp)

def test_load_nonexisting_file():
    with pytest.raises(OSError) as exc:
        _ = lis.load("this_file_does_not_exist.lis")
    msg = "unable to open file for path this_file_does_not_exist.lis"
    assert msg in str(exc.value)
