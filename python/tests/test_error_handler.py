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

# TODO: test_truncated

# TODO: test_extract

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
