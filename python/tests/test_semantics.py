import pytest
from datetime import datetime

import dlisio

from . import merge_files

@pytest.fixture(scope="module")
def f(tmpdir_factory, merge_files):
    path = str(tmpdir_factory.mktemp('semantic').join('semantic.dlis'))
    content = [
        'data/semantic/envelope.dlis.part',
        'data/semantic/file-header.dlis.part',
        'data/semantic/origin.dlis.part',
        'data/semantic/axis.dlis.part',
        'data/semantic/long-name-record.dlis.part',
        'data/semantic/channel.dlis.part',
        'data/semantic/zone.dlis.part',
        'data/semantic/parameter.dlis.part',
        'data/semantic/equipment.dlis.part',
        'data/semantic/tool.dlis.part',
        'data/semantic/measurement.dlis.part',
        'data/semantic/coefficient.dlis.part',
        'data/semantic/coefficient-wrong.dlis.part',
        'data/semantic/calibration.dlis.part',
        'data/semantic/frame.dlis.part',
        'data/semantic/unknown.dlis.part',
    ]
    merge_files(path, content)
    with dlisio.load(path) as f:
        yield f

def test_file_header(f):
    key = dlisio.core.fingerprint('FILE-HEADER', 'N', 10, 0)
    fh = f.objects[key]
    assert fh.type       == "FILE-HEADER"
    assert fh.name       == "N"
    assert fh.origin     == 10
    assert fh.copynumber == 0
    #next two check for value space-stripping
    assert fh.sequencenr == "8"
    assert fh.id         == "some logical file"

def test_origin(f):
    key = dlisio.core.fingerprint('ORIGIN', 'DEFINING_ORIGIN', 10, 0)
    def_origin = f.objects[key]
    assert def_origin.type              == "ORIGIN"
    assert def_origin.origin            == 10
    assert def_origin.file_id           == "some logical file"
    assert def_origin.file_set_name     == "SET-NAME"
    assert def_origin.file_set_nr       == 1042
    assert def_origin.file_nr           == 7
    assert def_origin.file_type         == "CRUCIAL"
    assert def_origin.product           == "fantasy"
    assert def_origin.version           == "-1.0"
    # checks for space-stripping for lists
    assert def_origin.programs          == ["PROG1", "PROG2"]
    assert def_origin.creation_time     == datetime(2019, 5, 2, 13, 51)
    assert def_origin.order_nr          == "SR-BB"
    assert def_origin.descent_nr        == ["DESNUM"]
    assert def_origin.run_nr            == [17]
    assert def_origin.well_id           == "CODED-WELL"
    assert def_origin.well_name         == "SECRET-WELL"
    assert def_origin.field_name        == "WILDCAT"
    assert def_origin.producer_code     == 307
    assert def_origin.producer_name     == "Test Production"
    assert def_origin.company           == "The Company"
    assert def_origin.namespace_name    == "DIC1"
    assert def_origin.namespace_version == 6

    key = dlisio.core.fingerprint('ORIGIN', 'RANDOM', 127, 0)
    random_origin = f.objects[key]
    assert random_origin.origin      == 127
    assert random_origin.file_id     == "some other logical file"
    assert random_origin.file_set_nr == 1042
    assert random_origin.file_nr     == 6

def test_channel(f):
    key = dlisio.core.fingerprint('TOOL', 'TOOL1', 10, 0)
    tool = f.objects[key]

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN1', 10, 0)
    channel = f.objects[key]

    assert channel.long_name         == (10, 0, "CHANN1-LONG-NAME")
    assert channel.properties        == ["AVERAGED", "DERIVED", "PATCHED"]
    assert channel.reprc             == 16
    assert channel.units             == "custom units"
    assert channel.dimension         == [2, 3, 2]
    assert channel.axis              == [(10, 0, "AXIS1"),
                                         (10, 0, "AXIS2"),
                                         (10, 0, "AXIS3")]
    assert channel.element_limit     == [10, 15, 10]
    assert channel.source            == tool

def test_frame(f):
    key = dlisio.core.fingerprint('CHANNEL', 'CHANN1', 10, 0)
    channel1 = f.objects[key]
    key = dlisio.core.fingerprint('CHANNEL', 'CHANN2', 10, 0)
    channel2 = f.objects[key]

    key = dlisio.core.fingerprint('FRAME', 'FRAME1', 10, 0)
    frame1 = f.objects[key]

    assert frame1.description == "Main frame"
    assert frame1.channels    == [channel1, channel2]
    assert frame1.index_type  == "BOREHOLE-DEPTH"
    assert frame1.direction   == "DECREASING"
    assert frame1.spacing     == 119
    assert frame1.encrypted   == False #attribute absent
    assert frame1.index_min   == 1
    assert frame1.index_max   == 100

    key = dlisio.core.fingerprint('FRAME', 'FRAME2', 10, 0)
    frame2 = f.objects[key]

    #for second frame many attributes are absent
    assert frame2.description == "Secondary frame"
    assert frame2.channels    == []
    assert frame2.index_type  == None
    assert frame2.direction   == None
    assert frame2.spacing     == None
    #assert frame2.encrypted   == True #attribute present
    assert frame2.index_min   == None
    assert frame2.index_max   == None

def test_parameter(f):
    key = dlisio.core.fingerprint('PARAMETER', 'PARAM1', 10, 0)
    param = f.objects[key]
    assert param.long_name         == (10, 0, "PARAM1-LONG")
    assert param.axis              == [(10, 0, "AXIS1")]
    assert param.zones             == [(10, 0, "ZONE-A")]
    assert param.dimension         == [2]
    assert param.values            == [101, 120]

    key = dlisio.core.fingerprint('PARAMETER', 'PARAM2', 10, 0)
    param = f.objects[key]
    assert param.long_name         == (10, 0, "PARAM2-LONG")
    assert param.values            == [131, 69]

    key = dlisio.core.fingerprint('PARAMETER', 'PARAM3', 10, 0)
    param = f.objects[key]
    assert param.long_name         == (10, 0, "PARAM3-LONG")
    assert param.values            == [152, 35]

def test_equipment(f):
    key = dlisio.core.fingerprint('EQUIPMENT', 'EQUIP1', 10, 0)
    e = f.objects[key]
    assert e.trademark_name == "some equipment"
    assert e.status         == True
    assert e.generic_type   == "Pad"
    assert e.serial_number  == "MNP123"
    assert e.location       == "RIG"
    assert e.height         == 120
    assert e.length         == 244
    assert e.diameter_min   == 1
    assert e.diameter_max   == 147
    assert e.volume         == 132
    assert e.weight         == 121
    assert e.hole_size      == 137
    assert e.pressure       == 148
    assert e.temperature    == 17
    assert e.vertical_depth == 103
    assert e.radial_drift   == 130
    assert e.angular_drift  == 41

def test_tool(f):
    key = dlisio.core.fingerprint('EQUIPMENT', 'EQUIP1', 10, 0)
    e = f.objects[key]

    key = dlisio.core.fingerprint('PARAMETER', 'PARAM1', 10, 0)
    param1 = f.objects[key]
    key = dlisio.core.fingerprint('PARAMETER', 'PARAM2', 10, 0)
    param2 = f.objects[key]

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN1', 10, 0)
    channel1 = f.objects[key]
    key = dlisio.core.fingerprint('CHANNEL', 'CHANN2', 10, 0)
    channel2 = f.objects[key]

    key = dlisio.core.fingerprint('TOOL', 'TOOL1', 10, 0)
    tool = f.objects[key]

    assert tool.description             == "description of tool 1"
    assert tool.trademark_name          == "TOOL123"
    assert tool.generic_name            == "Important tool"
    assert tool.parts                   == [e]
    assert tool.status                  == True
    assert tool.channels                == [channel1, channel2]
    assert tool.parameters              == [param1, param2]

def test_measurement(f):
    key = dlisio.core.fingerprint('TOOL', 'TOOL1', 10, 0)
    tool = f.objects[key]

    key = dlisio.core.fingerprint('CALIBRATION-MEASUREMENT', 'MEAS1', 10, 0)
    m = f.objects[key]

    assert m.axis == [(10, 0, "AXIS1"), (10, 0, "AXIS2")]
    assert m.phase           == "MASTER"
    assert m.source          == tool
    assert m.mtype           == "Zero"
    assert m.dimension       == [2, 3]
    assert m.samples         == [240, 137, 228, 120, 240, 136]
    assert m.samplecount     == 4
    assert m.max_deviation   == 2.5
    assert m.std_deviation   == -14.25
    assert m.begin_time      == 13447
    assert m.duration        == 21
    assert m.reference       == [240, 135, 240, 135, 240, 135]
    assert m.standard        == [1]
    assert m.plus_tolerance  == [5, 10, 5, 10, 5, 10]
    assert m.minus_tolerance == [1, 1, 1, 1, 1, 1]

def test_coefficient(f):
    key = dlisio.core.fingerprint('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)
    c = f.objects[key]

    assert c.label           == "GAIN"
    assert c.coefficients    == [18, 25]
    assert c.references      == [18, 32]
    assert c.plus_tolerance  == [1, 1]
    assert c.minus_tolerance == [2, 1]

def test_calibration(f):
    key = dlisio.core.fingerprint('PARAMETER', 'PARAM1', 10, 0)
    param1 = f.objects[key]
    key = dlisio.core.fingerprint('PARAMETER', 'PARAM2', 10, 0)
    param2 = f.objects[key]
    key = dlisio.core.fingerprint('PARAMETER', 'PARAM3', 10, 0)
    param3 = f.objects[key]

    key = dlisio.core.fingerprint('CALIBRATION-MEASUREMENT', 'MEAS1', 10, 0)
    meas1 = f.objects[key]
    key = dlisio.core.fingerprint('CALIBRATION-MEASUREMENT', 'MEAS2', 10, 0)
    meas2 = f.objects[key]

    key = dlisio.core.fingerprint('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)
    coeff1 = f.objects[key]
    key = dlisio.core.fingerprint('CALIBRATION-COEFFICIENT', 'COEFF2', 10, 0)
    coeff2 = f.objects[key]

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN1', 10, 0)
    channel1 = f.objects[key]
    key = dlisio.core.fingerprint('CHANNEL', 'CHANN2', 10, 0)
    channel2 = f.objects[key]
    key = dlisio.core.fingerprint('CHANNEL', 'CHANN3', 10, 0)
    channel3 = f.objects[key]
    key = dlisio.core.fingerprint('CHANNEL', 'CHANN4', 10, 0)
    channel4 = f.objects[key]

    key = dlisio.core.fingerprint('CALIBRATION', 'CALIBR1', 10, 0)
    c = f.objects[key]

    assert c.calibrated   == [channel1, channel2]
    assert c.uncalibrated == [channel3, channel4]
    assert c.coefficients == [coeff1, coeff2]
    assert c.measurements == [meas1, meas2]
    assert c.parameters   == [param1, param2, param3]
    assert c.method       == "USELESS"

def test_unknown(f):
    key = dlisio.core.fingerprint('UNKNOWN_SET', 'OBJ1', 10, 0)
    unknown = f.objects[key]

    assert unknown.stash["SOME_LIST"]   == ["LIST_V1", "LIST_V2"]
    assert unknown.stash["SOME_VALUE"]  == ["VAL1"]
    assert unknown.stash["SOME_STATUS"] == [1]

def test_unexpected_attributes(f):
    key = dlisio.core.fingerprint('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)
    c = f.objects[key]

    assert c.label                           == "SMTH"
    assert c.plus_tolerance                  == [] #count 0
    assert c.minus_tolerance                 == [] #not specified

    #'lnks' instead of 'references'
    assert c.stash["LNKS"]                   == [18, 32]
    #spaces are stripped for stash also
    assert c.stash["MY_PARAM"]               == ["wrong", "W"]
    assert c.stash["LINKS_TO_PARAMETERS"]    ==  [(10, 0, "PARAM2"),
                                                  (10, 0, "PARAMU")]
    assert c.stash["LINK_TO_UNKNOWN_OBJECT"] == [("UNKNOWN_SET",
                                                  (10, 0, "OBJ1"))]
