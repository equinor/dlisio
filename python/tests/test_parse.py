import pytest
from datetime import datetime
import os

import dlisio
from dlisio.core import reprc

@pytest.fixture
def merge(merge_files_oneLR):
    def merge(path, content):
        merge_files_oneLR(path, content)
    return merge

@pytest.mark.future_test_attributes
def test_invariant_attribute(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'invariant_attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['INVARIANT_ATTRIBUTE']
        #assert attr.count == 3
        #assert attr.reprc == dlisio.core.reprc.status
        #assert attr.units == 'invariant units'
        assert attr == [False, False, True]


@pytest.mark.future_warning_invariant_attribute
def test_invariant_attribute_in_object(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'invariant-attribute-in-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/invariant.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        assert attr == [8.0]


@pytest.mark.future_test_attributes
def test_default_attribute(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'default_attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/empty.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 2
        #assert attr.reprc == dlisio.core.reprc.fdoubl
        #assert attr.units == 'default attr units'
        assert attr == [-0.75, 10.0]


def test_default_attribute_cut(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'default_attribute_cut.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['INVARIANT_ATTRIBUTE']
        assert obj.attic['DEFAULT_ATTRIBUTE']


def test_attribute_absent(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'attribute_absent.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/absent.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['INVARIANT_ATTRIBUTE']
        with pytest.raises(KeyError):
            _ = obj.attic['DEFAULT_ATTRIBUTE']


@pytest.mark.future_warning_absent_attr_in_template
def test_absent_attribute_in_template(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'absent-attribute-in-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/absent.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['DEFAULT_ATTRIBUTE']


@pytest.mark.future_test_attributes
def test_global_default_attribute(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'global-default-attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/global-default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/empty.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['GLOBAL_DEFAULT_ATTRIBUTE']
        #assert attr.count == 1
        #assert attr.reprc == dlisio.core.reprc.ident
        #assert attr.units == ''
        assert attr == ['']


@pytest.mark.future_test_attributes
def test_all_attribute_bits(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'global-all-attribute-bits.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/all-set.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 4
        #assert attr.reprc == dlisio.core.reprc.ushort
        #assert attr.units == 'overwritten units'
        assert attr == [1, 2, 3, 4]


@pytest.mark.future_warning_label_bit_set_in_object_attr
def test_label_bit_set_in_attribute(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'label_bit_set_in_attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/label-bit-set.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['DEFAULT_ATTRIBUTE']


@pytest.mark.future_warning_label_bit_not_set_in_template
@pytest.mark.not_implemented_datetime_timezone
def test_label_bit_not_set_in_template(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'label-bit-not-set-in-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/label-bit-not-set.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['NEW_ATTRIBUTE']
        dt = datetime(2033, 4, 19, 20, 39, 58, 103000)
        assert attr == [dt]


@pytest.mark.future_test_attributes
def test_count0_novalue(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'count0-novalue.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count0-novalue-bit.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 0
        assert attr == None


@pytest.mark.future_test_attributes
def test_count0_value_bit(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'count0-value-bit.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count0-value-bit.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 0
        assert attr == None


@pytest.mark.future_test_attributes
def test_count0_different_repcode(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'count0-different-repcode.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count0-different-repcode.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 0
        #assert attr.reprc == dlisio.core.reprc.units
        assert attr == None


def test_different_repcode_no_value(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'different-repcode-no-value.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/csingle-novalue.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            # Load all objects
            f.load()
    assert "value is not explicitly set" in str(excinfo.value)


def test_same_as_default_no_value(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'same-as-default-but-no-value.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/repeat-default-novalue.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        assert attr == [-0.75, 10.0]


@pytest.mark.future_test_attributes
def test_novalue_less_count(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'novalue-less-count.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count1-novalue.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 1
        #assert attr.reprc == dlisio.core.reprc.fdoubl
        #assert attr.units == 'default attr units'
        assert attr == [-0.75]


@pytest.mark.not_implemented
def test_novalue_more_count(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'novalue-more-count.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/count9-novalue.dlis.part'
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *_):
        with pytest.raises(NotImplementedError):
            f.load()

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


def test_repcode(tmpdir, merge, filename_p, attr_n, attr_reprc, attr_v):
    path = os.path.join(str(tmpdir), filename_p + '.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/repcode/' + filename_p + '.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic[attr_n]
        #assert attr.reprc == attr_reprc
        assert attr == [attr_v]


def test_invalid_repcode_in_template_value(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'invalid-repcode.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invalid-repcode-value.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/all-set.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            f.load()
    assert "unknown representation code" in str(excinfo.value)


def test_invalid_repcode_in_template_no_value(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'invalid-repcode-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invalid-repcode-no-value.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/all-set.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *_):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        attr = obj.attic['INVALID']
        assert attr == [1, 2, 3, 4]


def test_invalid_repcode_in_objects(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'invalid-repcode-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/reprcode-invalid.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *_):
        with pytest.raises(RuntimeError) as excinfo:
            f.load()
    assert "unknown representation code" in str(excinfo.value)


def test_inccorect_set_header(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'incorrect-set-header.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/no-set-start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with pytest.raises(ValueError) as excinfo:
        dlisio.load(path)
    assert "expected SET" in str(excinfo.value)


@pytest.mark.future_warning_set_type_bit_not_set
def test_set_type_not_set(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'incorrect_set_header.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/no-type-flag.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['DEFAULT_ATTRIBUTE']


@pytest.mark.future_warning_object_name_bit_not_set
def test_no_object_name_bit(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'no-object-name-bit.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/no-name-bit.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *tail):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert obj.attic['DEFAULT_ATTRIBUTE']


def test_unexpected_attribute_instead_of_object(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'unexpected-attr-instead-of-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/empty.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *_):
        with pytest.raises(ValueError) as excinfo:
            f.load()
    assert "expected OBJECT" in str(excinfo.value)


def test_no_template(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'no-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f,):
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        assert len(obj.attic) == 0


def test_unexpected_set_in_object(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'unexpected-set-in-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/set/second-set.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *_):
        with pytest.raises(ValueError) as excinfo:
            f.load()
    assert "expected ATTRIB" in str(excinfo.value)


def test_unexpected_set_in_template(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'unexpected-set-in-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/set/second-set.dlis.part',
        'data/chap3/template/invariant.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *_):
        with pytest.raises(ValueError) as excinfo:
            f.load()
    assert "expected ATTRIB" in str(excinfo.value)


def test_cut_before_template(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'cut-before-template.dlis')
    content = [
        'data/chap3/start.dlis.part',
    ]
    merge(path, content)

    with dlisio.load(path) as (f, *_):
        with pytest.raises(IndexError) as excinfo:
            f.load()
    assert "unexpected end-of-record" in str(excinfo.value)


def test_cut_before_object(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'cut-before-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
    ]
    merge(path, content)
    with dlisio.load(path) as (f,):
        objects = {}
        for v in f.indexedobjects.values():
            objects.update(v)
        assert len(objects) == 0


@pytest.mark.skip(reason="result inconsistent")
def test_cut_middle_object(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'cut-middle-object.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/cut_middle_type.dlis.part',
    ]
    merge(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlisio.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)


@pytest.mark.skip(reason="result inconsistent")
def test_cut_middle_object_attribute(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'cut-middle-object-attribute.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/cut_middle_value.dlis.part',
    ]
    merge(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlisio.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)


@pytest.mark.skip(reason="result inconsistent")
def test_cut_middle_template_attribute(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'cut-middle-template-attribut.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/cut_after_attribute.dlis.part',
    ]
    merge(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlisio.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)

@pytest.mark.future_test_attributes
def test_broken_utf8_value(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'broken_utf8_value.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/broken-utf8-value.dlis.part',
    ]
    merge(path, content)

    prev_encodings = dlisio.get_encodings()
    dlisio.set_encodings([])
    with pytest.warns(UnicodeWarning):
        with dlisio.load(path) as (f, *_):
            f.load()
    try:
        dlisio.set_encodings(['koi8_r'])
        with dlisio.load(path) as (f, *_):
            obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
            assert obj.attic['DEFAULT_ATTRIBUTE'] == ['ВАЖНЫЙ-ПАРАМЕТР']
            assert obj.stash['DEFAULT_ATTRIBUTE'] == ['ВАЖНЫЙ-ПАРАМЕТР']
            #assert units == "2 локтя на долю"
    finally:
        dlisio.set_encodings(prev_encodings)

@pytest.mark.skip(reason="not warn on warning and sigabrt on second")
def test_broken_utf8_obname_value(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'broken_utf8_obname_value.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/broken-utf8-obname-value.dlis.part',
    ]
    merge(path, content)
    with pytest.warns(UnicodeWarning):
        with dlisio.load(path):
            pass
    prev_encodings = dlisio.get_encodings()
    try:
        dlisio.set_encodings(['koi8_r'])
        with dlisio.load(path) as (f, *_):
            obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
            obname = (2, 2, 'КОТ')
            assert obj.attic['DEFAULT_ATTRIBUTE'] == [obname]
    finally:
        dlisio.set_encodings(prev_encodings)

@pytest.mark.xfail(strict=True, reason="fingerprint error on no encoding")
def test_broken_utf8_object_name(tmpdir, merge):
    #some actual files have obname which fails with utf-8 codec
    path = os.path.join(str(tmpdir), 'broken_utf8_object_name.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/broken-utf8-object.dlis.part',
    ]
    merge(path, content)
    with pytest.warns(UnicodeWarning):
        with dlisio.load(path):
            pass
    prev_encodings = dlisio.get_encodings()
    try:
        dlisio.set_encodings(['koi8_r'])
        with dlisio.load(path) as (f, *_):
            _ = f.object('VERY_MUCH_TESTY_SET', 'КАДР', 12, 4)
    finally:
        dlisio.set_encodings(prev_encodings)

@pytest.mark.xfail(strict=True, reason="could not allocate string object")
def test_broken_utf8_label(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'broken_utf8_label.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/broken-utf8-label.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)
    with pytest.warns(UnicodeWarning):
        with dlisio.load(path):
            pass
    prev_encodings = dlisio.get_encodings()
    try:
        dlisio.set_encodings(['koi8_r'])
        with dlisio.load(path) as (f, *_):
            obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
            assert obj.attic['ДОХЛЫЙ-ПАРАМЕТР'] == ['Have a nice day!']
    finally:
        dlisio.set_encodings(prev_encodings)

@pytest.mark.xfail(strict=True, reason="fingerprint error on no encoding")
@pytest.mark.future_test_set_names
def test_broken_utf8_set(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'broken_utf8_set.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/broken-utf8-set.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge(path, content)
    with pytest.warns(UnicodeWarning):
        with dlisio.load(path) as (f, *_):
            f.load()
    prev_encodings = dlisio.get_encodings()
    try:
        dlisio.set_encodings(['koi8_r'])
        with dlisio.load(path) as (f, *_):
            _ = f.object('СЕТ_КИРИЛЛИЦЕЙ', 'OBJECT', 1, 1)
            #assert set_name == 'МЕНЯ.ЗОВУТ.СЕТ'
    finally:
        dlisio.set_encodings(prev_encodings)

def test_fdata_bad_ident(tmpdir, merge):
    path = os.path.join(str(tmpdir), 'fdata_bad_ident.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/implicit/fdata-bad-ident.dlis.part',
    ]
    merge(path, content)
    with pytest.raises(RuntimeError) as excinfo:
        dlisio.load(path)

    assert "fdata obname" in str(excinfo.value)
