"""
Testing error handler on various levels of representation
(user-facade functionality and underlying logical format)
"""

import pytest
import os
import numpy as np

from dlisio import dlis

from dlisio.common import ErrorHandler, Actions

errorhandler = ErrorHandler(critical = Actions.LOG_ERROR)

def test_custom_action():
    def custom(msg):
        raise ValueError("custom message: "+msg)

    path = 'data/chap2/truncated-in-lrsh-vr-over.dlis'
    errorhandler = ErrorHandler(critical=custom)
    with pytest.raises(ValueError) as excinfo:
        _ = dlis.load(path, error_handler=errorhandler)
    assert "custom message: \n" in str(excinfo.value)
    assert "File truncated in Logical Record Header" in str(excinfo.value)

def test_unescapable_notdlis(assert_error):
    path = 'data/chap2/nondlis.txt'
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load(path, error_handler=errorhandler)
    assert "could not find visible record envelope" in str(excinfo.value)

def test_truncated_in_data(assert_error):
    path = 'data/chap2/truncated-in-second-lr.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("File truncated in Logical Record Segment")
        assert len(f.channels) == 1

def test_tif_truncated_in_data(assert_error):
    path = 'data/tif/layout/truncated-in-data.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("File truncated in Logical Record Segment")

def test_truncated_in_lrsh(assert_error):
    path = 'data/chap2/truncated-in-lrsh.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("unexpected EOF when reading record")
        assert len(f.channels) == 1

def test_truncated_after_lrsh_new_lf(assert_error):
    path = 'data/chap2/lf-truncated-after-lrsh.dlis'
    with dlis.load(path, error_handler=errorhandler) as batch:
        assert_error("File truncated in Logical Record Segment")
        assert len(batch) == 2

def test_truncated_lr_missing_lrs_vr_over(assert_error):
    path = 'data/chap2/truncated-lr-no-lrs-vr-over.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("last logical record segment expects successor")
        assert len(f.channels) == 0

def test_zeroed_before_lrs(assert_error):
    path = 'data/chap2/zeroed-in-1st-lr.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("Too short logical record")
        assert len(f.channels) == 0

def test_zeroed_before_vr(assert_error):
    path = 'data/chap2/zeroed-in-2nd-lr.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("Incorrect format version")
        assert len(f.channels) == 1

def test_tif_padding(assert_error):
    path = 'data/tif/irregular/padding.dlis'
    with dlis.load(path, error_handler=errorhandler) as files:
        assert_error("File might be padded")
        assert len(files) == 2

def test_extract_broken_padbytes(assert_error):
    path = 'data/chap2/padbytes-bad.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("bad segment trim")
        valid_obj = f.object("VALID-SET", "VALID-OBJ", 10, 0)
        assert valid_obj

def test_findfdata_bad_obname(assert_error):
    path = 'data/chap3/implicit/fdata-broken-obname.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("fdata record corrupted, error on reading obname")
        assert "T.FRAME-I.DLIS-FRAME-O.3-C.1" in f.fdata_index

def test_curves_broken_fmt(assert_error):
    path = 'data/chap4-7/iflr/broken-fmt.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        frame = f.object('FRAME', 'FRAME-REPRCODE', 10, 0)
        curves = frame.curves()
        assert_error("fmtstr would read past end")
        assert np.array_equal(curves['FRAMENO'], np.array([1, 3]))

def test_parse_objects_unexpected_attribute_in_set(assert_error):
    path = 'data/chap3/explicit/broken-in-set.dlis'
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        assert_error("Construct object sets")
        _ = f.object('VALID-SET', 'VALID-OBJ', 10, 0)
        _ = f.object('GOOOD-SET', 'VALID-OBJ', 10, 0)

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

    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        # value is unclear and shouldn't be trusted
        _ = obj['INVALID']
        assert_error("invalid representation code")


def test_parse_unparsable_record(tmpdir, merge_files_oneLR, assert_error):
    path = os.path.join(str(tmpdir), 'unparsable.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invalid-repcode-no-value.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/empty.dlis.part',
        'data/chap3/object/object2.dlis.part',
        # here must go anything that will be considered unrecoverable
        'data/chap3/objattr/reprcode-invalid-value.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert_error("Action taken: object set parse has been interrupted")

        # value is unclear and shouldn't be trusted
        _ = obj['INVALID']
        assert_error("invalid representation code")

        with pytest.raises(ValueError) as excinfo:
            _ = f.object('VERY_MUCH_TESTY_SET', 'OBJECT2', 1, 1)
        assert "not found" in str(excinfo.value)

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
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
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
    with dlis.load(path, error_handler=errorhandler) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            _ = f.object('REDUNDANT', 'OBJECT', 1, 1)
        assert "Redundant sets are not supported" in str(excinfo.value)

def test_many_logical_files():
    path = "data/chap4-7/many-logical-files-error-in-last.dlis"
    errorhandler = ErrorHandler()
    errorhandler.critical = Actions.LOG_ERROR

    with dlis.load(path, error_handler=errorhandler) as files:
        # last file is not processed
        assert len(files) == 2

        errorhandler.critical = Actions.RAISE
        errorhandler.major    = Actions.RAISE
        errorhandler.minor    = Actions.RAISE
        for f in files:
            with pytest.raises(RuntimeError):
                f.load()

        # define default error handler specially for the first logical file
        errorhandler = ErrorHandler()
        files[0].error_handler = errorhandler

        files[0].load()
        with pytest.raises(RuntimeError):
            files[1].load()


@pytest.fixture
def create_very_broken_file(tmpdir, merge_files_oneLR, merge_files_manyLR):
    valid = os.path.join(str(tmpdir), 'valid.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invalid-repcode-no-value.dlis.part',
        'data/chap3/object/object.dlis.part',
        # will cause issues on attribute access
        'data/chap3/objattr/empty.dlis.part',
        'data/chap3/object/object2.dlis.part',
        # will cause issues on parsing
        'data/chap3/objattr/reprcode-invalid-value.dlis.part'
    ]
    merge_files_oneLR(valid, content)

    content = [
        valid,
        'data/chap3/sul.dlis.part', # will cause issues on load
    ]

    def create_file(path):
        merge_files_manyLR(path, content)
    return create_file


def test_complex(create_very_broken_file, tmpdir):

    path = os.path.join(str(tmpdir), 'complex.dlis')
    create_very_broken_file(path)

    errorhandler = ErrorHandler()

    with pytest.raises(RuntimeError):
        with dlis.load(path, error_handler=errorhandler) as (f, *_):
            pass

    # escape errors on load
    errorhandler.critical = Actions.LOG_ERROR
    with dlis.load(path, error_handler=errorhandler) as (f, *_):

        # fail again on parsing objects not parsed on load
        errorhandler.critical = Actions.RAISE
        with pytest.raises(RuntimeError) as excinfo:
            _ = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert "object set" in str(excinfo.value)

        # escape errors on parsing
        errorhandler.critical = Actions.LOG_ERROR
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)

        errorhandler.critical = Actions.RAISE
        # set is parsed, but user should get error anyway
        with pytest.raises(RuntimeError) as excinfo:
            _ = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert "object set" in str(excinfo.value)

        # fail on attribute access
        errorhandler.critical = Actions.RAISE
        with pytest.raises(RuntimeError):
            _ = obj['INVALID']

        # retrieve whatever value from errored attribute
        errorhandler.critical = Actions.LOG_ERROR
        _ = obj['INVALID']
