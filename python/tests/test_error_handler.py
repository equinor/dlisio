"""
Testing error handler on various levels of representation
(user-facade functionality and underlying logical format)
"""

import pytest
import os

import dlisio

from dlisio.errors import ErrorHandler, Actions

errorhandler = ErrorHandler(critical = Actions.LOG_ERROR)

# TODO: test_errors_explicit (let users examine the errors regardless of escape
# level set)

# TODO: test mix (do not fail on truncation, but fail on bad attribute access)

def test_unescapable_notdlis(assert_error):
    path = 'data/chap2/nondlis.txt'
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load(path, error_handler=errorhandler)
    assert "could not find visible record envelope" in str(excinfo.value)

def test_truncated_in_data(assert_error):
    path = 'data/chap2/truncated-in-second-lr.dlis'
    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("File truncated in Logical Record Segment")
        assert len(f.channels) == 1

def test_tif_truncated_in_data(assert_error):
    path = 'data/tif/layout/truncated-in-data.dlis'
    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("File truncated in Logical Record Segment")

def test_truncated_in_lrsh(assert_error):
    path = 'data/chap2/truncated-in-lrsh.dlis'
    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("unexpected EOF when reading record")
        assert len(f.channels) == 1

def test_truncated_after_lrsh_new_lf(assert_error):
    path = 'data/chap2/lf-truncated-after-lrsh.dlis'
    with dlisio.load(path, error_handler=errorhandler) as batch:
        assert_error("File truncated in Logical Record Segment")
        assert len(batch) == 2

def test_truncated_lr_missing_lrs_vr_over(assert_error):
    path = 'data/chap2/truncated-lr-no-lrs-vr-over.dlis'
    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("last logical record segment expects successor")
        assert len(f.channels) == 0

def test_zeroed_before_lrs(assert_error):
    path = 'data/chap2/zeroed-in-1st-lr.dlis'
    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("Too short logical record")
        assert len(f.channels) == 0

def test_zeroed_before_vr(assert_error):
    path = 'data/chap2/zeroed-in-2nd-lr.dlis'
    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("Incorrect format version")
        assert len(f.channels) == 1

def test_extract_broken_padbytes(assert_error):
    path = 'data/chap2/padbytes-bad.dlis'
    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("bad segment trim")
        valid_obj = f.object("VALID-SET", "VALID-OBJ", 10, 0)
        assert valid_obj

# TODO: test_parse_exeptions

def test_parse_critical_escaped(tmpdir, merge_files_oneLR,
                                         assert_error):
    path = os.path.join(str(tmpdir), 'error-on-attribute-access.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invalid-repcode-no-value.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/empty.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        # value is unclear and shouldn't be trusted
        _ = obj['INVALID']
        assert_error("invalid representation code")

def test_parse_major_errored(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'replacement-set.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/replacement.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part'
    ]
    merge_files_oneLR(path, content)

    errorhandler = ErrorHandler(
        major=Actions.RAISE)
    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            _ = f.object('REPLACEMENT', 'OBJECT', 1, 1)
        assert "Replacement sets are not supported" in str(excinfo.value)

def test_parse_minor_errored(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'redundant-set.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/redundant.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part'
    ]
    merge_files_oneLR(path, content)

    errorhandler = ErrorHandler(
        major=Actions.RAISE,
        minor=Actions.RAISE
    )
    with dlisio.load(path, error_handler=errorhandler) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            _ = f.object('REDUNDANT', 'OBJECT', 1, 1)
        assert "Redundant sets are not supported" in str(excinfo.value)
