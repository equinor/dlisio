import pytest
from datetime import datetime
import os

import dlisio


@pytest.fixture
def create_file():
    def create_file(fpath, flist):
        b = bytearray()
        for file in flist:
            with open(file, 'rb') as source:
                b += bytearray(source.read())

        with open(fpath, "wb") as dest:
            update_envelope_VRL_and_LRSL(b)
            dest.write(b)

    return create_file

def update_envelope_VRL_and_LRSL(b):
    lrsl = len(b) - 104
    padbytes_count = max(0, 20 - lrsl)

    if (len(b) + padbytes_count) % 2 :
        padbytes_count += 1
    else:
        padbytes_count += 2

    padbytes = bytearray([0x01] * (padbytes_count - 1))
    padbytes.extend([padbytes_count])

    b.extend(padbytes)

    if(len(b) > 255 + 80):
        msg = ("update the envelope method. "
               "current implementation assumes VRL <=255 bytes")
        raise RuntimeError(msg)

    b[81] = len(b) - 80 #change VR length
    b[105] = len(b) - 104 #change LRS length

@pytest.mark.future_test_attributes
def test_invariant_attribute(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'invariant_attribute.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/invariant.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['INVARIANT_ATTRIBUTE']
        #assert attr.count == 3
        #assert attr.reprc == dlisio.core.reprc.status
        #assert attr.units == 'invariant units'
        assert attr == [False, False, True]


@pytest.mark.future_warning_invariant_attribute
def test_invariant_attribute_in_object(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'invariant_attribute_in_object.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/invariant.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        assert attr == [8.0]


@pytest.mark.future_test_attributes
def test_default_attribute(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'default_attribute.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/empty.dlis_part'
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 2
        #assert attr.reprc == dlisio.core.reprc.fdoubl
        #assert attr.units == 'default attr units'
        assert attr == [-0.75, 10.0]


def test_default_attribute_cut(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'default_attribute_cut.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/invariant.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        assert obj.attic['INVARIANT_ATTRIBUTE']
        assert obj.attic['DEFAULT_ATTRIBUTE']


def test_attribute_absent(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'attribute_absent.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/invariant.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/absent.dlis_part'
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        assert obj.attic['INVARIANT_ATTRIBUTE']
        with pytest.raises(KeyError):
            obj.attic['DEFAULT_ATTRIBUTE']


@pytest.mark.future_warning_absent_attr_in_template
def test_absent_attribute_in_template(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'absent_attribute_in_template.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/absent.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        assert obj.attic['DEFAULT_ATTRIBUTE']


@pytest.mark.future_test_attributes
def test_global_default_attribute(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'global_default_attribute.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/global_default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/empty.dlis_part'
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['GLOBAL_DEFAULT_ATTRIBUTE']
        #assert attr.count == 1
        #assert attr.reprc == dlisio.core.reprc.ident
        #assert attr.units == ''
        assert attr == ['']


@pytest.mark.future_test_attributes
def test_all_attribute_bits(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'global_all_attribute_bits.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/all_set.dlis_part'
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 4
        #assert attr.reprc == dlisio.core.reprc.ushort
        #assert attr.units == 'overwritten units'
        assert attr == [1, 2, 3, 4]


@pytest.mark.future_warning_label_bit_set_in_object_attr
def test_label_bit_set_in_attribute(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'label_bit_set_in_attribute.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/label_bit_set.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        assert obj.attic['DEFAULT_ATTRIBUTE']


@pytest.mark.future_warning_label_bit_not_set_in_template
@pytest.mark.not_implemented_datetime_timezone
def test_label_bit_not_set_in_template(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'label_bit_not_set_in_template.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/label_bit_not_set.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['NEW_ATTRIBUTE']
        dt = datetime(2033, 4, 19, 20, 39, 58, 103)
        assert attr == [dt]


@pytest.mark.future_test_attributes
def test_count0_novalue(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'count0_novalue.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/count0_novalue_bit.dlis_part'
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 0
        assert attr == None


@pytest.mark.future_test_attributes
def test_count0_value_bit(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'count0_value_bit.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/count0_value_bit.dlis_part'
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 0
        assert attr == None


@pytest.mark.future_test_attributes
def test_count0_different_repcode(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'count0_different_repcode.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/count0_different_repcode.dlis_part'
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 0
        #assert attr.reprc == dlisio.core.reprc.units
        assert attr == None


def test_different_repcode_no_value(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'different_repcode_no_value.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/csingle_novalue.dlis_part'
    ]
    create_file(path, content)

    with pytest.raises(RuntimeError) as excinfo:
        dlisio.load(path)
    assert "value is not explicitly set" in str(excinfo.value)


@pytest.mark.future_test_attributes
def test_novalue_less_count(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'novalue_less_count.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/count1_novalue.dlis_part'
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic['DEFAULT_ATTRIBUTE']
        #assert attr.count == 1
        #assert attr.reprc == dlisio.core.reprc.fdoubl
        #assert attr.units == 'default attr units'
        assert attr == [-0.75]


@pytest.mark.not_implemented
def test_novalue_more_count(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'novalue_more_count.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/count9_novalue.dlis_part'
    ]
    create_file(path, content)

    with pytest.raises(NotImplementedError):
        dlisio.load(path)


@pytest.mark.future_test_attributes
@pytest.mark.not_implemented_datetime_timezone
@pytest.mark.parametrize("filename_p,attr_n,attr_reprc,attr_v", [
    ("01_fshort", 'FSHORT', dlisio.core.reprc.fshort, -1),
    ("02_fsingl", 'FSINGL', dlisio.core.reprc.fsingl, 5.5),
    ("03_fsing1", 'FSING1', dlisio.core.reprc.fsing1, (-2, 2)),
    ("04_fsing2", 'FSING2', dlisio.core.reprc.fsing2, (117, -13.25, 32444)),
    ("05_isingl", 'ISINGL', dlisio.core.reprc.isingl, -12),
    ("06_vsingl", 'VSINGL', dlisio.core.reprc.vsingl, 0.125),
    ("07_fdoubl", 'FDOUBL', dlisio.core.reprc.fdoubl, 900000000000000.5),
    ("08_fdoub1", 'FDOUB1', dlisio.core.reprc.fdoub1, (-13.5, -27670)),
    ("09_fdoub2", 'FDOUB2', dlisio.core.reprc.fdoub2,
        (6728332223, -45.75, -0.0625)),
    ("10_csingl", 'CSINGL', dlisio.core.reprc.csingl, complex(93, -14)),
    ("11_cdoubl", 'CDOUBL', dlisio.core.reprc.cdoubl, complex(125533556, -4.75)),
    ("12_sshort", 'SSHORT', dlisio.core.reprc.sshort, 89),
    ("13_snorm",  'SNORM',  dlisio.core.reprc.snorm,  -153),
    ("14_slong",  'SLONG',  dlisio.core.reprc.slong,  2147483647),
    ("15_ushort", 'USHORT', dlisio.core.reprc.ushort, 6),
    ("16_unorm",  'UNORM',  dlisio.core.reprc.unorm,  32921),
    ("17_ulong",  'ULONG',  dlisio.core.reprc.ulong,  1),
    ("18_uvari",  'UVARI',  dlisio.core.reprc.uvari,  257),
    ("19_ident",  'IDENT',  dlisio.core.reprc.ident,  "VALUE"),
    ("20_ascii",  'ASCII',  dlisio.core.reprc.ascii,  "ASCII VALUE"),
    ("21_dtime",  'DTIME',  dlisio.core.reprc.dtime,
        datetime(1971, 3, 21, 18, 4, 14, 386)),
    ("22_origin", 'ORIGIN', dlisio.core.reprc.origin, 16777217),
    ("23_obname", 'OBNAME', dlisio.core.reprc.obname,
        dlisio.core.obname(18, 5, "OBNAME_I")),
    ("24_objref", 'OBJREF', dlisio.core.reprc.objref,
        dlisio.core.objref("OBJREF_I",
            dlisio.core.obname(25, 3, "OBJREF_OBNAME"))),
    ("25_attref", 'ATTREF', dlisio.core.reprc.attref,
        dlisio.core.attref("FIRST_INDENT",
            dlisio.core.obname(3, 2, "ATTREF_OBNAME"), "SECOND_INDENT")),
    ("26_status", 'STATUS', dlisio.core.reprc.status, True),
    ("27_units",  'UNITS',  dlisio.core.reprc.units,  "unit"),
])
def test_repcode(tmpdir, create_file, filename_p, attr_n, attr_reprc, attr_v):
    path = os.path.join(str(tmpdir), filename_p+'.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/repcode/'+filename_p+'.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        attr = obj.attic[attr_n]
        #assert attr.reprc == attr_reprc
        assert attr == [attr_v]


def test_invalid_repcode(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'invalid_repcode.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/invalid_repcod.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)

    with pytest.raises(ValueError) as excinfo:
        dlisio.load(path)
    assert "invalid representation code" in str(excinfo.value)


def test_inccorect_set_header(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'incorrect_set_header.dlis')
    content = [
        'data/parse/sul.dlis_part',
        'data/parse/set/no_set_start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)

    with pytest.raises(ValueError) as excinfo:
        dlisio.load(path)
    assert "expected SET" in str(excinfo.value)


@pytest.mark.future_warning_set_type_bit_not_set
def test_set_type_not_set(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'incorrect_set_header.dlis')
    content = [
        'data/parse/sul.dlis_part',
        'data/parse/set/no_type_flag.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        assert obj.attic['DEFAULT_ATTRIBUTE']


@pytest.mark.future_warning_object_name_bit_not_set
def test_no_object_name_bit(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'no_object_name_bit.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/no_name_bit.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        assert obj.attic['DEFAULT_ATTRIBUTE']


def test_unexpected_attribute_instead_of_object(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'unexpected_attr_instead_of_object.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/invariant.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/empty.dlis_part',
    ]
    create_file(path, content)
    with pytest.raises(ValueError) as excinfo:
        dlisio.load(path)
    assert "expected OBJECT" in str(excinfo.value)


def test_no_template(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'no_template.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)

    with dlisio.load(path) as f:
        key = dlisio.core.fingerprint('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obj = f.objects[key]
        assert len(obj.attic) == 0


def test_unexpected_set_in_object(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'unexpected_set_in_object.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/set/second_set.dlis_part',
        'data/parse/template/invariant.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)
    with pytest.raises(ValueError) as excinfo:
        dlisio.load(path)
    assert "expected ATTRIB" in str(excinfo.value)


def test_unexpected_set_in_template(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'unexpected_set_in_template.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/set/second_set.dlis_part',
        'data/parse/template/invariant.dlis_part',
        'data/parse/object/object.dlis_part',
    ]
    create_file(path, content)
    with pytest.raises(ValueError) as excinfo:
        dlisio.load(path)
    assert "expected ATTRIB" in str(excinfo.value)


def test_cut_before_template(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'cut_before_template.dlis')
    content = [
        'data/parse/start.dlis_part',
    ]
    create_file(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlisio.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)


def test_cut_before_object(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'cut_before_object.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
    ]
    create_file(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlisio.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)


@pytest.mark.skip(reason="result inconsistent")
def test_cut_middle_object(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'cut_middle_object.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/cut_middle_type.dlis_part',
    ]
    create_file(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlisio.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)


@pytest.mark.skip(reason="result inconsistent")
def test_cut_middle_object_attribute(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'cut_middle_object_attribute.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/default.dlis_part',
        'data/parse/object/object.dlis_part',
        'data/parse/objattr/cut_middle_value.dlis_part',
    ]
    create_file(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlisio.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)


@pytest.mark.skip(reason="result inconsistent")
def test_cut_middle_template_attribute(tmpdir, create_file):
    path = os.path.join(str(tmpdir), 'cut_middle_template_attribut.dlis')
    content = [
        'data/parse/start.dlis_part',
        'data/parse/template/cut_after_attribute.dlis_part',
    ]
    create_file(path, content)
    with pytest.raises(IndexError) as excinfo:
        dlisio.load(path)
    assert "unexpected end-of-record" in str(excinfo.value)

