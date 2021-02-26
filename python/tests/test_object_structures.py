"""
Testing objects from Chapter 5 and 6. Tests objects structure and attributes
"""

from datetime import datetime
import numpy as np

from dlisio import dlis

def test_file_header(f):
    fh = f.object('FILE-HEADER', 'N', 10, 0)
    assert fh.type       == "FILE-HEADER"
    assert fh.name       == "N"
    assert fh.origin     == 10
    assert fh.copynumber == 0
    #next two check for value space-stripping
    assert fh.sequencenr == "8"
    assert fh.id         == "some logical file"

def test_origin(f):
    def_origin = f.object('ORIGIN', 'DEFINING_ORIGIN', 10, 0)
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

    random_origin = f.object('ORIGIN', 'RANDOM', 127, 0)
    assert random_origin.origin      == 127
    assert random_origin.file_id     == "some other logical file"
    assert random_origin.file_set_nr == 1042
    assert random_origin.file_nr     == 6

def test_axis(f):
    axis = f.object('AXIS', 'AXIS2', 10, 0)

    assert axis.axis_id     == 'AX2'
    assert axis.coordinates == ['very near', 'not so far']
    assert axis.spacing     == 'a bit'

def test_longname(f):
    ln  = f.object('LONG-NAME', 'CHANN1-LONG-NAME', 10, 0)

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

def test_channel(f):
    tool     = f.object('TOOL', 'TOOL1', 10, 0)
    longname = f.object('LONG-NAME', 'CHANN1-LONG-NAME', 10, 0)
    channel  = f.object('CHANNEL', 'CHANN1', 10, 0)
    axis1    = f.object('AXIS', 'AXIS1', 10, 0)
    axis2    = f.object('AXIS', 'AXIS2', 10, 0)
    axis3    = f.object('AXIS', 'AXIS3', 10, 0)

    assert channel.long_name     == longname
    assert channel.properties    == ["AVERAGED", "DERIVED", "PATCHED"]
    assert channel.reprc         == 16
    assert channel.dimension     == [4, 3, 2]
    assert channel.axis          == [axis3, axis2, axis1]
    assert channel.element_limit == [11, 15, 10]
    assert channel.source        == tool

    assert channel.attic["DIMENSION"].value     == [2, 3, 4]
    assert channel.attic["ELEMENT-LIMIT"].value == [10, 15, 11]
    assert channel.attic["AXIS"].value          == [(10, 0, 'AXIS1'),
                                                    (10, 0, 'AXIS2'),
                                                    (10, 0, 'AXIS3')]

def test_frame(f):
    channel1 = f.object('CHANNEL', 'CHANN1', 10, 0)
    channel2 = f.object('CHANNEL', 'CHANN2', 10, 0)
    frame1   = f.object('FRAME', 'FRAME1', 10, 0)

    assert frame1.description == "Main frame"
    assert frame1.channels    == [channel1, channel2]
    assert frame1.index_type  == "BOREHOLE-DEPTH"
    assert frame1.direction   == "DECREASING"
    assert frame1.spacing     == 119
    assert frame1.encrypted   == False
    assert frame1.index_min   == 1
    assert frame1.index_max   == 100

    frame2 = f.object('FRAME', 'FRAME2', 10, 0)

    #for second frame many attributes are absent
    assert frame2.description == "Secondary frame"
    assert frame2.channels    == []
    assert frame2.index_type  == None
    assert frame2.direction   == None
    assert frame2.spacing     == None
    assert frame2.encrypted   == True #attribute present
    assert frame2.index_min   == None
    assert frame2.index_max   == None

def test_zone(f):
    zone = f.object('ZONE', 'ZONE-A', 10, 0)

    assert zone.description == 'Some along zone'
    assert zone.domain      == 'VERTICAL-DEPTH'
    assert zone.maximum     == 13398
    assert zone.minimum     == 8603

def test_parameter(f):
    p        = f.object('PARAMETER', 'PARAM3', 10, 0)
    longname = f.object('LONG-NAME', 'PARAM3-LONG', 10, 0)
    zoneA    = f.object('ZONE', 'ZONE-A', 10, 0)
    axis2    = f.object('AXIS', 'AXIS2', 10, 0)
    axis3    = f.object('AXIS', 'AXIS3', 10, 0)

    assert p.long_name == longname
    assert p.dimension == [2, 3]
    assert p.axis      == [axis3, axis2]
    assert p.zones     == [zoneA, None, None, None]

    assert p.attic["DIMENSION"].value  == [3, 2]
    assert len(p.attic["AXIS"].value)  == 2
    assert len(p.attic["ZONES"].value) == 4

    sample = np.reshape(np.array([1, 2, 3, 4, 5, 6]), (2,3))

    assert np.array_equal(p.values[0], sample)
    assert np.array_equal(p.values[1][1], np.array([10, 11, 12]))

    assert p.values[2][0][1] == 14
    assert p.values[3][1][2] == 24

    p = f.object('PARAMETER', 'PARAM1', 10, 0)
    longname = f.object('LONG-NAME', 'PARAM1-LONG', 10, 0)

    assert p.long_name == longname

    value = p.values[0]
    assert np.array_equal(value, np.array([101, 120]))

def test_equipment(f):
    e = f.object('EQUIPMENT', 'EQUIP1', 10, 0)
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
    e        = f.object('EQUIPMENT', 'EQUIP1', 10, 0)
    param1   = f.object('PARAMETER', 'PARAM1', 10, 0)
    param2   = f.object('PARAMETER', 'PARAM2', 10, 0)
    channel1 = f.object('CHANNEL', 'CHANN1', 10, 0)
    channel2 = f.object('CHANNEL', 'CHANN2', 10, 0)
    tool     = f.object('TOOL', 'TOOL1', 10, 0)

    assert tool.description              == "description of tool 1"
    assert tool.trademark_name           == "TOOL123"
    assert tool.generic_name             == "Important tool"
    assert tool.parts                    == [e]
    assert tool.status                   == True
    assert tool.channels                 == [channel1, channel2]
    assert tool.parameters               == [param1, None, param2]
    assert len(tool.attic['PARAMETERS'].value) == 3

def test_message(f):
    mes = f.object('MESSAGE', 'MESSAGE1', 10, 0)

    assert mes.message_type   == 'SYSTEM'
    assert mes.time           == datetime(1990, 4, 20, 12, 58, 59, 1000)
    assert mes.borehole_drift == 65282
    assert mes.vertical_depth == 120
    assert mes.radial_drift   == 65093
    assert mes.angular_drift  == 344
    assert mes.text           == ['System says hi!']

def test_measurement(f):
    tool  = f.object('TOOL', 'TOOL1', 10, 0)
    m     = f.object('CALIBRATION-MEASUREMENT', 'MEAS1', 10, 0)
    axis1 = f.object('AXIS', 'AXIS1', 10, 0)
    axis2 = f.object('AXIS', 'AXIS2', 10, 0)

    assert m.phase       == "MASTER"
    assert m.source      == tool
    assert m.mtype       == "Zero"
    assert m.dimension   == [3, 2]
    assert m.axis        == [axis2, axis1]
    assert m.samplecount == 4
    assert m.begin_time  == 13447
    assert m.duration    == 21
    assert m.standard    == [1]

    assert m.attic["DIMENSION"].value == [2, 3]

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

def test_coefficient(f):
    c = f.object('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)

    assert c.label           == "GAIN"
    assert c.coefficients    == [18, 25]
    assert c.references      == [18, 32]
    assert c.plus_tolerance  == [1, 1]
    assert c.minus_tolerance == [2, 1]

def test_calibration(f):
    param1   = f.object('PARAMETER', 'PARAM1', 10, 0)
    param2   = f.object('PARAMETER', 'PARAM2', 10, 0)
    param3   = f.object('PARAMETER', 'PARAM3', 10, 0)
    meas1    = f.object('CALIBRATION-MEASUREMENT', 'MEAS1', 10, 0)
    meas2    = f.object('CALIBRATION-MEASUREMENT', 'MEAS2', 10, 0)
    coeff1   = f.object('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)
    coeff2   = f.object('CALIBRATION-COEFFICIENT', 'COEFF2', 10, 0)
    channel1 = f.object('CHANNEL', 'CHANN1', 10, 0)
    channel2 = f.object('CHANNEL', 'CHANN2', 10, 0)
    channel3 = f.object('CHANNEL', 'CHANN3', 10, 0)
    channel4 = f.object('CHANNEL', 'CHANN4', 10, 0)
    c        = f.object('CALIBRATION', 'CALIBR1', 10, 0)

    assert c.calibrated   == [channel1, channel2]
    assert c.uncalibrated == [channel3, channel4]
    assert c.coefficients == [coeff1, coeff2]
    assert c.measurements == [meas1, meas2]
    assert c.parameters   == [param1, param2, param3]
    assert c.method       == "USELESS"

def test_computation(f):
    com     = f.object('COMPUTATION', 'COMPUT2', 10, 0)
    axis2   = f.object('AXIS', 'AXIS2', 10, 0)
    axis3   = f.object('AXIS', 'AXIS3', 10, 0)
    zone    = f.object('ZONE', 'ZONE-A', 10, 0)
    process = f.object('PROCESS', 'PROC1', 10, 0)

    assert com.long_name  == 'computation object 2'
    assert com.properties == ['MUDCAKE-CORRECTED', 'DEPTH-MATCHED']
    assert com.dimension  == [4, 2]
    assert com.axis       == [axis3, axis2]
    assert com.zones      == [zone]
    assert com.source     == process

    assert com.attic["DIMENSION"].value == [2, 4]

    values  = np.array([[140, 99], [144, 172], [202, 52], [109, 120]])
    assert np.array_equal(com.values[0], values)

def test_splice(f):
    splice = f.object('SPLICE', 'SPLICE1', 10, 0)
    in1    = f.object('CHANNEL', 'CHANN4', 10, 0)
    in2    = f.object('CHANNEL', 'CHANN1', 10, 0)
    zone1  = f.object('ZONE', 'ZONE-A', 10, 0)

    # Output channel does not exist, but should be accessible through attic
    assert splice.output_channel == None
    assert splice.attic['OUTPUT-CHANNEL'].value[0].id         == 'CHANN-NEW'
    assert splice.attic['OUTPUT-CHANNEL'].value[0].origin     == 10
    assert splice.attic['OUTPUT-CHANNEL'].value[0].copynumber ==  0

    assert splice.input_channels == [in1, in2]

    # Second zone does not exist, but should be accessible through attic
    assert splice.zones                       == [zone1 , None]
    assert splice.attic['ZONES'].value[1].id         == 'ZONE-B'
    assert splice.attic['ZONES'].value[1].origin     == 10
    assert splice.attic['ZONES'].value[1].copynumber == 0

def test_wellref(f):
    wellref = f.object('WELL-REFERENCE', 'THE-WELL', 10, 0)

    assert wellref.permanent_datum           == 'Ground Level'
    assert wellref.vertical_zero             == 'Kelly Bushing'
    assert wellref.permanent_datum_elevation == -89
    assert wellref.above_permanent_datum     == -5
    assert wellref.magnetic_declination      == -22

    assert wellref.coordinates['longitude']  == -11.25
    assert wellref.coordinates['latitude']   == 60.75
    assert wellref.coordinates['elevation']  == 0.25

def test_group(f):
    g1    = f.object('GROUP', 'GROUP1', 10, 0)
    param = f.object('PARAMETER', 'PARAM3', 10, 0)
    g2    = f.object('GROUP', 'GROUP2', 10, 0)
    g3    = f.object('GROUP', 'GROUP3', 10, 0)
    ch    = f.object('CHANNEL', 'CHANN3', 10, 0)
    tool  = f.object('TOOL', 'TOOL1', 10, 0)
    ax1   = f.object('AXIS', 'AXIS1', 10, 0)
    ax2   = f.object('AXIS', 'AXIS2', 10, 0)
    ax3   = f.object('AXIS', 'AXIS3', 10, 0)

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

def test_process(f):
    p1     = f.object('PROCESS', 'PROC1', 10, 0)
    param1 = f.object('PARAMETER', 'PARAM1', 10, 0)
    param3 = f.object('PARAMETER', 'PARAM3', 10, 0)
    in2    = f.object('CHANNEL', 'CHANN1', 10, 0)
    out1   = f.object('CHANNEL', 'CHANN3', 10, 0)
    out2   = f.object('CHANNEL', 'CHANN2', 10, 0)
    ic1    = f.object('COMPUTATION', 'COMPUT1', 10, 0)
    oc1    = f.object('COMPUTATION', 'COMPUT2', 10, 0)

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

def test_path(f):
    p1  = f.object('PATH', 'PATH1', 10, 0)
    p2  = f.object('PATH', 'PATH2', 10, 0)
    in1 = f.object('CHANNEL', 'CHANN1', 10, 0)
    in2 = f.object('CHANNEL', 'CHANN2', 10, 0)
    fr1 = f.object('FRAME', 'FRAME1', 10, 0)
    fr2 = f.object('FRAME', 'FRAME2', 10, 0)
    wr  = f.object('WELL-REFERENCE', 'THE-WELL', 10, 0)

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

def test_comment(f):
    com = f.object('COMMENT', 'COMMENT1', 10, 0)

    assert com.text == ['Trust me, this is a very nice comment',
                        "What, you don't believe me?", ':-(']

def test_noformat(f):
    noformat = f.object('NO-FORMAT', 'NOFORMAT-IMAGE', 10, 0)

    assert noformat.consumer_name == "PNG image"
    assert noformat.description   == "dlisio logo"

def test_update_just_warning(fpath, assert_log):
    with dlis.load(fpath) as _:
        assert_log('contains UPDATE-object')

def test_unknown(f):
    unknown = f.object('UNKNOWN_SET', 'OBJ1', 10, 0)

    assert unknown.stash["SOME_LIST"]   == ["LIST_V1", "LIST_V2"]
    assert unknown.stash["SOME_VALUE"]  == ["VAL1"]
    assert unknown.stash["SOME_STATUS"] == [1]

def test_incomplete_object(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('load').join('incomplete_object.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/channel-inc.dlis.part',
    ]
    merge_files_manyLR(fpath, content)

    with dlis.load(fpath) as (f, *_):
        channel = f.object('CHANNEL', 'INC-CH1', 10, 0)
        assert channel.long_name     == "Incomplete channel1"
        assert channel.properties    == []
        assert channel.reprc         == 15
        assert channel.dimension     == [1]
        assert channel.axis          == []
        assert channel.element_limit == []
        assert channel.source        == None

