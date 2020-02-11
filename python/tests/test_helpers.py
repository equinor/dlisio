"""
Testing common helper methods and functionality passed from C level
"""

import pytest

import dlisio
from dlisio.plumbing import *

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
    stream = dlisio.open('data/chap2/3lr-in-vr-one-encrypted.dlis')
    tells = [80, 116, 148]
    residuals = [0, 64, 32]
    # for the test pretend all 3 records are explicit
    explicits = [0, 1, 2]
    stream.reindex(tells, residuals)
    recs = stream.extract(explicits)
    buffer = bytearray(1)

    assert len(recs) == 3

    assert recs[0].type == 1
    assert not recs[0].explicit
    assert not recs[0].encrypted
    # due to error in VE version
    assert not recs[0].consistent
    checked_byte = np.array(recs[0])[1]
    assert checked_byte == 4
    stream.get(buffer, tells[0] + 9, 1)
    assert checked_byte == buffer[0]

    assert recs[1].type == 2
    assert recs[1].explicit
    assert not recs[1].encrypted
    assert recs[1].consistent
    stream.get(buffer, tells[1] + 5, 1)
    assert np.array(recs[1])[1] == buffer[0]

    # last record ignored as encrypted
    rec3 = stream[2]
    assert rec3.type == 3
    assert not rec3.explicit
    assert rec3.encrypted
    assert rec3.consistent
    assert np.array(rec3)[1] == 8

    stream.close()

