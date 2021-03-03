"""
Testing frame.curves() and channel.curves() functions and all the
helper functionality
"""
import pytest
import numpy as np
from datetime import datetime

from dlisio import core
from dlisio import dlis
from dlisio.dlis import mkunique

def load_curves(fpath):
    with dlis.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-REPRCODE', 10, 0)
        curves = frame.curves()
        return curves

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

    with dlis.load(fpath) as (f, *_):
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

    with dlis.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-VALIDATE', 10, 0)
        curves = frame.curves()

        assert curves[0][1].size == 3

        assert curves[0][1][0] == (56, 0.0625, 0.0625)
        assert curves[0][1][1] == (43, 0.0625, 0.0625)
        assert curves[0][1][2] == (71, 0.5, 0.5)

def test_dimensions_in_multifdata():
    fpath = 'data/chap4-7/iflr/multidimensions-multifdata.dlis'

    with dlis.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-DIMENSION', 11, 0)
        curves = frame.curves()

        assert curves.shape == (2,)

        np.testing.assert_array_equal(curves[0][1], [[1, 2, 3], [4, 5, 6]])
        np.testing.assert_array_equal(curves[1][1], [[7, 8, 9], [10, 11, 12]])

def test_duplicated_mnemonics_get_unique_labels():
    fpath = "data/chap4-7/eflr/frames-and-channels/mainframe.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "MAINFRAME")
        assert 'ifDDD' == frame.fmtstr()
        dtype = frame.dtype()

        assert ('FRAMENO', 'TIME.0.0', 'TDEP', 'TIME.1.0') == dtype.names

        fields = [
            'FRAMENO',
            frame.channels[0].fingerprint,
            frame.channels[1].fingerprint,
            frame.channels[2].fingerprint,
        ]

        assert all(x in dtype.fields for x in fields)


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
    fpath = "data/chap4-7/eflr/frames-and-channels/mainframe.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "MAINFRAME")
        _ = memoryview(np.zeros(1, dtype = frame.dtype()))

def test_duplicated_signatures(assert_error):
    fpath = "data/chap4-7/eflr/frames-and-channels/duplicated.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "DUPLICATED")
        with pytest.raises(Exception):
            _ = frame.curves()
        assert_error("duplicated mnemonics")

        curves = frame.curves(strict=False)
        names  = curves.dtype.names

        assert names == ('FRAMENO', 'DUPL.0.0(0)', 'DUPL.0.0(1)')

def test_mkunique():
    types = [
        (("T.CHANNEL-I.TIME-O.0-C.0", "TIME.0.0"), "f2"),
        (("T.CHANNEL-I.TDEP-O.0-C.0", "TDEP.0.0"), "f4"),
        (("T.CHANNEL-I.TDEP-O.0-C.0", "TDEP.0.0"), "i1"),
        (("T.CHANNEL-I.TDEP-O.0-C.1", "TDEP.0.1"), "i2"),
        (("T.CHANNEL-I.TIME-O.0-C.0", "TIME.0.0"), "i4"),
        (("T.CHANNEL-I.TIME-O.0-C.0", "TIME.0.0"), "i4"),
    ]
    expected = [
        (("T.CHANNEL-I.TIME-O.0-C.0(0)", "TIME.0.0(0)"), "f2"),
        (("T.CHANNEL-I.TDEP-O.0-C.0(0)", "TDEP.0.0(0)"), "f4"),
        (("T.CHANNEL-I.TDEP-O.0-C.0(1)", "TDEP.0.0(1)"), "i1"),
        (("T.CHANNEL-I.TDEP-O.0-C.1"   , "TDEP.0.1"   ), "i2"),
        (("T.CHANNEL-I.TIME-O.0-C.0(1)", "TIME.0.0(1)"), "i4"),
        (("T.CHANNEL-I.TIME-O.0-C.0(2)", "TIME.0.0(2)"), "i4"),
    ]
    assert expected == mkunique(types)


def test_channel_order():
    fpath = "data/chap4-7/eflr/frames-and-channels/mainframe.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "MAINFRAME")

        ref = [("TIME", 0), ("TDEP", 0), ("TIME", 1)]

        for i, ch in enumerate(frame.channels):
            assert ch.name   == ref[i][0]
            assert ch.origin == ref[i][1]


def test_dtype():
    fpath = "data/chap4-7/eflr/frames-and-channels/mainframe.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "MAINFRAME")

        dtype = np.dtype([
            ('FRAMENO', np.int32),
            ((frame.channels[0].fingerprint, 'TIME.0.0'), np.float32),
            ((frame.channels[1].fingerprint, 'TDEP'), np.int16, (2,)),
            ((frame.channels[2].fingerprint, 'TIME.1.0'), np.int16),
        ])

        assert frame.dtype() == dtype

def test_dtype_fmt_instance():
    fpath = "data/chap4-7/eflr/frames-and-channels/mainframe.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "MAINFRAME")
        frame.dtype_fmt = 'x-{:s} {:d}~{:d}'

        # fmtstr is unchanged
        assert 'ifDDD' == frame.fmtstr()
        expected_names = ('FRAMENO', 'x-TIME 0~0', 'TDEP', 'x-TIME 1~0')
        assert expected_names == frame.dtype().names

def test_dtype_fmt_class():
    original = dlis.Frame.dtype_format

    try:
        # change dtype before the object itself is constructed, so it
        dlis.Frame.dtype_format = 'x-{:s} {:d}~{:d}'
        fpath = "data/chap4-7/eflr/frames-and-channels/mainframe.dlis"
        with dlis.load(fpath) as (f, *_):
            frame = f.object("FRAME", "MAINFRAME")
            expected_names = ('FRAMENO', 'x-TIME 0~0', 'TDEP', 'x-TIME 1~0')
            assert expected_names == frame.dtype().names
            assert 'ifDDD' == frame.fmtstr()

    finally:
        # even if the test fails, make sure the format string is reset to its
        # default, to not interfere with other tests
        dlis.Frame.dtype_format = original

@pytest.mark.parametrize('fmt', [
    ("x-{:d}.{:s}.{:d}"),
    ("x-{:s}.{:d}.{:d}.{:d}"),
])
def test_dtype_wrong_fmt(fmt, assert_error):
    fpath = "data/chap4-7/eflr/frames-and-channels/mainframe.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "MAINFRAME")
        frame.dtype_fmt = fmt
        with pytest.raises(Exception):
            _ = frame.dtype().names
        assert_error("rich label")


def test_channel_curves():
    fpath = 'data/chap4-7/iflr/all-reprcodes.dlis'
    with dlis.load(fpath) as (f, *_):
        channel = f.object('CHANNEL', 'CH26', 10, 0)
        curves = channel.curves()
        assert curves[0] == True

        channel = f.object('CHANNEL', 'CH22', 10, 0)
        curves22 = channel.curves()
        assert curves22[0] == 16777217

        frame_curves = load_curves(fpath)
        assert frame_curves['CH22'] == curves22

def test_channel_curves_duplicated_mnemonics():
    fpath = "data/chap4-7/eflr/frames-and-channels/mainframe.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "MAINFRAME")
        channel = f.object("CHANNEL", "TIME", 0, 0)
        curve = channel.curves()

        np.testing.assert_array_equal(curve,
                                      frame.curves()[channel.fingerprint])

def test_channel_without_frame(assert_info, tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('curves').join('no-frame.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
    ]
    merge_files_manyLR(fpath, content)
    with dlis.load(fpath) as (f, *_):
        channel = f.object("CHANNEL", "CHANN1")
        assert channel.curves() == None
        assert_info('no recorded curve-data')

        assert channel.frame == None
        assert_info('does not belong')

def test_channels_with_same_id(assert_info):
    # Test that the following channels and frames are linked correctly
    #
    # T.FRAME-I.FRAME_SAME1-O.0-C.0' -> T.CHANNEL-I.SAME-O.0-C.1'
    # T.FRAME-I.FRAME_SAME2-O.0-C.0' -> T.CHANNEL-I.SAME-O.0-C.2'
    fpath = "data/chap4-7/eflr/frames-and-channels/2-channels-same-content-diff-copynr.dlis"
    with dlis.load(fpath) as (f, *_):
        ch1 = f.object('CHANNEL', 'SAME', 0, 1)
        ch2 = f.object('CHANNEL', 'SAME', 0, 2)
        fr1 = f.object('FRAME', 'FRAME_SAME1')
        fr2 = f.object('FRAME', 'FRAME_SAME2')

        assert ch1.frame == fr1
        assert ch2.frame == fr2

def test_channel_in_multiple_frames(assert_info):
    fpath = "data/chap4-7/eflr/frames-and-channels/1-channel-2-frames.dlis"
    with dlis.load(fpath) as (f, *_):
        ch = f.object("CHANNEL", "DUPL")
        _  = ch.frame
        assert_info("Channel(DUPL) belongs to multiple")

def test_channel_duplicated_in_frame(assert_info):
    fpath = "data/chap4-7/eflr/frames-and-channels/duplicated.dlis"
    with dlis.load(fpath) as (f, *_):
        fr = f.object("FRAME", "DUPLICATED")
        ch = f.object("CHANNEL", "DUPL")

        assert ch.frame == fr

def test_channel_fmt():
    fpath = "data/chap4-7/eflr/frames-and-channels/various.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "VARIOUS")
        channel = f.object("CHANNEL", "chn3")
        pre_fmt, ch_fmt, post_fmt = frame.fmtstrchannel(channel)
        assert pre_fmt == "CCCCCbbbb"
        assert ch_fmt == "qqqqqqqq"
        assert post_fmt == "Ldddddd"

def test_channel_no_dimension(assert_log, tmpdir_factory, merge_files_manyLR):
    fpath = "data/chap4-7/eflr/frames-and-channels/no-dimension.dlis"
    with dlis.load(fpath) as (f, *_):
        ch = f.object("CHANNEL", "NODIM")
        with pytest.raises(ValueError) as exc:
            ch.fmtstr()
        assert "channel.dimension is invalid" in str(exc.value)

def test_frame_index():
    fpath = "data/chap4-7/eflr/frames-and-channels/mainframe.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "MAINFRAME")
        assert frame.index == frame.channels[0].name

def test_frame_index_absent(assert_info):
    fpath = "data/chap4-7/eflr/frames-and-channels/nonindexed.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "NONINDEXED")
        assert frame.index == 'FRAMENO'

def test_frame_index_nochannels(assert_info, tmpdir_factory,
                                merge_files_manyLR):
    fpath = "data/chap4-7/eflr/frames-and-channels/indexed-no-channels.dlis"
    with dlis.load(fpath) as (f, *_):
        frame = f.object("FRAME", "INDEXED_NO_CHANNELS")
        assert frame.index is None
        assert_info('Frame has no channels')
