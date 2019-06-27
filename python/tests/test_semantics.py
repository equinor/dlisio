import pytest
from datetime import datetime
import numpy as np

from dlisio.core import fingerprint
from dlisio.plumbing import valuetypes, linkage, dataobject
from dlisio.plumbing.coefficient import Coefficient
from dlisio.plumbing.measurement import Measurement

import dlisio

from . import merge_files

@pytest.fixture(scope="module")
def fpath(tmpdir_factory, merge_files):
    path = str(tmpdir_factory.mktemp('semantic').join('semantic.dlis'))
    content = [
        'data/semantic/envelope.dlis.part',
        'data/semantic/file-header.dlis.part',
        'data/semantic/origin.dlis.part',
        'data/semantic/well-reference-point.dlis.part',
        'data/semantic/axis.dlis.part',
        'data/semantic/long-name-record.dlis.part',
        'data/semantic/channel.dlis.part',
        'data/semantic/frame.dlis.part',
        'data/semantic/fdata-frame1-1.dlis.part',
        'data/semantic/fdata-frame1-2.dlis.part',
        'data/semantic/fdata-frame1-3.dlis.part',
        'data/semantic/path.dlis.part',
        'data/semantic/zone.dlis.part',
        'data/semantic/parameter.dlis.part',
        'data/semantic/equipment.dlis.part',
        'data/semantic/tool.dlis.part',
        'data/semantic/process.dlis.part',
        'data/semantic/computation.dlis.part',
        'data/semantic/measurement.dlis.part',
        'data/semantic/coefficient.dlis.part',
        'data/semantic/coefficient-wrong.dlis.part',
        'data/semantic/calibration.dlis.part',
        'data/semantic/group.dlis.part',
        'data/semantic/splice.dlis.part',
        'data/semantic/message.dlis.part',
        'data/semantic/comment.dlis.part',
        'data/semantic/update.dlis.part',
        'data/semantic/unknown.dlis.part',
        'data/semantic/channel-reprcode.dlis.part',
        'data/semantic/frame-reprcode.dlis.part',
        'data/semantic/fdata-reprcode.dlis.part',
        'data/semantic/file-header2.dlis.part',
        'data/semantic/origin2.dlis.part',
        'data/semantic/channel-dimension.dlis.part',
        'data/semantic/frame-dimension.dlis.part',
        'data/semantic/fdata-dimension.dlis.part',
    ]
    merge_files(path, content)
    return path

@pytest.fixture(scope="module")
def f(tmpdir_factory, fpath):
    with dlisio.load(fpath) as (f, *tail):
        yield f

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

def test_axis(f):
    key = fingerprint('AXIS', 'AXIS2', 10, 0)
    axis = f.objects[key]

    assert axis.axis_id     == 'AX2'
    assert axis.coordinates == ['very near', 'not so far']
    assert axis.spacing     == 'a bit'

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

def test_parameter(f):
    key = fingerprint('PARAMETER', 'PARAM3', 10, 0)
    param = f.objects[key]

    key = fingerprint('LONG-NAME', 'PARAM3-LONG', 10, 0)
    longname = f.objects[key]
    key = fingerprint('ZONE', 'ZONE-A', 10, 0)
    zoneA = f.objects[key]
    key = fingerprint('AXIS', 'AXIS2', 10, 0)
    axis2 = f.objects[key]
    key = fingerprint('AXIS', 'AXIS3', 10, 0)
    axis3 = f.objects[key]

    assert param.long_name                 == longname
    assert param.dimension                 == [2, 3]
    assert param.attic["DIMENSION"]        == [3, 2]
    assert param.axis                      == [axis3, axis2]
    assert len(param.attic["AXIS"])        == 2
    assert param.zones                     == [zoneA, None, None, None]
    assert len(param.attic["ZONES"])       == 4
    assert len(param.datapoints["values"]) == 24

    key = fingerprint('PARAMETER', 'PARAM1', 10, 0)
    param = f.objects[key]
    key = fingerprint('LONG-NAME', 'PARAM1-LONG', 10, 0)
    longname = f.objects[key]
    assert param.long_name                 == longname
    assert param.datapoints["values"][0:2] == [101, 120]

    key = fingerprint('PARAMETER', 'PARAM2', 10, 0)
    param = f.objects[key]
    key = fingerprint('LONG-NAME', 'PARAM2-LONG', 10, 0)
    longname = f.objects[key]
    assert param.long_name                 == longname
    assert param.datapoints["values"][0:2] == [131, 69]

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
    assert m.datapoints["samples"][0:6]    == [240, 137, 228, 120, 240, 136]
    assert m.datapoints["max_deviation"]   == [2.5, 2.5, 2.5, 2.75, 2.5, 2.5]
    assert m.datapoints["std_deviation"]   == [-14.25, -14.25, -14.25,
                                               -14.25, -14, -14.25]
    assert m.datapoints["reference"]       == [240, 135, 240, 135, 240, 135]
    assert m.datapoints["plus_tolerance"]  == [5, 10, 5, 10, 5, 10]
    assert m.datapoints["minus_tolerance"] == [1, 1, 1, 1, 1, 1]

def test_coefficient(f):
    key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)
    c = f.objects[key]

    assert c.label           == "GAIN"
    assert c.coefficients    == [18, 25]
    assert c.references      == [18, 32]
    assert c.plus_tolerance  == [1, 1]
    assert c.minus_tolerance == [2, 1]

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

def test_computation(f):
    key = fingerprint('COMPUTATION', 'COMPUT2', 10, 0)
    com = f.objects[key]

    key = fingerprint('AXIS', 'AXIS2', 10, 0)
    axis2 = f.objects[key]

    key = fingerprint('AXIS', 'AXIS3', 10, 0)
    axis3 = f.objects[key]

    key = fingerprint('ZONE', 'ZONE-A', 10, 0)
    zone = f.objects[key]

    assert com.long_name            == 'computation object 2'
    assert com.properties           == ['MUDCAKE-CORRECTED', 'DEPTH-MATCHED']
    assert com.dimension            == [4, 2]
    assert com.attic["DIMENSION"]   == [2, 4]
    assert com.axis                 == [axis3, axis2]
    assert com.zones                == [zone]
    assert com.refs['source']       == [('PROCESS', (10, 0, 'PROC1'))]
    assert com.datapoints["values"] == [140, 99, 144, 172, 202, 52, 109, 120]


def test_unknown(f):
    key = fingerprint('UNKNOWN_SET', 'OBJ1', 10, 0)
    unknown = f.objects[key]

    assert unknown.stash["SOME_LIST"]   == ["LIST_V1", "LIST_V2"]
    assert unknown.stash["SOME_VALUE"]  == ["VAL1"]
    assert unknown.stash["SOME_STATUS"] == [1]

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

def test_dynamic_class(fpath):
    with dlisio.load(fpath) as (f, _):
        class ActuallyKnown(dlisio.plumbing.basicobject.BasicObject):
            attributes = {
                "SOME_LIST"   : valuetypes.vector('list'),
                "SOME_VALUE"  : valuetypes.scalar('value'),
                "SOME_STATUS" : valuetypes.boolean('status'),
            }

            def __init__(self, obj = None, name = None):
                super().__init__(obj, name = name, type = "UNKNOWN_SET")
                self.list = []
                self.value = None
                self.status = None

        key = fingerprint('UNKNOWN_SET', 'OBJ1', 10, 0)
        unknown = f.objects[key]
        with pytest.raises(AttributeError):
            assert unknown.value == "VAL1"

        f.types['UNKNOWN_SET'] = ActuallyKnown.create
        f.load()

        key = fingerprint('UNKNOWN_SET', 'OBJ1', 10, 0)
        unknown = f.objects[key]

        assert unknown.list == ["LIST_V1", "LIST_V2"]
        assert unknown.value == "VAL1"
        assert unknown.status == True

def test_change_object_type(f):
    try:
        # Parse all parameters as if they where Channels
        dlisio.dlis.types['PARAMETER'] = dlisio.plumbing.Channel.create
        f.load()

        key = dlisio.core.fingerprint('LONG-NAME', 'PARAM1-LONG', 10, 0)
        longname = f.objects[key]

        key = dlisio.core.fingerprint('AXIS', 'AXIS1', 10, 0)
        axis = f.objects[key]

        key = dlisio.core.fingerprint('CHANNEL', 'PARAM1', 10, 0)
        obj = f.objects[key]

        # obj should have been parsed as a Channel
        assert isinstance(obj, dlisio.plumbing.Channel)

        # Parameter attributes that's also Channel attributes should be
        # parsed normally
        assert obj.long_name         == longname
        assert obj.dimension         == [2]
        assert obj.axis              == [axis]

        # Parameter attributes that's not in Channel should end up in stash
        assert obj.stash['VALUES']   == [101, 120]
        assert obj.stash['ZONES']    == [(10, 0, 'ZONE-A')]

    finally:
        # even if the test fails, make sure that types is reset to its default,
        # to not interfere with other tests
        dlisio.dlis.types['PARAMETER'] = dlisio.plumbing.Parameter.create

def test_remove_object_type(f):
    try:
        # Deleting object-type CHANNEL and reload
        del dlisio.dlis.types['CHANNEL']
        f.load()

        key = dlisio.core.fingerprint('CHANNEL', 'CHANN1', 10, 0)
        obj = f.objects[key]

        # Channel should be parsed as Unknown, but the type should still
        # reflects what's on file
        assert isinstance(obj, dlisio.plumbing.Unknown)
        assert obj in f.unknowns
        assert obj.type == 'CHANNEL'

    finally:
        # even if the test fails, make sure that types is reset to its default,
        # to not interfere with other tests
        f.types['CHANNEL'] = dlisio.plumbing.Channel.create

    f.load()
    obj = f.objects[key]

    # Channels should now be parsed as Channel.allobjects
    assert isinstance(obj, dlisio.plumbing.Channel)
    assert obj not in f.unknowns

def test_dynamic_instance_attribute(fpath):
    with dlisio.load(fpath) as (f, _):
        key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)
        c = f.objects[key]
        # update attributes only for one object
        c.attributes = dict(c.attributes)
        c.attributes['MY_PARAM'] = valuetypes.vector('myparams')

        c.load()
        assert c.myparams == ["wrong", "W"]

        # check that other object of the same type is not affected
        key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)
        c = f.objects[key]

        with pytest.raises(KeyError):
            c.attributes['myparams']

def test_dynamic_class_attribute(fpath):
    with dlisio.load(fpath) as (f, _):
        try:
            # update attribute for the class
            Coefficient.attributes['MY_PARAM'] = valuetypes.vector('myparams')

            key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)
            c = f.objects[key]

            assert c.attributes['MY_PARAM'] == valuetypes.vector('myparams')
            c.load()
            assert c.myparams == ["wrong", "W"]

        finally:
            # manual cleanup. "reload" doesn't work
            del c.__class__.attributes['MY_PARAM']

def test_dynamic_linkage(fpath):
    with dlisio.load(fpath) as (f, _):
        key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)
        c = f.objects[key]

        c.attributes = dict(c.attributes)
        c.attributes['LINKS_TO_PARAMETERS'] = valuetypes.vector('paramlinks')
        c.attributes['LINK_TO_UNKNOWN_OBJECT'] = (
                    valuetypes.scalar('unknown_link'))

        c.load()

        c.linkage = dict(c.linkage)
        c.linkage['label']        = linkage.obname("EQUIPMENT")
        c.linkage['paramlinks']   = linkage.obname("PARAMETER")
        c.linkage['unknown_link'] = linkage.objref
        c.linkage['notlink']      = linkage.objref
        c.linkage['wrongobname']  = "i am just wrong obname"
        c.linkage['wrongobjref']  = "i am just wrong objref"

        c.refs["notlink"]     = "i am no link"
        c.refs["wrongobname"] = c.refs["paramlinks"]
        c.refs["wrongobjref"] = c.refs["unknown_link"]

        c.link(f.objects)

        key = fingerprint('PARAMETER', 'PARAM2', 10, 0)
        param2 = f.objects[key]
        key = fingerprint('UNKNOWN_SET', 'OBJ1', 10, 0)
        u = f.objects[key]

        assert c.label        == "SMTH"
        assert c.paramlinks   == [param2, None]
        assert c.unknown_link == u

def test_dynamic_datamap(fpath):
    try:
        #if user doesn't want to reshape
        del Measurement.datamap['minus_tolerance']
        with dlisio.load(fpath) as (f, _):
            key = fingerprint('CALIBRATION-MEASUREMENT', 'MEAS1', 10, 0)
            m = f.objects[key]
            m.shapedata()

            assert np.array_equal(m.plus_tolerance, [[5, 10], [5, 10], [5, 10]])
            assert m.minus_tolerance == [1, 1, 1, 1, 1, 1]
    finally:
        Measurement.datamap['minus_tolerance'] = dataobject.simple

def test_dynamic_change_through_instance(fpath):
    with dlisio.load(fpath) as (f, _):
        try:
            key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)
            c = f.objects[key]
            c.attributes['MY_PARAM']            = valuetypes.vector('myparams')
            c.attributes['LINKS_TO_PARAMETERS'] = (
                        valuetypes.vector('paramlinks'))
            c.linkage['paramlinks']             = linkage.obname("PARAMETER")

            key = fingerprint('PARAMETER', 'PARAM2', 10, 0)
            param2 = f.objects[key]
            key = fingerprint('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)
            c = f.objects[key]
            c.load()
            c.link(f.objects)

            assert c.myparams     == ["wrong", "W"]
            assert c.paramlinks   == [param2, None]

        finally:
            del c.attributes['MY_PARAM']
            del c.attributes['LINKS_TO_PARAMETERS']
            del c.linkage['paramlinks']

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
