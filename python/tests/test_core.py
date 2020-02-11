import pytest
import numpy as np
from datetime import datetime

import dlisio

# The example record from the specification
stdrecord = bytearray([
    # The eflr function assumes unsegmented record
    # # segment header #1
    # 0x00, 0x68, # length = 104
    # 0xA6,       # attributes
    # 0x03,       # type = CHANNL

    # channel set
    0xF8,       # SET:TN
    0x07, 0x43, 0x48, 0x41, 0x4E, 0x4E, 0x45, 0x4C, # "CHANNEL"
    0x01, 0x30, # "0"

    # template
    0x34,       # ATTRIB:LR
    # "LONG-NAME"
    0x09, 0x4C, 0x4F, 0x4E, 0x47, 0x2D, 0x4E, 0x41, 0x4D, 0x45,
    0x17,       # OBNAME

    0x35,       # ATTRIB:LRV
    # "ELEMENT-LIMIT"
    0x0D, 0x45, 0x4C, 0x45, 0x4D, 0x45, 0x4E, 0x54, 0x2D, 0x4C,
    0x49, 0x4D, 0x49, 0x54,
    0x12,       # UVARI
    0x01,       # 1

    0x35,       # ATTRIB: LRV
    # "REPRESENTATION-CODE
    0x13, 0x52, 0x45, 0x50, 0x52, 0x45, 0x53, 0x45, 0x4E, 0x54,
    0x41, 0x54, 0x49, 0x4F, 0x4E, 0x2D, 0x43, 0x4F, 0x44, 0x45,
    0x0F,       # USHORT
    0x02,       # FSINGL

    0x30,       # ATTRIB: L
    0x05, 0x55, 0x4E, 0x49, 0x54, 0x53, # "UNITS"

    0x35,       # ATTRIB: LRV
    # "DIMENSION"
    0x09, 0x44, 0x49, 0x4D, 0x45, 0x4E, 0x53, 0x49, 0x4F, 0x4E,
    0x12,       # UVARI
    0x01,       # 1

    # object #1
    0x70,       # OBJECT:N
    0x00, 0x00, 0x04, 0x54, 0x49, 0x4D, 0x45, # (0, 0, "TIME")
    0x21, 0x00, 0x00, 0x01, 0x31,             # "1"

    # # segment trailer #1
    # 0x00, 0x00, # CHECKSUM, not checked yet
    # 0x00, 0x68, # length = 104

    # # segment header #2
    # 0x00, 0x26, # length = 38
    # 0xE6, #in spec value is E6 in binary, but E7 in hex; binary is correct
    # 0x03,

    # ATTRIB: x2
    0x20,
    0x20,

    0x21,       # ATTRIB: V
    0x01, 0x73, # 1

    # object #2
    0x70,
    # (1, 0, "PRESSURE")
    0x01, 0x00, 0x08, 0x50, 0x52, 0x45, 0x53, 0x53, 0x55, 0x52, 0x45,

    0x21,   # 0,0, "2"
    0x00, 0x00, 0x01, 0x32,

    0x20,   # ATTRIB:

    0x21, 0x07,

    0x21,
    0x03, 0x70, 0x73, 0x69, # "psi"

    # # segment trailer #2
    # 0x00, 0x00, # CHECKSUM, not cheched yet
    # 0x00, 0x26, # length = 38

    # # segment header #3
    # 0x00, 0x26, # length = 38
    # 0xC7,
    # 0x03,

    0x70,
    # "PAD-ARRAY"
    0x00, 0x01, 0x09, 0x50, 0x41, 0x44, 0x2D, 0x41, 0x52, 0x52, 0x41, 0x59,

    0x21,
    0x00, 0x00, 0x01, 0x33, # 0, 0, "3"

    0x29,
    0x02,
    0x08, 0x14, # [8, 20]

    0x21,
    0x0D,       # UNORM

    0x00,       # ABSENT

    0x29,
    0x02,
    0x08, 0x0A, # [8, 10]

    # # segment trailer #3
    # 0x01, # pad-count
    # 0x00, 0x00,
    # 0x00, 0x26, # length = 38
])

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

def test_record_attributes():
    stream = dlisio.open('data/3-syntactic-logical-records.dlis')
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
