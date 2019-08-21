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

def test_objects(DWL206):
    objects = DWL206.objects
    assert len(list(objects)) == 864

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

def test_fileheader(DWL206):
    fh = DWL206.object('FILE-HEADER', '5', 2, 0)
    assert fh.name == "5"
    assert fh.origin == 2
    assert fh.copynumber == 0
    assert fh.id == "MSCT_197LTP"
    assert fh.sequencenr == "197"

def test_origin(DWL206):
    origin = DWL206.object('ORIGIN', 'DLIS_DEFINING_ORIGIN', 2, 0)

    assert origin.name              == "DLIS_DEFINING_ORIGIN"
    assert origin.origin            == 2
    assert origin.copynumber        == 0
    assert origin.file_id           == "MSCT_197LTP"
    assert origin.file_set_name     == "FAROE_PETROLEUM/206_05A-3"
    assert origin.file_set_nr       == 41
    assert origin.file_nr           == 167
    assert origin.file_type         == "STATION LOG"
    assert origin.product           == "OP"
    assert origin.version           == "19C0-187"
    assert len(origin.programs)     == 4
    assert origin.creation_time     == datetime(2011, 8, 20, 22, 48, 50)
    assert origin.order_nr          == "BSAX-00003"
    assert origin.descent_nr        == ["-1"]
    assert origin.run_nr            == ["1"]
    assert origin.well_id           == ""
    assert origin.well_name         == "206/05a-3"
    assert origin.field_name        == "Fulla"
    assert origin.producer_code     == 440
    assert origin.producer_name     == "Schlumberger"
    assert origin.company           == "Faroe Petroleum"
    assert origin.namespace_name    == "SLB"
    assert origin.namespace_version == None

def test_channel(DWL206):
    channel = DWL206.object('CHANNEL', 'TDEP', 2, 0)
    assert channel.name            == "TDEP"
    assert channel.origin          == 2
    assert channel.copynumber      == 0
    assert channel.long_name       == "6-Inch Frame Depth"
    assert channel.type            == "CHANNEL"
    assert channel.reprc           == 2
    assert channel.properties      == ["440-BASIC"]
    assert channel.dimension       == [1]
    assert channel.axis            == []
    assert channel.element_limit   == [1]
    assert channel.units           == "0.1 in"
    assert channel.source is None

def test_frame(DWL206):
    frame = DWL206.object('FRAME', '2000T', 2, 0)
    assert frame.name            == "2000T"
    assert frame.origin          == 2
    assert frame.copynumber      == 0
    assert frame.type            == "FRAME"
    assert frame.direction       == "INCREASING"
    assert frame.spacing         == 2000
    assert frame.index_type      == "TIME"
    assert frame.index_min       == 33354518
    assert frame.index_max       == 35194520
    assert len(frame.channels)   == 4
    assert frame.encrypted == False
    assert frame.description is None

def test_channel_order(DWL206):
    frame800 = DWL206.object('FRAME', '800T', 2, 0)
    frame2000 = DWL206.object('FRAME', '2000T', 2, 0)

    ref2000T = ["TIME", "TDEP", "TENS_SL", "DEPT_SL"]
    ref800T  = ["TIME", "TDEP", "ETIM", "LMVL", "UMVL", "CFLA", "OCD" , "RCMD",
                "RCPP", "CMRT", "RCNU", "DCFL", "DFS" , "DZER", "RHMD", "HMRT",
                "RHV" , "RLSW", "MNU" , "S1CY", "S2CY", "RSCU", "RSTS", "UCFL",
                "CARC", "CMDV", "CMPP", "CNU" , "HMDV", "HV"  , "LSWI", "SCUR",
                "SSTA", "RCMP", "RHPP", "RRPP", "CMPR", "HPPR", "RPPV", "SMSC",
                "CMCU", "HMCU", "CMLP"]

    for i, ch in enumerate(frame800.channels):
        assert ch.name == ref800T[i]

    for i, ch in enumerate(frame2000.channels):
        assert ch.name == ref2000T[i]

def test_tool(DWL206):
    tool = DWL206.object('TOOL', 'MSCT', 2, 0)
    assert tool.name            == "MSCT"
    assert tool.origin          == 2
    assert tool.copynumber      == 0
    assert tool.type            == "TOOL"
    assert tool.description     == "Mechanical Sidewall Coring Tool"
    assert tool.trademark_name  == "MSCT-AA"
    assert tool.generic_name    == "MSCT"
    assert tool.status          == True
    assert len(tool.parameters) == 22
    assert len(tool.channels)   == 74
    assert len(tool.parts)      == 9

    assert len(list(DWL206.tools)) == 2
    tools = [o for o in DWL206.tools if o.name == "MSCT"]
    assert len(tools) == 1

def test_equipment(DWL206):
    e = DWL206.object('EQUIPMENT', 'MSCT/MCFU_1/EQUIPMENT', 2, 0)

    assert e.name            == "MSCT/MCFU_1/EQUIPMENT"
    assert e.origin          == 2
    assert e.copynumber      == 0
    assert e.trademark_name  == "MCFU_1-AA"
    assert e.status          == True
    assert e.serial_number   == "119."
    assert e.length          == 125.0
    assert e.diameter_min    == 5.25
    assert e.volume          == 1.5700000524520874
    assert e.weight          == 144.0
    assert e.pressure        == 20000.0
    assert e.temperature     == 350
    assert e.generic_type    is None
    assert e.location        is None
    assert e.height          is None
    assert e.diameter_max    is None
    assert e.hole_size       is None
    assert e.vertical_depth  is None
    assert e.radial_drift    is None
    assert e.angular_drift   is None

    assert len(list(DWL206.equipments)) == 14

def test_parameter(DWL206):
    param = DWL206.object('PARAMETER', 'FLSHSTRM', 2, 0)
    assert param.name       == "FLSHSTRM"
    assert param.origin     == 2
    assert param.copynumber == 0
    assert param.type       == "PARAMETER"
    assert param.long_name  == "Flush depth-delayed streams to output at end"
    assert param.dimension  == []
    assert param.axis       == []
    assert param.zones      == []

    assert param.values[0] == 'DOWNLOG_ONLY'
    assert len(list(DWL206.parameters)) == 226


def test_measurement(DWL206):
    m = DWL206.object('CALIBRATION-MEASUREMENT',
                      'MSCT_SGTE/ZM_BEF/CALI_MEAS', 2, 0)

    assert m.phase           == 'BEFORE'
    assert m.source          == None
    assert m.mtype           == None
    assert m.dimension       == []
    assert m.axis            == []
    assert m.samplecount     == 142
    assert m.begin_time      == datetime(2011, 8, 20, 18, 13, 38)
    assert m.duration        == 30
    assert m.standard        == []

    assert np.array_equal(m.samples , np.array([2.640824317932129]))

    assert m.max_deviation   == 11.421565055847168
    assert m.std_deviation   == 3.4623820781707764
    assert m.reference       == 0.0

    assert np.array_equal(m.plus_tolerance , np.empty(0))
    assert np.array_equal(m.minus_tolerance, np.empty(0))

    assert len(list(DWL206.measurements)) == 6

def test_coefficient(DWL206):
    c = DWL206.object('CALIBRATION-COEFFICIENT',
                      'GAIN-MSCT/HPPR/CALIBRATION', 2, 0)
    assert c.label           == 'GAIN'
    assert c.coefficients    == [1.0]
    assert c.references      == []
    assert c.plus_tolerance  == []
    assert c.minus_tolerance == []

    assert len(list(DWL206.coefficients)) == 24

def test_calibrations(DWL206):
    calibration = DWL206.object('CALIBRATION', 'CNU', 2, 0)
    assert calibration.name              == "CNU"
    assert calibration.origin            == 2
    assert calibration.copynumber        == 0
    assert calibration.type              == "CALIBRATION"
    assert len(calibration.parameters)   == 0
    assert len(calibration.coefficients) == 2
    assert len(calibration.measurements) == 0
    assert calibration.method is None
    assert len(list(calibration.calibrated))   == 1
    assert len(list(calibration.uncalibrated)) == 1

def test_fmtstring(DWL206):
    reference1 = "ffffffffffffffffffffffffffffffffffffffflfff"
    reference2 = "ffff"

    frame800 = DWL206.object('FRAME', '800T', 2, 0)
    frame2000 = DWL206.object('FRAME', '2000T', 2, 0)

    fmtstring1 = frame800.fmtstr()
    fmtstring2 = frame2000.fmtstr()

    assert fmtstring1 == reference1
    assert fmtstring2 == reference2

def test_dtype(DWL206):
    frame2000 = DWL206.object('FRAME', '2000T', 2, 0)
    dtype1 = frame2000.dtype
    assert dtype1 == np.dtype([('TIME', np.float32),
                               ('TDEP', np.float32),
                               ('TENS_SL', np.float32),
                               ('DEPT_SL', np.float32)])

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
