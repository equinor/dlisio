import numpy as np
import pytest

import dlisio
from dlisio.plumbing import linkage
from dlisio import core

def test_frame_getitem(DWL206):
    frame = DWL206.object('FRAME', '2000T', 2, 0)
    curves = frame.curves()

    expected = [1, 16677259.0, 852606.0, 2233.0, 852606.0]

    assert list(curves[0]) == expected

    assert curves['TIME'][0] == 16677259.0
    assert curves[0]['TIME'] == 16677259.0

    assert curves['TDEP'][0] == 852606.0
    assert curves[0]['TDEP'] == 852606.0

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

def test_duplicated_mnemonics_gets_unique_labels():
    frame = makeframe()
    assert 'ifDDD' == frame.fmtstr()
    assert ('FRAMENO', 'TIME.0.0', 'TDEP', 'TIME.1.0') == frame.dtype.names

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
    _ = memoryview(np.zeros(1, dtype = frame.dtype))

def test_duplicated_channels(assert_log):
    frame = makeframe()
    channel = frame.attic['CHANNELS'][0]
    frame.attic['CHANNELS'] = [channel, channel]

    with pytest.raises(ValueError):
        frame.dtype.names
    assert_log("duplicated mnemonics")

    frame.link()
    assert_log("already belongs to")

def test_instance_dtype_fmt():
    frame = makeframe()
    frame.dtype_fmt = 'x-{:s} {:d}~{:d}'

    # fmtstr is unchanged
    assert 'ifDDD' == frame.fmtstr()
    expected_names = ('FRAMENO', 'x-TIME 0~0', 'TDEP', 'x-TIME 1~0')
    assert expected_names == frame.dtype.names

@pytest.mark.parametrize('fmt', [
    ("x-{:d}.{:s}.{:d}"),
    ("x-{:s}.{:d}.{:d}.{:d}"),
])
def test_instance_dtype_wrong_fmt(fmt, assert_log):
    frame = makeframe()

    frame.dtype_fmt = fmt
    with pytest.raises(Exception):
        frame.dtype.names
    assert_log("rich label")

def test_class_dtype_fmt():
    original = dlisio.plumbing.Frame.dtype_format

    try:
        # change dtype before the object itself is constructed, so it
        dlisio.plumbing.Frame.dtype_format = 'x-{:s} {:d}~{:d}'
        frame = makeframe()
        expected_names = ('FRAMENO', 'x-TIME 0~0', 'TDEP', 'x-TIME 1~0')
        assert expected_names == frame.dtype.names
        assert 'ifDDD' == frame.fmtstr()

    finally:
        # even if the test fails, make sure the format string is reset to its
        # default, to not interfere with other tests
        dlisio.plumbing.Frame.dtype_format = original

def test_channel_curves():
    ch1 = dlisio.plumbing.Channel()
    ch1.name       ='ch1'
    ch1.origin     = 0
    ch1.copynumber = 0
    ch1.attic = {
        'DIMENSION'           : [5],
        'REPRESENTATION-CODE' : [11],
    }

    ch2 = dlisio.plumbing.Channel()
    ch2.name       ='ch2'
    ch2.origin     = 0
    ch2.copynumber = 0
    ch2.attic = {
        'DIMENSION'           : [2, 2],
        'REPRESENTATION-CODE' : [3],
    }

    ch3 = dlisio.plumbing.Channel()
    ch3.name       ='ch3'
    ch3.origin     = 0
    ch3.copynumber = 0
    ch3.attic = {
        'DIMENSION'           : [4, 2],
        'REPRESENTATION-CODE' : [26],
    }

    ch4 = dlisio.plumbing.Channel()
    ch4.name       ='ch4'
    ch4.origin     = 0
    ch4.copynumber = 0
    ch4.attic = {
        'DIMENSION'           : [1],
        'REPRESENTATION-CODE' : [17],
    }

    ch5 = dlisio.plumbing.Channel()
    ch5.name       ='ch5'
    ch5.origin     = 0
    ch5.copynumber = 0
    ch5.attic = {
        'DIMENSION'           : [2, 3, 1],
        'REPRESENTATION-CODE' : [12],
    }

    frame = dlisio.plumbing.Frame()
    frame.name       ='fr'
    frame.origin     = 0
    frame.copynumber = 0
    frame.attic = {
        'CHANNELS' : [
            core.obname(ch1.origin, ch1.copynumber, ch1.name),
            core.obname(ch2.origin, ch2.copynumber, ch2.name),
            core.obname(ch3.origin, ch3.copynumber, ch3.name),
            core.obname(ch4.origin, ch4.copynumber, ch4.name),
            core.obname(ch5.origin, ch5.copynumber, ch5.name),
        ]
    }

    logicalfile = dlisio.dlis(None, [], [], [])
    logicalfile.indexedobjects['FRAME'] = {
        frame.fingerprint : frame
    }

    logicalfile.indexedobjects['CHANNEL'] = {
        ch1.fingerprint : ch1,
        ch2.fingerprint : ch2,
        ch3.fingerprint : ch3,
        ch4.fingerprint : ch4,
        ch5.fingerprint : ch5,
    }
    frame.logicalfile = logicalfile
    ch1.logicalfile   = logicalfile
    ch2.logicalfile   = logicalfile
    ch3.logicalfile   = logicalfile
    ch4.logicalfile   = logicalfile
    ch5.logicalfile   = logicalfile

    pre_fmt, ch_fmt, post_fmt = frame.fmtstrchannel(ch3)
    assert pre_fmt  == "CCCCCbbbb"
    assert ch_fmt   == "qqqqqqqq"
    assert post_fmt == "Ldddddd"

def test_channel_no_dimension(assert_log):
    ch = dlisio.plumbing.Channel()
    ch.name = 'CH'
    ch.origin = 0
    ch.copynumber = 0
    ch.attic = { 'REPRESENTATION-CODE' : [17] }

    with pytest.raises(ValueError) as exc:
        ch.fmtstr()
    assert "channel.dimension is unvalid" in str(exc.value)

    ch.attic['DIMENSION'] = [1]
    assert ch.fmtstr() == "L"

def test_frame_index():
    frame = makeframe()
    frame.attic['INDEX-TYPE'] = ['DECREASING']

    assert frame.index == frame.channels[0]

def test_frame_noindex(assert_info):
    frame = makeframe()

    assert frame.index is None
    assert_info('There is no index channel')

def test_frame_nochannels_no_index(assert_info):
    frame = dlisio.plumbing.Frame()
    frame.attic['INDEX-TYPE'] = ['DECREASING']

    assert frame.index == None
    assert_info('There is no index channel')
