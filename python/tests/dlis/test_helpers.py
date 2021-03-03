"""
Testing common helper methods and functionality passed from C level
"""

import pytest

import dlisio
from dlisio.dlis.utils import *

def test_fingerprint():
    reference = "T.FRAME-I.800T-O.2-C.46"
    key = dlisio.core.fingerprint("FRAME", "800T", 2, 46)
    assert key == reference

    reference = "T.FRAME-I.-O.2-C.46"
    key = dlisio.core.fingerprint("FRAME", "", 2, 46)
    assert key == reference

def test_fingerprint_invalid_argument():
    with pytest.raises(ValueError):
        _ = dlisio.core.fingerprint("", "800T", 2, 46)
    with pytest.raises(ValueError):
        _ = dlisio.core.fingerprint("FRAME", "800T", -1, 46)
    with pytest.raises(ValueError):
        _ = dlisio.core.fingerprint("FRAME", "800T", 2, -1)

def test_issequence():
    assert not issequence('seq')
    assert not issequence("seq")
    assert not issequence("""seq""")
    assert not issequence(bytes(1))

    assert issequence([1])
    assert issequence(np.array([1]))

def test_remove_empties():
    d = OrderedDict()
    d['a'] = 0
    d['b'] = 1
    d['c'] = None
    d['d'] = np.empty(0)
    d['e'] = []
    d['f'] = 'str'
    d['g'] = ''
    d['h'] = ""

    ref = OrderedDict()
    ref['a'] = 0
    ref['b'] = 1
    ref['f'] = 'str'

    clean = remove_empties(d)
    assert clean == ref

def test_record_attributes():
    stream = core.open('data/chap2/3lr-in-vr-one-encrypted.dlis', 80)
    stream = core.open_rp66(stream)
    explicits = [0, 32, 64]
    recs = core.extract(stream, explicits, dlisio.common.ErrorHandler())

    buffer = bytearray(1)

    assert len(recs) == 3

    assert recs[0].type == 1
    assert not recs[0].explicit
    assert not recs[0].encrypted
    assert recs[0].consistent
    checked_byte = np.array(recs[0])[1]
    assert checked_byte == 4
    stream.get(buffer, explicits[0] + 5, 1)
    assert checked_byte == buffer[0]

    assert recs[1].type == 2
    assert recs[1].explicit
    assert not recs[1].encrypted
    stream.get(buffer, explicits[1] + 5, 1)
    assert np.array(recs[1])[1] == buffer[0]

    # last record ignored as encrypted
    assert recs[2].type == 3
    assert not recs[2].explicit
    assert recs[2].encrypted
    assert np.array(recs[2])[1] == 8

    stream.close()

