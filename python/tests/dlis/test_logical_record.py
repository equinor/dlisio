"""
Testing logical record data representation level - Chapter 3.
"""

import pytest
from datetime import datetime
import os, sys

from dlisio import dlis
from dlisio.core import dlis_reprc as reprc

@pytest.mark.future_test_attributes
def test_default_attribute(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'default_attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/empty.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 2
        #assert attr.reprc == dlisio.core.reprc.fdoubl
        assert attr.units == 'default attr units'
        assert attr.value == [-0.75, 10.0]


def test_default_attribute_cut(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'default_attribute_cut.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['INVARIANT_ATTRIBUTE'].value
        assert obj.attic['DEFAULT_ATTRIBUTE'].value

@pytest.mark.future_test_attributes
def test_invariant_attribute(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'invariant_attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['INVARIANT_ATTRIBUTE']
        #assert attr.count == 3
        #assert attr.reprc == dlisio.core.reprc.status
        assert attr.units == 'invariant units'
        assert attr.value == [False, False, True]


def test_invariant_attribute_in_object(tmpdir, merge_files_oneLR, assert_log):
    path = os.path.join(str(tmpdir), 'invariant-attribute-in-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/invariant.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        assert attr.value == [8.0]

        _ = obj['DEFAULT_ATTRIBUTE']
        assert_log("Invariant attribute")


def test_absent_attribute(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'attribute_absent.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/absent.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['INVARIANT_ATTRIBUTE'].value
        with pytest.raises(KeyError):
            _ = obj.attic['DEFAULT_ATTRIBUTE']


def test_absent_attribute_in_template(tmpdir, merge_files_oneLR, assert_log):
    path = os.path.join(str(tmpdir), 'absent-attribute-in-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/absent.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['DEFAULT_ATTRIBUTE'].value
        assert_log("Absent Attribute in object set template")

@pytest.mark.future_test_attributes
def test_global_default_attribute(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'global-default-attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/global-default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/empty.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['GLOBAL_DEFAULT_ATTRIBUTE']
        #assert attr.count == 1
        #assert attr.reprc == dlisio.core.reprc.ident
        assert attr.units == ''
        assert attr.value == ['']


@pytest.mark.future_test_attributes
def test_all_attribute_bits(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'global-all-attribute-bits.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/all-set.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 4
        #assert attr.reprc == dlisio.core.reprc.ushort
        assert attr.units == 'overwritten units'
        assert attr.value == [1, 2, 3, 4]


def test_objattr_same_as_default_no_value(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'same-as-default-but-no-value.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/repeat-default-novalue.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        assert attr.value == [-0.75, 10.0]


def test_no_template(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'no-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f,):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert len(obj.attic) == 0


@pytest.mark.future_test_attributes
@pytest.mark.not_implemented_datetime_timezone
@pytest.mark.parametrize("filename_p, attr_n, attr_reprc, attr_v", [
    ("01-fshort", 'FSHORT', reprc.fshort, -1),
    ("02-fsingl", 'FSINGL', reprc.fsingl, 5.5),
    ("03-fsing1", 'FSING1', reprc.fsing1, (-2, 2)),
    ("04-fsing2", 'FSING2', reprc.fsing2, (117, -13.25, 32444)),
    ("05-isingl", 'ISINGL', reprc.isingl, -12),
    ("06-vsingl", 'VSINGL', reprc.vsingl, 0.125),
    ("07-fdoubl", 'FDOUBL', reprc.fdoubl, 900000000000000.5),
    ("08-fdoub1", 'FDOUB1', reprc.fdoub1, (-13.5, -27670)),
    ("09-fdoub2", 'FDOUB2', reprc.fdoub2, (6728332223, -45.75, -0.0625)),
    ("10-csingl", 'CSINGL', reprc.csingl, complex(93, -14)),
    ("11-cdoubl", 'CDOUBL', reprc.cdoubl, complex(125533556, -4.75)),
    ("12-sshort", 'SSHORT', reprc.sshort, 89),
    ("13-snorm",  'SNORM',  reprc.snorm,  -153),
    ("14-slong",  'SLONG',  reprc.slong,  2147483647),
    ("15-ushort", 'USHORT', reprc.ushort, 6),
    ("16-unorm",  'UNORM',  reprc.unorm,  32921),
    ("17-ulong",  'ULONG',  reprc.ulong,  1),
    ("18-uvari",  'UVARI',  reprc.uvari,  257),
    ("19-ident",  'IDENT',  reprc.ident,  "VALUE"),
    ("20-ascii",  'ASCII',  reprc.ascii,  "ASCII VALUE"),
    ("21-dtime",  'DTIME',  reprc.dtime,  datetime(1971,
                                                   3, 21, 18,
                                                   4, 14, 386000)),
    ("22-origin", 'ORIGIN', reprc.origin, 16777217),
    ("23-obname", 'OBNAME', reprc.obname, (18, 5, "OBNAME_I")),
    ("24-objref", 'OBJREF', reprc.objref, ("OBJREF_I",
                                          (25, 3, "OBJREF_OBNAME"))),
    ("25-attref", 'ATTREF', reprc.attref, ("FIRST_INDENT",
                                          (3, 2, "ATTREF_OBNAME"),
                                          "SECOND_INDENT")),
    ("26-status", 'STATUS', reprc.status, True),
    ("27-units",  'UNITS',  reprc.units,  "unit"),
])


def test_repcode(tmpdir, merge_files_oneLR, filename_p, attr_n, attr_reprc, attr_v):
    path = os.path.join(str(tmpdir), filename_p + '.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/repcode/' + filename_p + '.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic[attr_n]
        #assert attr.reprc == attr_reprc
        assert attr.value == [attr_v]

def test_repcode_invalid_datetime(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'invalid_dtime.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/repcode/invalid-dtime.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)

        # run this test from python 3.6 only as code doesn't fail on python 3.5
        # check might be removed once we remove support for python 3.5
        if sys.version_info.major >= 3 and sys.version_info.minor > 5:
            with pytest.raises(ValueError) as excinfo:
                _ = obj.attic['DTIME'].value
            assert "month must be in 1..12" in str(excinfo.value)

def test_repcode_invalid_in_template_value(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'invalid-repcode-template-value.dlis')

    # template for attribute 'INVALID':
    # repcode = 0  # invalid
    # value = [bytes] # value is declared to be present

    # attribute 'INVALID' in obj 'OBJECT':
    # repcode = USHORT  # valid
    # value = [1, 2, 3, 4]  # valid value
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invalid-repcode-value.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/all-set.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            f.load()
    assert "unknown representation code" in str(excinfo.value)


def test_repcode_invalid_in_template_no_value_fixed(tmpdir, merge_files_oneLR,
                                                    assert_info,
                                                    assert_message_count):
    path = os.path.join(str(tmpdir), 'invalid-repcode-template-fixed.dlis')

    # template for attribute 'INVALID':
    # repcode = 0  # invalid
    # value = None # no value

    # attribute 'INVALID' in obj 'OBJECT':
    # repcode = USHORT  # valid
    # value = [1, 2, 3, 4]  # valid value
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invalid-repcode-no-value.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/all-set.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)

        _ = obj['DEFAULT_ATTRIBUTE']
        assert_info("Problem:      One or more attributes "
                    "of this object violate specification")
        assert_info("Where:        T.VERY_MUCH_TESTY_SET-I.OBJECT-O.1-C.1")

        attr = obj.attic['INVALID']
        assert attr.value == [1, 2, 3, 4]

        _ = obj['INVALID']
        assert_info("Problem:      Invalid representation code 0\n"
                    "Where:        "
                    "T.VERY_MUCH_TESTY_SET-I.OBJECT-O.1-C.1-A.INVALID")

        assert_message_count("Invalid representation code", 1)
        assert_message_count("One or more attributes", 2)

def test_repcode_invalid_in_template_no_value_not_fixed(tmpdir,
                                                        merge_files_oneLR,
                                                        assert_info):
    path = os.path.join(str(tmpdir), 'invalid-repcode-template-bad.dlis')


    # template for attribute 'INVALID':
    # repcode = 0  # invalid
    # value = None # no value

    # attribute 'INVALID' in obj 'OBJECT' is implicitly taken from template
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invalid-repcode-no-value.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)
    with dlis.load(path) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['INVALID']
        # note that behavior is different from the one below
        # here we never process the attribute, hence error is not triggered
        assert attr.value == None

        _ = obj['INVALID']
        assert_info("Invalid representation code 0")

def test_repcode_invalid_in_template_no_value_empty(tmpdir, merge_files_oneLR,
                                                    assert_log, assert_info):
    path = os.path.join(str(tmpdir), 'invalid-repcode-template-bad-empty.dlis')

    # template for attribute 'INVALID':
    # repcode = 0  # invalid
    # value = None # no value

    # attribute 'INVALID' in obj 'OBJECT' is explicitly taken from template

    # attribute 'INVALID' in obj 'OBJECT2':
    # repcode = USHORT  # valid
    # value = [1, 2, 3, 4]  # valid value
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invalid-repcode-no-value.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/empty.dlis.part',
        'data/chap3/object/object2.dlis.part',
        'data/chap3/objattr/all-set.dlis.part',
    ]
    merge_files_oneLR(path, content)
    with dlis.load(path) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        with pytest.raises(RuntimeError) as excinfo:
            # note that behavior is different from the one above
            # by adding "empty", we process the attribute, hence trigger error
            _ = obj['INVALID']
        assert "invalid representation code" in str(excinfo.value)

        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT2', 1, 1)
        attr = obj.attic['INVALID']
        assert attr.value == [1, 2, 3, 4]

        _ = obj['INVALID']
        assert_info(
            "Problem:      Invalid representation code 0\n"
            "Where:        T.VERY_MUCH_TESTY_SET-I.OBJECT2-O.1-C.1-A.INVALID")

def test_repcode_invalid_in_objects_value(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'invalid-repcode-object.dlis')

    # template for attribute 'DEFAULT_ATTRIBUTE':
    # repcode = FDOUBLE  # valid
    # value = [value1, value2] # valid

    # attribute 'DEFAULT_ATTRIBUTE' in obj 'OBJECT':
    # repcode = 32  # invalid
    # value = [bytes]  # value is declared to be present
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/reprcode-invalid-value.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            f.load()
    assert "unknown representation code" in str(excinfo.value)

def test_repcode_invalid_in_objects_no_value(tmpdir, merge_files_oneLR,
                                             assert_log, assert_message_count):
    path = os.path.join(str(tmpdir), 'invalid-repcode-object-no-value.dlis')

    # template for attribute 'GLOBAL_DEFAULT_ATTRIBUTE' is empty

    # attribute 'GLOBAL_DEFAULT_ATTRIBUTE' in obj 'OBJECT':
    # repcode = 32  # invalid
    # value = None  # no value is present

    # attribute 'GLOBAL_DEFAULT_ATTRIBUTE' in obj 'OBJECT2':
    # repcode = USHORT  # valid
    # value = [1, 2, 3, 4]  # valid value
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/global-default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/reprcode-invalid-no-value.dlis.part',
        'data/chap3/object/object2.dlis.part',
        'data/chap3/objattr/all-set.dlis.part',
    ]
    merge_files_oneLR(path, content)
    with dlis.load(path) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj['GLOBAL_DEFAULT_ATTRIBUTE']
        assert "invalid representation code" in str(excinfo.value)
        assert_log("value is not explicitly set")

        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT2', 1, 1)
        attr = obj.attic['GLOBAL_DEFAULT_ATTRIBUTE']
        assert attr.value == [1, 2, 3, 4]

        assert_message_count("value is not explicitly set", 1)
        assert_message_count("One or more attributes", 1)

def test_repcode_different_no_value(tmpdir, merge_files_oneLR, assert_log,
                                    assert_info):
    path = os.path.join(str(tmpdir), 'different-repcode-no-value.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/csingle-novalue.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)

        attr = obj['DEFAULT_ATTRIBUTE']
        assert attr == [0j, 0j]
        assert_log("value is not explicitly set")

@pytest.mark.future_test_attributes
def test_count0_novalue(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'count0-novalue.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count0-novalue-bit.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 0
        assert attr.value == None


@pytest.mark.future_test_attributes
def test_count0_value_bit(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'count0-value-bit.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count0-value-bit.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 0
        assert attr.value == None


@pytest.mark.future_test_attributes
def test_count0_different_repcode(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'count0-different-repcode.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count0-different-repcode.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 0
        #assert attr.reprc == dlisio.core.reprc.units
        assert attr.value == None


def test_label_bit_set_in_attribute(tmpdir, merge_files_oneLR, assert_log):
    path = os.path.join(str(tmpdir), 'label_bit_set_in_attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/label-bit-set.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['DEFAULT_ATTRIBUTE'].value

        _ = obj['DEFAULT_ATTRIBUTE']
        assert_log("Label bit")

@pytest.mark.not_implemented_datetime_timezone
def test_label_bit_not_set_in_template(tmpdir, merge_files_oneLR, assert_log):
    path = os.path.join(str(tmpdir), 'label-bit-not-set-in-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/label-bit-not-set.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['NEW_ATTRIBUTE']
        dt = datetime(2033, 4, 19, 20, 39, 58, 103000)
        assert attr.value == [dt]
        assert_log("Label not set in template")


def test_set_type_bit_not_set_in_set(tmpdir, merge_files_oneLR, assert_log):
    path = os.path.join(str(tmpdir), 'set-type-not-set.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/no-type-flag.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['DEFAULT_ATTRIBUTE'].value
        assert_log("Problem:      SET:type not set\n"
                   "Where:        object set of type 'VERY_MUCH_TESTY_SET' "
                   "named ''")


def test_set_name_bit_set_name_not_present(tmpdir, merge_files_oneLR, assert_log):
    # based on frequent situation for FILE-HEADER sets
    path = os.path.join(str(tmpdir), 'name-bit-set-name-not-present.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/name-bit-set-no-name.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            _ = f.object('FILE-HEADER', 'N', 2, 0)
        err = "object set of type 'FILE-HEADER' named 'SEQUENCE-NUMBER4ID"
        assert err in str(excinfo.value)


def test_object_name_bit_not_set_in_object(tmpdir, merge_files_oneLR,
                                           assert_log):
    path = os.path.join(str(tmpdir), 'no-object-name-bit.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/no-name-bit.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['DEFAULT_ATTRIBUTE'].value
        _ = obj['DEFAULT_ATTRIBUTE']
        assert_log("Problem:      OBJECT:name was not set\n"
                   "Where:        T.VERY_MUCH_TESTY_SET-I.OBJECT-O.1-C.1")


@pytest.mark.future_test_attributes
def test_novalue_less_count(tmpdir, merge_files_oneLR, assert_log):
    path = os.path.join(str(tmpdir), 'novalue-less-count.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count1-novalue.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 1
        #assert attr.reprc == dlisio.core.reprc.fdoubl
        assert attr.units == 'default attr units'
        assert attr.value == [-0.75]

        _ = obj['DEFAULT_ATTRIBUTE']
        assert_log("< template count")


def test_novalue_more_count(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'novalue-more-count.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count9-novalue.dlis.part',
        'data/chap3/object/object2.dlis.part',
        'data/chap3/objattr/all-set.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        with pytest.raises(RuntimeError) as excinfo:
            _ = obj['DEFAULT_ATTRIBUTE']
        assert "> template count" in str(excinfo.value)

        obj2 = f.object('VERY_MUCH_TESTY_SET', 'OBJECT2', 1, 1)
        attr = obj2['DEFAULT_ATTRIBUTE']
        assert attr == [1, 2, 3, 4]

def test_set_redundant(tmpdir, merge_files_oneLR, assert_info):
    path = os.path.join(str(tmpdir), 'redundant-set.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/redundant.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/all-set.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        _ = f.object('REDUNDANT', 'OBJECT', 1, 1)
        assert_info("Redundant sets are not supported")

def test_set_replacement(tmpdir, merge_files_oneLR, assert_log):
    path = os.path.join(str(tmpdir), 'replacement-set.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/replacement.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/all-set.dlis.part'
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *tail):
        _ = f.object('REPLACEMENT', 'OBJECT', 1, 1)
        assert_log("Replacement sets are not supported")


# these tests first of all verify findfdata method, which now belongs
# both to physical and logical layers of processing.
# Hence there is no good place for it

def test_findfdata_VR_aligned():
    with dlis.load('data/chap3/implicit/fdata-vr-aligned.dlis') as (f, *_):
        assert len(f.fdata_index) == 1
        assert f.fdata_index['T.FRAME-I.DLIS-FRAME-O.3-C.1'] == [0]

def test_findfdata_VR_aligned_padding():
    path = 'data/chap3/implicit/fdata-vr-aligned-padding.dlis'
    with dlis.load(path) as (f, *_):
        assert len(f.fdata_index) == 1
        assert f.fdata_index['T.FRAME-I.DLIS-FRAME-O.3-C.1'] == [0]

def test_findfdata_many_in_same_VR():
    with dlis.load('data/chap3/implicit/fdata-many-in-same-vr.dlis') as (f, *_):
        assert len(f.fdata_index) == 3
        assert f.fdata_index['T.FRAME-I.DLIS-FRAME-O.3-C.1'] == [0, 48]

        fingerprint = 'T.FRAME-I.-O.3-C.1'
        assert f.fdata_index[fingerprint] == [144]

        ident = '3'*255
        fingerprint = 'T.FRAME-I.'+ident+'-O.1073741823-C.255'
        assert f.fdata_index[fingerprint] == [192]

def test_findfdata_non_0_non_1_type():
    path = 'data/chap3/implicit/fdata-non-0-non-1-type.dlis'
    with dlis.load(path) as (f, *_):
        assert len(f.fdata_index) == 0

def test_findfdata_VR_disaligned():
    with dlis.load('data/chap3/implicit/fdata-vr-disaligned.dlis') as (f, *_):
        assert len(f.fdata_index) == 1
        assert f.fdata_index['T.FRAME-I.IFLR-O.35-C.1'] == [0]

def test_findfdata_VR_disaligned_after_obname():
    path = 'data/chap3/implicit/fdata-vr-disaligned-checksum.dlis'
    with dlis.load(path) as (f, *_):
        assert len(f.fdata_index) == 1
        name = 'FRAME-OBNAME-INTERRUPTED-BY-VR!'
        assert f.fdata_index['T.FRAME-I.'+name+'-O.19-C.1'] == [0]

def test_findfdata_VR_disaligned_in_obname():
    path = 'data/chap3/implicit/fdata-vr-disaligned-in-obname.dlis'
    with dlis.load(path) as (f, *_):
        assert len(f.fdata_index) == 1
        name = 'FRAME-OBNAME-INTERRUPTED-BY-VR'
        assert f.fdata_index['T.FRAME-I.'+name+'-O.19-C.1'] == [0]

def test_findfdata_VR_disaligned_in_obname_trailing_length_in_lrs():
    path = 'data/chap3/implicit/fdata-vr-obname-trailing.dlis'
    with dlis.load(path) as (f, *_):
        assert len(f.fdata_index) == 1
        name = 'FRAME-OBNAME-INTERRUPTED-BY-VR'
        assert f.fdata_index['T.FRAME-I.'+name+'-O.19-C.1'] == [0]

def test_findfdata_encrypted():
    with dlis.load('data/chap3/implicit/fdata-encrypted.dlis') as (f, *_):
        assert len(f.fdata_index) == 0

def test_findfdata_bad_obname():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap3/implicit/fdata-broken-obname.dlis')

    # Obname is truncated by LRS-length, which in itself is fine as long as it
    # continues on the next LRS. However, in this case there are no new LRS.
    msg = 'fdata record corrupted, error on reading obname'
    assert msg in str(excinfo.value)

def test_unexpected_attribute_in_set(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'unexpected-attribute.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/no-set-start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with pytest.raises(RuntimeError) as excinfo:
        dlis.load(path)
    assert "expected SET" in str(excinfo.value)

def test_unexpected_set_in_object(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'unexpected-set-in-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/set/second-set.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            f.load()
    assert "expected ATTRIB" in str(excinfo.value)


def test_unexpected_set_in_template(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'unexpected-set-in-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/set/second-set.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            f.load()
    assert "expected ATTRIB" in str(excinfo.value)



def test_unexpected_attribute_instead_of_object(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'unexpected-attr-instead-of-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/empty.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            f.load()
    assert "expected OBJECT" in str(excinfo.value)




def test_cut_before_template(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'cut-before-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            f.load()
    assert "unexpected end-of-record" in str(excinfo.value)


def test_cut_before_object(tmpdir, merge_files_oneLR, assert_debug):
    # otherwise known as "set with no objects" test
    path = os.path.join(str(tmpdir), 'cut-before-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
    ]
    merge_files_oneLR(path, content)
    with dlis.load(path) as (f,):
        objects = f.find('.*', '.*')
        assert len(objects) == 0
        assert_debug("Set contains no objects")


@pytest.mark.skip(reason="result inconsistent")
def test_cut_middle_object(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'cut-middle-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/cut_middle_type.dlis.part',
    ]
    merge_files_oneLR(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlis.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)


@pytest.mark.skip(reason="result inconsistent")
def test_cut_middle_object_attribute(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'cut-middle-object-attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/cut_middle_value.dlis.part',
    ]
    merge_files_oneLR(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlis.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)


@pytest.mark.skip(reason="result inconsistent")
def test_cut_middle_template_attribute(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'cut-middle-template-attribut.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/cut_after_attribute.dlis.part',
    ]
    merge_files_oneLR(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlis.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)


