"""
Testing BasicObject class
"""
import pytest
import dlisio
from dlisio.dlis.utils import *


def test_getitem(f):
    obj = f.object('FRAME', 'FRAME1')

    assert obj['INDEX-TYPE'] == 'BOREHOLE-DEPTH'

def test_getitem_defaultvalue(f):
    obj = f.object('FRAME', 'FRAME2')

    # Attribute index_type is absent (from attic), but we stil expect to get a
    # default value
    assert obj['INDEX-TYPE'] is None

def test_getitem_unexpected_attr(f):
    obj = f.object('TOOL', 'TOOL-BAD')
    # Attributes unknown to dlisio, such as 'MY_PARAM' should be reachable
    # through __getitem__
    assert obj["MY_PARAM"] == ["wrong", "W"]

    # Should also be in stash
    assert obj.stash["MY_PARAM"] == ["wrong", "W"]

def test_getitem_noattribute(f):
    obj = f.object('FRAME', 'FRAME2')

    # getitem should raise an KeyError if key not in obj.attic or
    # obj.attributes

    with pytest.raises(KeyError):
        _ = obj['DUMMY']

def test_lookup(f):
    value = dlisio.core.obname(10, 0, 'CHANN2')
    res = lookup(f, linkage.obname('CHANNEL'), value)

    assert res.long_name == "CHANN2-LONG-NAME"

def test_lookup_value_not_a_ref(f, assert_log):
    res = lookup(f, linkage.objref, 0)

    assert res is None
    assert_log('Unable to create object-reference')

def test_lookup_value_should_be_objref(f, assert_log):
    value = dlisio.core.obname(10, 2, 'channel')
    res = lookup(f, linkage.objref, value)

    assert res is None
    assert_log('Unable to create object-reference')

def test_lookup_no_such_object(f, assert_log):
    value = dlisio.core.obname(10, 2, 'channel')
    res = lookup(f, linkage.obname('CHANNEL'), value)

    assert res is None
    assert_log('Unable to find linked object')

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

def test_incorrect_object(f, assert_log):
    t = f.object('TOOL', 'TOOL-BAD', 10, 0)

    # two descriptions provided
    assert t.description == "Description"
    assert_log('Expected only 1 value')

    # according to spec it must be ascii
    assert t.trademark_name == 21

    # correct attribute
    assert t.generic_name == "Some important tool"

    #spaces are stripped for stash also
    assert t["MY_PARAM"] == ["wrong", "W"]

    # no linkage is performed for stash even for known objects
    assert t["LINKS_TO_PARAMETERS"] == [(10, 0, "PARAM2"),
                                        (10, 0, "PARAMU")]
    assert t.stash["LINK_TO_UNKNOWN_OBJECT"] == [("UNKNOWN_SET",
                                                 (10, 0, "OBJ1"))]

    # wrong type
    assert t.parts == ["SOME PART"]

    # There were two non-boolean statuses
    assert t.status == True

    # attribute count is 0
    assert t.channels == []

    # attribute missing
    assert t.parameters == []
