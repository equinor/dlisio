import numpy as np

import dlisio

from . import DWL206

def test_frame_getitem(DWL206):
    key = dlisio.core.fingerprint('FRAME', '2000T', 2, 0)
    curves = DWL206.curves(key)

    expected = [16677259.0, 852606.0, 2233.0, 852606.0]

    assert list(curves[0]) == expected

    assert curves['TIME'][0] == 16677259.0
    assert curves[0]['TIME'] == 16677259.0

    assert curves['TDEP'][0] == 852606.0
    assert curves[0]['TDEP'] == 852606.0

def makeframe():
    time0 = dlisio.plumbing.Channel()
    time0.name = 'TIME'
    time0.origin = 0
    time0.copynumber = 0
    time0.dimension = [1]
    time0.reprc = 2 # f4

    tdep = dlisio.plumbing.Channel()
    tdep.name = 'TDEP'
    tdep.origin = 0
    tdep.copynumber = 0
    tdep.dimension = [2]
    tdep.reprc = 13 # i2

    time1 = dlisio.plumbing.Channel()
    time1.name = 'TIME'
    time1.origin = 1
    time1.copynumber = 0
    time1.dimension = [1]
    time1.reprc = 13 # i2

    frame = dlisio.plumbing.Frame()
    frame.channels = [time0, tdep, time1]

    return frame

def test_duplicated_mnemonics_gets_unique_labels():
    frame = makeframe()
    assert 'fDDD' == frame.fmtstr()
    assert ('TIME.0.0', 'TDEP', 'TIME.1.0') == frame.dtype.names

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
