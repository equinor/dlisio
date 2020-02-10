"""
Testing BasicObject class
"""
import pytest
import dlisio
from dlisio.plumbing import *


def test_getitem(f):
    obj = f.object('FRAME', 'FRAME1')

    assert obj['INDEX-TYPE'] == 'BOREHOLE-DEPTH'

def test_getitem_defaultvalue(f):
    obj = f.object('FRAME', 'FRAME2')

    # Attribute index_type is absent (from attic), but we stil expect to get a
    # default value
    assert obj['INDEX-TYPE'] is None

def test_getitem_unexpected_attr(f):
    obj = f.object('FRAME', 'FRAME2')

    try:
        obj.attic['NEW-ATTR'] = [1]

        # Attributes unknown to dlisio, such as 'NEW-ATTR' should be reachable
        # through __getitem__
        assert obj['NEW-ATTR'] == [1]

        # Should also be in stash
        assert obj.stash['NEW-ATTR'] == [1]
    finally:
        del obj.attic['NEW-ATTR']

def test_getitem_noattribute(f):
    obj = f.object('FRAME', 'FRAME2')

    # getitem should raise an KeyError if key not in obj.attic or
    # obj.attributes

    with pytest.raises(KeyError):
        _ = obj['DUMMY']

def test_lookup():
    other = Channel()
    other.name = 'channel'
    other.origin = 10
    other.copynumber = 2

    lf = dlisio.dlis(None, [], [], [])
    lf.indexedobjects['CHANNEL'] = {other.fingerprint : other}

    ch = Channel()
    ch.logicalfile = lf

    value = dlisio.core.obname(10, 2, 'channel')
    res = lookup(ch, linkage.obname('CHANNEL'), value)

    assert res == other

def test_lookup_value_not_a_ref(assert_log):
    res = lookup(None, linkage.objref, 0)

    assert res is None
    assert_log('Unable to create object-reference')

def test_lookup_value_should_be_objref(assert_log):
    value = dlisio.core.obname(10, 2, 'channel')
    res = lookup(None, linkage.objref, value)

    assert res is None
    assert_log('Unable to create object-reference')

def test_lookup_no_logicalfile(assert_log):
    value = dlisio.core.obname(10, 2, 'channel')
    ch = Channel() #channel without reference to a logical file

    res = lookup(ch, linkage.obname('CHANNEL'), value)

    assert res is None
    assert_log('has no logical file')

def test_lookup_no_such_object(assert_log):
    value = dlisio.core.obname(10, 2, 'channel')
    ch = Channel()
    ch.logicalfile = dlisio.dlis(None, [], [], [])
    res = lookup(ch, linkage.obname('CHANNEL'), value)

    assert res is None
    assert_log('not in logical file')

@pytest.mark.xfail(strict=True, reason="attempt to link empty fingerprint")
def test_link_empty_object(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('load').join('empty-attribute.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/origin.dlis.part',
        'data/chap4-7/eflr/channel-empty-source.dlis.part',
    ]
    merge_files_manyLR(fpath, content)

    with dlisio.load(fpath) as (f, *_):
        c1 = f.object('CHANNEL', 'EMPTY_SOURCE_1', 10, 0)
        try:
            _ = c1.stash["SOURCE"]
        except KeyError:
            pass
        c2 = f.object('CHANNEL', 'EMPTY_SOURCE_2', 10, 0)
        assert c2.source == (0, 0, "", "")


def test_parse_attribute_scalar():
    res = parsevalue([1], scalar)
    assert res == 1

def test_parse_attribute_scalar_unexpected_element(assert_log):
    res = parsevalue([1, 2], scalar)
    assert res == 1
    assert_log('Expected only 1 value')

def test_parse_attribute_boolean():
    res = parsevalue([0], boolean)
    assert res == False

def test_parse_attribute_boolean_unexpected_element(assert_log):
    res = parsevalue([1, 2], boolean)
    assert res == True
    assert_log('Expected only 1 value')

def test_parse_attribute_vector():
    res = parsevalue([1], vector)
    assert res == [1]

def test_parse_attribute_reverse_unexpected_element(assert_log):
    res = parsevalue([1, 2], reverse)
    assert res == [2, 1]

def test_valuetype_mismatch(assert_log):
    tool = dlisio.plumbing.tool.Tool()
    tool.attic = {
        'DESCRIPTION' : ["Description", "Unexpected description"],
        'STATUS'      : ["Yes", 0],
    }

    assert tool.description == "Description"
    assert tool.status      == True
    assert_log('Expected only 1 value')

def test_unexpected_attributes(f):
    c = f.object('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)

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
