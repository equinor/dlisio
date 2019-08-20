import pytest
from datetime import datetime
import numpy as np

from dlisio.core import fingerprint
import dlisio

def test_file_header(f):
    key = fingerprint('FILE-HEADER', 'N', 10, 0)
    fh = f.objects[key]
    assert fh.type       == "FILE-HEADER"
    assert fh.name       == "N"
    assert fh.origin     == 10
    assert fh.copynumber == 0
    #next two check for value space-stripping
    assert fh.sequencenr == "8"
    assert fh.id         == "some logical file"

    _ = fh.describe(indent='   ', width=70, exclude='e')

def test_origin(f):
    key = fingerprint('ORIGIN', 'DEFINING_ORIGIN', 10, 0)
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

    key = fingerprint('ORIGIN', 'RANDOM', 127, 0)
    random_origin = f.objects[key]
    assert random_origin.origin      == 127
    assert random_origin.file_id     == "some other logical file"
    assert random_origin.file_set_nr == 1042
    assert random_origin.file_nr     == 6

    _ = random_origin.describe(indent='   ', width=70, exclude='e')

def test_axis(f):
    key = fingerprint('AXIS', 'AXIS2', 10, 0)
    axis = f.objects[key]

    assert axis.axis_id     == 'AX2'
    assert axis.coordinates == ['very near', 'not so far']
    assert axis.spacing     == 'a bit'

    _ = axis.describe(indent='   ', width=70, exclude='e')

def test_longname(f):
    key = fingerprint('LONG-NAME', 'CHANN1-LONG-NAME', 10, 0)
    ln  = f.objects[key]

    assert ln.modifier        == ['channel 1 long name']
    assert ln.quantity        == 'color'
    assert ln.quantity_mod    == ['nice']
    assert ln.altered_form    == 'deviation'
    assert ln.entity          == 'borehole'
    assert ln.entity_mod      == ['bad']
    assert ln.entity_nr       == '21'
    assert ln.entity_part     == 'top part?'
    assert ln.entity_part_nr  == '1'
    assert ln.generic_source  == 'random words'
    assert ln.source_part     == ['generator']
    assert ln.source_part_nr  == ['8412']
    assert ln.conditions      == ['at standard temperature']
    assert ln.standard_symbol == 'SYM'
    assert ln.private_symbol  == 'BOL'

    _ = ln.describe(indent='   ', width=70, exclude='e')

def test_channel(f):
    key = fingerprint('TOOL', 'TOOL1', 10, 0)
    tool = f.objects[key]

    key = fingerprint('LONG-NAME', 'CHANN1-LONG-NAME', 10, 0)
    longname = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN1', 10, 0)
    channel = f.objects[key]

    key = fingerprint('AXIS', 'AXIS1', 10, 0)
    axis1 = f.objects[key]

    key = fingerprint('AXIS', 'AXIS2', 10, 0)
    axis2 = f.objects[key]

    key = fingerprint('AXIS', 'AXIS3', 10, 0)
    axis3 = f.objects[key]

    assert channel.long_name              == longname
    assert channel.properties             == ["AVERAGED", "DERIVED", "PATCHED"]
    assert channel.reprc                  == 16
    assert channel.units                  == "custom unit°"
    assert channel.dimension              == [4, 3, 2]
    assert channel.attic["DIMENSION"]     == [2, 3, 4]
    assert channel.axis                   == [axis3, axis2, axis1]
    assert channel.attic["AXIS"]          == [(10, 0, 'AXIS1'),
                                              (10, 0, 'AXIS2'),
                                              (10, 0, 'AXIS3')]
    assert channel.element_limit          == [11, 15, 10]
    assert channel.attic["ELEMENT-LIMIT"] == [10, 15, 11]
    assert channel.source                 == tool

    _ = channel.describe(indent='   ', width=70, exclude='e')

def test_channel_fdata(f):
    key = fingerprint('CHANNEL', 'CHANN1', 10, 0)
    channel = f.objects[key]
    curves = channel.curves()

    assert list(curves[0][0][0]) == [1, 2]
    assert list(curves[1][1][1]) == [521, 522]
    assert list(curves[2][2][2]) == [1041, 1042]

    key = fingerprint('FRAME', 'FRAME1', 10, 0)
    frame = f.objects[key]
    ch1_curves = frame.curves()["CHANN1"]

    assert np.array_equal(curves, ch1_curves)

def test_frame(f):
    key = fingerprint('CHANNEL', 'CHANN1', 10, 0)
    channel1 = f.objects[key]
    key = fingerprint('CHANNEL', 'CHANN2', 10, 0)
    channel2 = f.objects[key]

    key = fingerprint('FRAME', 'FRAME1', 10, 0)
    frame1 = f.objects[key]

    assert frame1.description == "Main frame"
    assert frame1.channels    == [channel1, channel2]
    assert frame1.index_type  == "BOREHOLE-DEPTH"
    assert frame1.direction   == "DECREASING"
    assert frame1.spacing     == 119
    assert frame1.encrypted   == False #attribute absent
    assert frame1.index_min   == 1
    assert frame1.index_max   == 100

    key = fingerprint('FRAME', 'FRAME2', 10, 0)
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

def test_fdata_reprcode(f):
    key = fingerprint('FRAME', 'FRAME-REPRCODE', 10, 0)
    frame = f.objects[key]
    curves = frame.curves()

    assert list(curves[0][0])     == [153, -1]
    assert list(curves[0][1])     == [17.25, -13.75]
    assert list(curves[0][2][0])  == [-2, 3.5]
    assert list(curves[0][2][1])  == [56.125, -0.0625]
    assert list(curves[0][3][0])  == [7, -0.50390625, 0.5]
    assert list(curves[0][3][1])  == [3524454, 10, 20]
    assert list(curves[0][4])     == [-12, 65536.5]
    assert list(curves[0][5])     == [-26.5, 0.125]
    assert list(curves[0][6])     == [153, -153]
    assert list(curves[0][7])     == [5673345, 14]
    assert list(curves[0][8])     == [95637722454, 20, 5]
    assert curves[0][9]           == np.complex(67, -37)
    assert curves[0][10]          == np.complex(67, -37)
    assert list(curves[0][11])    == [89, -89]
    assert list(curves[0][12])    == [153, -153]
    assert list(curves[0][13])    == [153, -153]
    assert list(curves[0][14][0]) == [217, 1, 118]
    assert list(curves[0][14][1]) == [66, 251, 75]
    assert list(curves[0][15])    == [32921, 256]
    assert list(curves[0][16])    == [153, 4294967143]
    assert list(curves[0][17])    == [False, True]

def test_fdata_dimension(fpath):
    with dlisio.load(fpath) as (_, g):
        key = fingerprint('FRAME', 'FRAME-DIMENSION', 11, 0)
        frame = g.objects[key]
        curves = frame.curves()

        assert list(curves[0][0][0])    == [1, 2, 3]
        assert list(curves[0][0][1])    == [4, 5, 6]
        assert list(curves[0][1][0])    == [1, 2]
        assert list(curves[0][1][1])    == [3, 4]
        assert list(curves[0][1][2])    == [5, 6]
        assert list(curves[0][2][0][0]) == [1, 2]
        assert list(curves[0][2][1][1]) == [9, 10]
        assert list(curves[0][2][2][1]) == [15, 16]
        assert list(curves[0][2][3][2]) == [23, 24]
        assert list(curves[0][3][0])    == [1, 2]
        assert list(curves[0][4][0])    == [1]
        assert list(curves[0][4][1])    == [2]
        assert list(curves[0][5][0])    == [1]
        assert list(curves[0][6])       == [1, 2, 3, 4]

def test_zone(f):
    key = fingerprint('ZONE', 'ZONE-A', 10, 0)
    zone = f.objects[key]

    assert zone.description == 'Some along zone'
    assert zone.domain      == 'VERTICAL-DEPTH'
    assert zone.maximum     == 13398
    assert zone.minimum     == 8603

    _ = zone.describe(indent='   ', width=70, exclude='e')

def test_parameter(f):
    key = fingerprint('PARAMETER', 'PARAM3', 10, 0)
    p = f.objects[key]

    key = fingerprint('LONG-NAME', 'PARAM3-LONG', 10, 0)
    longname = f.objects[key]
    key = fingerprint('ZONE', 'ZONE-A', 10, 0)
    zoneA = f.objects[key]
    key = fingerprint('AXIS', 'AXIS2', 10, 0)
    axis2 = f.objects[key]
    key = fingerprint('AXIS', 'AXIS3', 10, 0)
    axis3 = f.objects[key]

    assert p.long_name           == longname
    assert p.dimension           == [2, 3]
    assert p.attic["DIMENSION"]  == [3, 2]
    assert p.axis                == [axis3, axis2]
    assert len(p.attic["AXIS"])  == 2
    assert p.zones               == [zoneA, None, None, None]
    assert len(p.attic["ZONES"]) == 4

    sample = np.reshape(np.array([1, 2, 3, 4, 5, 6]), (2,3))

    assert np.array_equal(p.values[0], sample)
    assert np.array_equal(p.values[1][1], np.array([10, 11, 12]))

    assert p.values[2][0][1] == 14
    assert p.values[3][1][2] == 24

    key = fingerprint('PARAMETER', 'PARAM1', 10, 0)
    p = f.objects[key]
    key = fingerprint('LONG-NAME', 'PARAM1-LONG', 10, 0)
    longname = f.objects[key]

    assert p.long_name == longname

    value = p.values[0]
    assert np.array_equal(value, np.array([101, 120]))

    _ = p.describe(indent='   ', width=70, exclude='e')

def test_equipment(f):
    key = fingerprint('EQUIPMENT', 'EQUIP1', 10, 0)
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

    _ = e.describe(indent='   ', width=70, exclude='e')

def test_tool(f):
    key = fingerprint('EQUIPMENT', 'EQUIP1', 10, 0)
    e = f.objects[key]

    key = fingerprint('PARAMETER', 'PARAM1', 10, 0)
    param1 = f.objects[key]
    key = fingerprint('PARAMETER', 'PARAM2', 10, 0)
    param2 = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN1', 10, 0)
    channel1 = f.objects[key]
    key = fingerprint('CHANNEL', 'CHANN2', 10, 0)
    channel2 = f.objects[key]

    key = fingerprint('TOOL', 'TOOL1', 10, 0)
    tool = f.objects[key]

    assert tool.description             == "description of tool 1"
    assert tool.trademark_name          == "TOOL123"
    assert tool.generic_name            == "Important tool"
    assert tool.parts                   == [e]
    assert tool.status                  == True
    assert tool.channels                == [channel1, channel2]
    assert tool.parameters              == [param1, None, param2]
    assert len(tool.refs["parameters"]) == 3

    _ = tool.describe(indent='   ', width=70, exclude='e')

def test_message(f):
    key = fingerprint('MESSAGE', 'MESSAGE1', 10, 0)
    mes = f.objects[key]

    assert mes.message_type   == 'SYSTEM'
    assert mes.time           == datetime(1990, 4, 20, 12, 58, 59, 1)
    assert mes.borehole_drift == 65282
    assert mes.vertical_depth == 120
    assert mes.radial_drift   == 65093
    assert mes.angular_drift  == 344
    assert mes.text           == ['System says hi!']

    _ = mes.describe(indent='   ', width=70, exclude='e')

def test_measurement(f):
    key = fingerprint('TOOL', 'TOOL1', 10, 0)
    tool = f.objects[key]

    key = fingerprint('CALIBRATION-MEASUREMENT', 'MEAS1', 10, 0)
    m = f.objects[key]

    key = fingerprint('AXIS', 'AXIS1', 10, 0)
    axis1 = f.objects[key]

    key = fingerprint('AXIS', 'AXIS2', 10, 0)
    axis2 = f.objects[key]

    assert m.phase              == "MASTER"
    assert m.source             == tool
    assert m.mtype              == "Zero"
    assert m.dimension          == [3, 2]
    assert m.attic["DIMENSION"] == [2, 3]
    assert m.axis               == [axis2, axis1]
    assert m.samplecount        == 4
    assert m.begin_time         == 13447
    assert m.duration           == 21
    assert m.standard           == [1]

    samples = np.array([[240, 137], [228, 120], [240, 136]])
    maxdev  = np.array([[2.5, 2.5], [2.5, 2.75], [2.5, 2.5]])
    stddev  = np.array([[-14.25, -14.25], [-14.25, -14.25], [-14, -14.25]])
    ref     = np.array([[240, 135], [240, 135], [240, 135]])
    plus    = np.array([[5, 10], [5, 10], [5, 10]])
    minus   = np.array([[1, 1], [1, 1], [1, 1]])

    assert np.array_equal(m.samples[0]      , samples)
    assert np.array_equal(m.max_deviation   , maxdev)
    assert np.array_equal(m.std_deviation   , stddev)
    assert np.array_equal(m.reference       , ref)
    assert np.array_equal(m.plus_tolerance  , plus)
    assert np.array_equal(m.minus_tolerance , minus)

    _ = m.describe(indent='   ', width=70, exclude='e')

def test_coefficient(f):
    key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)
    c = f.objects[key]

    assert c.label           == "GAIN"
    assert c.coefficients    == [18, 25]
    assert c.references      == [18, 32]
    assert c.plus_tolerance  == [1, 1]
    assert c.minus_tolerance == [2, 1]

    _ = c.describe(indent='   ', width=70, exclude='e')

def test_calibration(f):
    key = fingerprint('PARAMETER', 'PARAM1', 10, 0)
    param1 = f.objects[key]
    key = fingerprint('PARAMETER', 'PARAM2', 10, 0)
    param2 = f.objects[key]
    key = fingerprint('PARAMETER', 'PARAM3', 10, 0)
    param3 = f.objects[key]

    key = fingerprint('CALIBRATION-MEASUREMENT', 'MEAS1', 10, 0)
    meas1 = f.objects[key]
    key = fingerprint('CALIBRATION-MEASUREMENT', 'MEAS2', 10, 0)
    meas2 = f.objects[key]

    key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)
    coeff1 = f.objects[key]
    key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF2', 10, 0)
    coeff2 = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN1', 10, 0)
    channel1 = f.objects[key]
    key = fingerprint('CHANNEL', 'CHANN2', 10, 0)
    channel2 = f.objects[key]
    key = fingerprint('CHANNEL', 'CHANN3', 10, 0)
    channel3 = f.objects[key]
    key = fingerprint('CHANNEL', 'CHANN4', 10, 0)
    channel4 = f.objects[key]

    key = fingerprint('CALIBRATION', 'CALIBR1', 10, 0)
    c = f.objects[key]

    assert c.calibrated   == [channel1, channel2]
    assert c.uncalibrated == [channel3, channel4]
    assert c.coefficients == [coeff1, coeff2]
    assert c.measurements == [meas1, meas2]
    assert c.parameters   == [param1, param2, param3]
    assert c.method       == "USELESS"

    _ = c.describe(indent='   ', width=70, exclude='e')

def test_computation(f):
    key = fingerprint('COMPUTATION', 'COMPUT2', 10, 0)
    com = f.objects[key]

    key = fingerprint('AXIS', 'AXIS2', 10, 0)
    axis2 = f.objects[key]

    key = fingerprint('AXIS', 'AXIS3', 10, 0)
    axis3 = f.objects[key]

    key = fingerprint('ZONE', 'ZONE-A', 10, 0)
    zone = f.objects[key]

    key = fingerprint('PROCESS', 'PROC1', 10, 0)
    process = f.objects[key]

    assert com.long_name          == 'computation object 2'
    assert com.properties         == ['MUDCAKE-CORRECTED', 'DEPTH-MATCHED']
    assert com.dimension          == [4, 2]
    assert com.attic["DIMENSION"] == [2, 4]
    assert com.axis               == [axis3, axis2]
    assert com.zones              == [zone]
    assert com.source             == process

    values  = np.array([[140, 99], [144, 172], [202, 52], [109, 120]])
    assert np.array_equal(com.values[0], values)

    _ = com.describe(indent='   ', width=70, exclude='e')

def test_splice(f):
    key = fingerprint('SPLICE', 'SPLICE1', 10, 0)
    splice = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN4', 10, 0)
    in1 = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN1', 10, 0)
    in2 = f.objects[key]

    key = fingerprint('ZONE', 'ZONE-A', 10, 0)
    zone1 = f.objects[key]

    # Output channel does not exist, but should be accessible through refs
    assert splice.output_channel == None
    assert splice.refs['output_channel'].id         == 'CHANN-NEW'
    assert splice.refs['output_channel'].origin     == 10
    assert splice.refs['output_channel'].copynumber ==  0

    assert splice.input_channels == [in1, in2]

    # Second zone does not exist, but should be accessible through refs
    assert splice.zones                       == [zone1 , None]
    assert splice.refs['zones'][1].id         == 'ZONE-B'
    assert splice.refs['zones'][1].origin     == 10
    assert splice.refs['zones'][1].copynumber == 0

    _ = splice.describe(indent='   ', width=70, exclude='e')

def test_wellref(f):
    key = fingerprint('WELL-REFERENCE', 'THE-WELL', 10, 0)
    wellref = f.objects[key]

    assert wellref.permanent_datum           == 'Ground Level'
    assert wellref.vertical_zero             == 'Kelly Bushing'
    assert wellref.permanent_datum_elevation == -89
    assert wellref.above_permanent_datum     == -5
    assert wellref.magnetic_declination      == -22

    assert wellref.coordinates['longitude']  == -11.25
    assert wellref.coordinates['latitude']   == 60.75
    assert wellref.coordinates['elevation']  == 0.25

    _ = wellref.describe(indent='   ', width=70, exclude='e')

def test_group(f):
    key = fingerprint('GROUP', 'GROUP1', 10, 0)
    g1 = f.objects[key]

    key = fingerprint('PARAMETER', 'PARAM3', 10, 0)
    param = f.objects[key]

    key = fingerprint('GROUP', 'GROUP2', 10, 0)
    g2 = f.objects[key]

    key = fingerprint('GROUP', 'GROUP3', 10, 0)
    g3 = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN3', 10, 0)
    ch = f.objects[key]

    key = fingerprint('TOOL', 'TOOL1', 10, 0)
    tool = f.objects[key]

    key = fingerprint('AXIS', 'AXIS1', 10, 0)
    ax1 = f.objects[key]

    key = fingerprint('AXIS', 'AXIS2', 10, 0)
    ax2 = f.objects[key]

    key = fingerprint('AXIS', 'AXIS3', 10, 0)
    ax3 = f.objects[key]

    assert g1.objects     == [ax1, ax3]
    assert g1.description == 'some axis group'
    assert g1.objecttype  == 'AXIS'

    assert g2.objects     == [param]
    assert g2.description == 'various objects'
    assert g2.objecttype  == None

    assert g3.objects     == [ax2, ch, tool]
    assert g3.description == 'messed up group'
    assert g3.groups      == [g1, g2]
    assert g3.objecttype  == 'IGNORE-ME-PLZ'

    _ = g3.describe(indent='   ', width=70, exclude='e')

def test_process(f):
    key = fingerprint('PROCESS', 'PROC1', 10, 0)
    p1 = f.objects[key]

    key = fingerprint('PARAMETER', 'PARAM1', 10, 0)
    param1 = f.objects[key]

    key = fingerprint('PARAMETER', 'PARAM3', 10, 0)
    param3 = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN1', 10, 0)
    in2 = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN3', 10, 0)
    out1 = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN2', 10, 0)
    out2 = f.objects[key]

    key = fingerprint('COMPUTATION', 'COMPUT1', 10, 0)
    ic1 = f.objects[key]

    key = fingerprint('COMPUTATION', 'COMPUT2', 10, 0)
    oc1 = f.objects[key]

    assert p1.description         == 'Random process'
    assert p1.trademark_name      == 'Cute process'
    assert p1.version             == 'The one and only'
    assert p1.properties          == ['RE-SAMPLED', 'LITHOLOGY-CORRECTED']
    assert p1.status              == 'COMPLETE'
    assert p1.input_channels      == [in2]
    assert p1.output_channels     == [out1, out2]
    assert p1.input_computations  == [ic1]
    assert p1.output_computations == [oc1]
    assert p1.parameters          == [param1, param3]
    assert p1.comments            == ["It was", "nicely", "executed", "??"]

    _ = p1.describe(indent='   ', width=70, exclude='e')

def test_path(f):
    key = fingerprint('PATH', 'PATH1', 10, 0)
    p1 = f.objects[key]

    key = fingerprint('PATH', 'PATH2', 10, 0)
    p2 = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN1', 10, 0)
    in1 = f.objects[key]

    key = fingerprint('CHANNEL', 'CHANN2', 10, 0)
    in2 = f.objects[key]

    key = fingerprint('FRAME', 'FRAME1', 10, 0)
    fr1 = f.objects[key]

    key = fingerprint('FRAME', 'FRAME2', 10, 0)
    fr2 = f.objects[key]

    key = fingerprint('WELL-REFERENCE', 'THE-WELL', 10, 0)
    wr = f.objects[key]

    assert p1.borehole_depth       == 87
    assert p1.value                == [in2, in1]
    assert p1.tool_zero_offset     == -7
    assert p1.radial_drift         == 105
    assert p1.measure_point_offset == 82
    assert p1.depth_offset         == -123
    assert p1.frame                == fr1
    assert p1.well_reference_point == wr
    assert p1.time                 == 180
    assert p1.angular_drift        == in1
    assert p1.vertical_depth       == in2

    assert p2.borehole_depth       == in2
    assert p2.value                == [in2]
    assert p2.tool_zero_offset     == -7
    assert p2.radial_drift         == in2
    assert p2.measure_point_offset == 82
    assert p2.depth_offset         == -123
    assert p2.frame                == fr2
    assert p2.well_reference_point == wr
    assert p2.time                 == in2
    assert p2.angular_drift        == 64
    assert p2.vertical_depth       == -119

    _ = p2.describe(indent='   ', width=70, exclude='e')

def test_comment(f):
    key = fingerprint('COMMENT', 'COMMENT1', 10, 0)
    com = f.objects[key]

    assert com.text == ['Trust me, this is a very nice comment',
                        "What, you don't believe me?", ':-(']

    _ = com.describe(indent='   ', width=70, exclude='e')

def test_unknown(f):
    key = fingerprint('UNKNOWN_SET', 'OBJ1', 10, 0)
    unknown = f.objects[key]

    assert unknown.stash["SOME_LIST"]   == ["LIST_V1", "LIST_V2"]
    assert unknown.stash["SOME_VALUE"]  == ["VAL1"]
    assert unknown.stash["SOME_STATUS"] == [1]

    _ = unknown.describe(indent='   ', width=70, exclude='e')

def test_unexpected_attributes(f):
    key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)
    c = f.objects[key]

    assert c.label                           == "SMTH"
    assert c.plus_tolerance                  == [] #count 0
    assert c.minus_tolerance                 == [] #not specified

    #'lnks' instead of 'references'
    assert c.stash["LNKS"]                   == [18, 32]
    #spaces are stripped for stash also
    assert c.stash["MY_PARAM"]               == ["wrong", "W"]
    # no linkage is performed for stash even for known objects
    assert c.stash["LINKS_TO_PARAMETERS"]    ==  [(10, 0, "PARAM2"),
                                                  (10, 0, "PARAMU")]
    assert c.stash["LINK_TO_UNKNOWN_OBJECT"] == [("UNKNOWN_SET",
                                                  (10, 0, "OBJ1"))]

def test_match(f):
    refs = []

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN1', 10, 0)
    refs.append( f.objects[key] )

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN2', 10, 0)
    refs.append( f.objects[key] )

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN3', 10, 0)
    refs.append( f.objects[key] )

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN4', 10, 0)
    refs.append( f.objects[key] )

    channels = f.match('CHAN.*')

    assert len(list(channels)) == 4
    for ch in channels:
        assert ch in refs

def test_match_type(f):
    refs = []

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN1', 10, 0)
    refs.append( f.objects[key] )

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN2', 10, 0)
    refs.append( f.objects[key] )

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN3', 10, 0)
    refs.append( f.objects[key] )

    key = dlisio.core.fingerprint('CHANNEL', 'CHANN4', 10, 0)
    refs.append( f.objects[key] )

    key = dlisio.core.fingerprint('LONG-NAME', 'CHANN1-LONG-NAME', 10, 0)
    refs.append( f.objects[key] )

    objs = f.match('CHAN.*', type='CHANNEL|LONG-NAME')

    assert len(list(objs)) == len(refs)
    for obj in objs:
        assert obj in refs

def test_match_invalid_regex(f):
    with pytest.raises(ValueError):
        _ = next(f.match('*'))

    with pytest.raises(ValueError):
        _ = next(f.match('AIBK', type='*'))
