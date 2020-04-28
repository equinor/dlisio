"""
Testing frame.curves() and channel.curves() functions and all the
helper functionality
"""
import pytest
import numpy as np
from datetime import datetime

import dlisio
from dlisio import core
from dlisio.plumbing import mkunique

def load_curves(fpath):
    with dlisio.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-REPRCODE', 10, 0)
        curves = frame.curves()
        return curves

def makeframe():
    frame = dlisio.plumbing.Frame()
    frame.name = 'MAINFRAME'
    frame.origin = 0
    frame.copynumber = 0

    time0 = dlisio.plumbing.Channel()
    time0.name = 'TIME'
    time0.origin = 0
    time0.copynumber = 0
    attic = {
        'DIMENSION': [1],
        'REPRESENTATION-CODE' : [2] # f4
    }
    time0.attic = attic

    tdep = dlisio.plumbing.Channel()
    tdep.name = 'TDEP'
    tdep.origin = 0
    tdep.copynumber = 0
    attic = {
        'DIMENSION': [2],
        'REPRESENTATION-CODE' : [13] # i2
    }
    tdep.attic = attic

    time1 = dlisio.plumbing.Channel()
    time1.name = 'TIME'
    time1.origin = 1
    time1.copynumber = 0
    attic = {
        'DIMENSION'           : [1],
        'REPRESENTATION-CODE' : [13], # i2
    }
    time1.attic = attic

    #frame.channels = [time0, tdep, time1]
    frame.attic = {
        'CHANNELS' : [core.obname(time0.origin, time0.copynumber, time0.name),
                      core.obname(tdep.origin,  tdep.copynumber,  tdep.name),
                      core.obname(time1.origin, time1.copynumber, time1.name)]
    }

    logicalfile = dlisio.dlis(None, [], [], [])
    logicalfile.indexedobjects['FRAME'] = { frame.fingerprint : frame }
    logicalfile.indexedobjects['CHANNEL'] = {
            time0.fingerprint : time0,
            tdep.fingerprint  : tdep,
            time1.fingerprint : time1,
    }
    for objs in logicalfile.indexedobjects.values():
        for obj in objs.values():
            obj.logicalfile = logicalfile

    frame.link()
    return frame

def test_curves_are_copy(f):
    # All channel.curves() really does is to slice the full frame array
    # returned by frame.curves(). Make sure the returned slice is a copy not a
    # view.  Returning a view makes it impossible to free up any memory from
    # the original array, hence holding on to way more memory than needed.

    channel = f.object('CHANNEL', 'CHANN1')
    curves = channel.curves()
    assert curves.flags['OWNDATA']

def test_curves_values(f):
    frame = f.object('FRAME', 'FRAME1', 10, 0)
    curves = frame.curves()

    base = np.array([
        [[1, 2],   [3, 4],   [5, 6]],
        [[7, 8],   [9, 10],  [11, 12]],
        [[13, 14], [15, 16], [17, 18]],
        [[19, 20], [21, 22], [23, 24]]
    ])

    val = base + 0
    np.testing.assert_array_equal(curves['CHANN1'][0], val)
    np.testing.assert_array_equal(curves[0]['CHANN1'], val)

    val = base + 256
    np.testing.assert_array_equal(curves['CHANN2'][0], val)
    np.testing.assert_array_equal(curves[0]['CHANN2'], val)

    val = base + 512
    np.testing.assert_array_equal(curves['CHANN1'][1], val)
    np.testing.assert_array_equal(curves[1]['CHANN1'], val)

    val = base + 768
    np.testing.assert_array_equal(curves['CHANN2'][1], val)
    np.testing.assert_array_equal(curves[1]['CHANN2'], val)

    val = base + 1024
    np.testing.assert_array_equal(curves['CHANN1'][2], val)
    np.testing.assert_array_equal(curves[2]['CHANN1'], val)

    val = base + 1280
    np.testing.assert_array_equal(curves['CHANN2'][2], val)
    np.testing.assert_array_equal(curves[2]['CHANN2'], val)

def test_two_various_fdata_in_one_iflr():
    fpath = 'data/chap4-7/iflr/two-various-fdata-in-one-iflr.dlis'

    curves = load_curves(fpath)
    assert curves[0][1] == datetime(1971, 3, 21, 18, 4, 14, 386000)
    assert curves[0][2] == "VALUE"
    assert curves[0][3] == 89
    assert curves[1][1] == datetime(1970, 3, 21, 18, 4, 14, 0)
    assert curves[1][2] == "SECOND-VALUE"
    assert curves[1][3] == -89

def test_framenos_out_of_order_one_frame():
    fpath = 'data/chap4-7/iflr/out-of-order-framenos-one-frame.dlis'
    curves = load_curves(fpath)
    np.testing.assert_array_equal(curves['FRAMENO'], [2, 1])
    assert curves[0][1] == True
    assert curves[1][1] == False

def test_framenos_out_of_order_two_frames():
    fpath = 'data/chap4-7/iflr/out-of-order-framenos-two-frames.dlis'
    curves = load_curves(fpath)
    np.testing.assert_array_equal(curves['FRAMENO'], [2, 1])
    assert curves[0][1] == True
    assert curves[1][1] == False

def test_framenos_out_of_order_two_frames_multidata():
    fpath = 'data/chap4-7/iflr/out-of-order-framenos-two-frames-multifdata.dlis'
    curves = load_curves(fpath)
    np.testing.assert_array_equal(curves['FRAMENO'], [3, 4, 1, 2])
    assert curves[0][1] == True
    assert curves[1][1] == False
    assert curves[2][1] == False
    assert curves[3][1] == True

def test_framenos_missing_numbers():
    fpath = 'data/chap4-7/iflr/missing-framenos.dlis'
    curves = load_curves(fpath)
    np.testing.assert_array_equal(curves['FRAMENO'], [2, 4])
    assert curves[0][1] == True
    assert curves[1][1] == False

def test_framenos_duplicated():
    fpath = 'data/chap4-7/iflr/duplicate-framenos.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == curves[0][1]
    assert curves[0][0] == True
    assert curves[1][1] == False

def test_framenos_duplicated_same_frame():
    fpath = 'data/chap4-7/iflr/duplicate-framenos-same-frames.dlis'
    curves = load_curves(fpath)
    np.testing.assert_array_equal(curves[0], curves[1])

def test_dimensions():
    fpath = 'data/chap4-7/iflr/multidimensions-ints-various.dlis'

    with dlisio.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-DIMENSION', 11, 0)
        curves = frame.curves()

        np.testing.assert_array_equal(curves[0][1], [[1, 2, 3], [4, 5, 6]])
        np.testing.assert_array_equal(curves[0][2], [[1, 2], [3, 4], [5, 6]])

        arr2 = [
            [[1, 2],   [3, 4],   [5, 6]],
            [[7, 8],   [9, 10],  [11, 12]],
            [[13, 14], [15, 16], [17, 18]],
            [[19, 20], [21, 22], [23, 24]]
        ]
        np.testing.assert_array_equal(curves[0][3], arr2)
        np.testing.assert_array_equal(curves[0][4], [[1, 2]])
        np.testing.assert_array_equal(curves[0][5], [[1], [2]])
        np.testing.assert_array_equal(curves[0][6], [[1]])
        np.testing.assert_array_equal(curves[0][7], [1, 2, 3, 4])

def test_dimensions_tuple():
    fpath = 'data/chap4-7/iflr/multidimensions-validated.dlis'

    with dlisio.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-VALIDATE', 10, 0)
        curves = frame.curves()

        assert curves[0][1].size == 3

        assert curves[0][1][0] == (56, 0.0625, 0.0625)
        assert curves[0][1][1] == (43, 0.0625, 0.0625)
        assert curves[0][1][2] == (71, 0.5, 0.5)

def test_dimensions_in_multifdata():
    fpath = 'data/chap4-7/iflr/multidimensions-multifdata.dlis'

    with dlisio.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-DIMENSION', 11, 0)
        curves = frame.curves()

        assert curves.shape == (2,)

        np.testing.assert_array_equal(curves[0][1], [[1, 2, 3], [4, 5, 6]])
        np.testing.assert_array_equal(curves[1][1], [[7, 8, 9], [10, 11, 12]])

def test_duplicated_mnemonics_get_unique_labels():
    frame = makeframe()
    assert 'ifDDD' == frame.fmtstr()
    assert ('FRAMENO', 'TIME.0.0', 'TDEP', 'TIME.1.0') == frame.dtype().names

def test_duplicated_mnemonics_dtype_supports_buffer_protocol():
    # Getting a buffer from a numpy array adds a :name: field after the label
    # name, and forbids the presence of :. Unfortunately, the full visible
    # (non-whitespace) ascii set is legal for the RP66 IDENT type, so in theory
    # it's possible that a similar mnemonic can be legally present.
    #
    # In practice, this is unlikely to be a problem. By default, dlisio uses
    # the full stop (.) as a separator, but for particularly nasty files this
    # would collide with a different channel mnemonic in the same frame. A
    # possible fix could be to use a blank character for mnemonic-origin-copy
    # separation, or lowercase letters (which are not supposed to be a part of
    # the IDENT type, but dlisio imposes no such restriction)
    #
    # https://github.com/equinor/dlisio/pull/97
    frame = makeframe()
    _ = memoryview(np.zeros(1, dtype = frame.dtype()))

def test_duplicated_signatures(f, assert_log):
    frame = f.object('FRAME', 'FRAME1')

    frame.channels[1].name       = frame.channels[0].name
    frame.channels[1].origin     = frame.channels[0].origin
    frame.channels[1].copynumber = frame.channels[0].copynumber

    with pytest.raises(Exception):
        _ = frame.curves()
    assert_log("duplicated mnemonics")

    curves = frame.curves(strict=False)
    names  = curves.dtype.names

    assert names == ('FRAMENO', 'CHANN1.10.0(0)', 'CHANN1.10.0(1)')

def test_mkunique():
    types    = [("TIME.0.0"   , "f2"),
                ("TDEP.0.0"   , "f4"),
                ("TDEP.0.0"   , "i1"),
                ("TDEP.0.1"   , "i2"),
                ("TIME.0.0"   , "i4"),
                ("TIME.0.0"   , "i4"),
    ]
    expected = [("TIME.0.0(0)", "f2"),
                ("TDEP.0.0(0)", "f4"),
                ("TDEP.0.0(1)", "i1"),
                ("TDEP.0.1"   , "i2"),
                ("TIME.0.0(1)", "i4"),
                ("TIME.0.0(2)", "i4"),
    ]
    assert expected == mkunique(types)


def test_channel_order():
    frame = makeframe()

    ref = [("TIME", 0), ("TDEP", 0), ("TIME", 1)]

    for i, ch in enumerate(frame.channels):
        assert ch.name   == ref[i][0]
        assert ch.origin == ref[i][1]


def test_dtype():
    frame = makeframe()
    assert frame.dtype() == np.dtype([('FRAMENO', np.int32),
                                      ('TIME.0.0', np.float32),
                                      ('TDEP', np.int16, (2,)),
                                      ('TIME.1.0', np.int16),
                                      ])

def test_dtype_fmt_instance():
    frame = makeframe()
    frame.dtype_fmt = 'x-{:s} {:d}~{:d}'

    # fmtstr is unchanged
    assert 'ifDDD' == frame.fmtstr()
    expected_names = ('FRAMENO', 'x-TIME 0~0', 'TDEP', 'x-TIME 1~0')
    assert expected_names == frame.dtype().names

def test_dtype_fmt_class():
    original = dlisio.plumbing.Frame.dtype_format

    try:
        # change dtype before the object itself is constructed, so it
        dlisio.plumbing.Frame.dtype_format = 'x-{:s} {:d}~{:d}'
        frame = makeframe()
        expected_names = ('FRAMENO', 'x-TIME 0~0', 'TDEP', 'x-TIME 1~0')
        assert expected_names == frame.dtype().names
        assert 'ifDDD' == frame.fmtstr()

    finally:
        # even if the test fails, make sure the format string is reset to its
        # default, to not interfere with other tests
        dlisio.plumbing.Frame.dtype_format = original

@pytest.mark.parametrize('fmt', [
    ("x-{:d}.{:s}.{:d}"),
    ("x-{:s}.{:d}.{:d}.{:d}"),
])
def test_dtype_wrong_fmt(fmt, assert_log):
    frame = makeframe()

    frame.dtype_fmt = fmt
    with pytest.raises(Exception):
        _ = frame.dtype().names
    assert_log("rich label")


def test_channel_curves():
    fpath = 'data/chap4-7/iflr/all-reprcodes.dlis'
    with dlisio.load(fpath) as (f, *_):
        channel = f.object('CHANNEL', 'CH26', 10, 0)
        curves = channel.curves()
        assert curves[0] == True

        channel = f.object('CHANNEL', 'CH22', 10, 0)
        curves22 = channel.curves()
        assert curves22[0] == 16777217

        frame_curves = load_curves(fpath)
        assert frame_curves['CH22'] == curves22

def test_channel_without_frame(assert_info):
    channel = dlisio.plumbing.Channel()
    assert channel.curves() == None
    assert_info('no recorded curve-data')

def test_channel_fmt():
    ch1 = dlisio.plumbing.Channel()
    ch1.name = 'ch1'
    ch1.origin = 0
    ch1.copynumber = 0
    ch1.attic = {
        'DIMENSION': [5],
        'REPRESENTATION-CODE': [11],
    }

    ch2 = dlisio.plumbing.Channel()
    ch2.name = 'ch2'
    ch2.origin = 0
    ch2.copynumber = 0
    ch2.attic = {
        'DIMENSION': [2, 2],
        'REPRESENTATION-CODE': [3],
    }

    ch3 = dlisio.plumbing.Channel()
    ch3.name = 'ch3'
    ch3.origin = 0
    ch3.copynumber = 0
    ch3.attic = {
        'DIMENSION': [4, 2],
        'REPRESENTATION-CODE': [26],
    }

    ch4 = dlisio.plumbing.Channel()
    ch4.name = 'ch4'
    ch4.origin = 0
    ch4.copynumber = 0
    ch4.attic = {
        'DIMENSION': [1],
        'REPRESENTATION-CODE': [17],
    }

    ch5 = dlisio.plumbing.Channel()
    ch5.name = 'ch5'
    ch5.origin = 0
    ch5.copynumber = 0
    ch5.attic = {
        'DIMENSION': [2, 3, 1],
        'REPRESENTATION-CODE': [12],
    }

    frame = dlisio.plumbing.Frame()
    frame.name = 'fr'
    frame.origin = 0
    frame.copynumber = 0
    frame.attic = {
        'CHANNELS': [
            core.obname(ch1.origin, ch1.copynumber, ch1.name),
            core.obname(ch2.origin, ch2.copynumber, ch2.name),
            core.obname(ch3.origin, ch3.copynumber, ch3.name),
            core.obname(ch4.origin, ch4.copynumber, ch4.name),
            core.obname(ch5.origin, ch5.copynumber, ch5.name),
        ]
    }

    logicalfile = dlisio.dlis(None, [], [], [])
    logicalfile.indexedobjects['FRAME'] = {
        frame.fingerprint: frame
    }

    logicalfile.indexedobjects['CHANNEL'] = {
        ch1.fingerprint: ch1,
        ch2.fingerprint: ch2,
        ch3.fingerprint: ch3,
        ch4.fingerprint: ch4,
        ch5.fingerprint: ch5,
    }
    frame.logicalfile = logicalfile
    ch1.logicalfile = logicalfile
    ch2.logicalfile = logicalfile
    ch3.logicalfile = logicalfile
    ch4.logicalfile = logicalfile
    ch5.logicalfile = logicalfile

    pre_fmt, ch_fmt, post_fmt = frame.fmtstrchannel(ch3)
    assert pre_fmt == "CCCCCbbbb"
    assert ch_fmt == "qqqqqqqq"
    assert post_fmt == "Ldddddd"


def test_channel_no_dimension(assert_log):
    ch = dlisio.plumbing.Channel()
    ch.name = 'CH'
    ch.origin = 0
    ch.copynumber = 0
    ch.attic = {'REPRESENTATION-CODE': [17]}

    with pytest.raises(ValueError) as exc:
        ch.fmtstr()
    assert "channel.dimension is invalid" in str(exc.value)

    ch.attic['DIMENSION'] = [1]
    assert ch.fmtstr() == "L"


def test_frame_index():
    frame = makeframe()
    frame.attic['INDEX-TYPE'] = ['DECREASING']

    assert frame.index == frame.channels[0].name

def test_frame_index_absent(assert_info):
    frame = makeframe()
    assert frame.index == 'FRAMENO'

def test_frame_index_absent_nochannels(assert_info):
    frame = dlisio.plumbing.Frame()
    frame.attic['INDEX-TYPE'] = ['DECREASING']

    assert frame.index is None
    assert_info('Frame has no channels')

