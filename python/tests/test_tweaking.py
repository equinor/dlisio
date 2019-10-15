import pytest

from dlisio.plumbing import valuetypes, linkage
from dlisio.plumbing.coefficient import Coefficient

import dlisio

def test_dynamic_class(f):
    class ActuallyKnown(dlisio.plumbing.basicobject.BasicObject):
        attributes = {
            "SOME_LIST"   : valuetypes.vector('list'),
            "SOME_VALUE"  : valuetypes.scalar('value'),
            "SOME_STATUS" : valuetypes.boolean('status'),
        }

        def __init__(self, obj = None, name = None, lf = None):
            super().__init__(obj, name = name, type = "UNKNOWN_SET", lf = lf)
            self.list = []
            self.value = None
            self.status = None

    unknown = f.object('UNKNOWN_SET', 'OBJ1', 10, 0)
    with pytest.raises(AttributeError):
        assert unknown.value == "VAL1"

    try:
        f.types['UNKNOWN_SET'] = ActuallyKnown
        f.load()

        unknown = f.object('UNKNOWN_SET', 'OBJ1', 10, 0)

        assert unknown.list == ["LIST_V1", "LIST_V2"]
        assert unknown.value == "VAL1"
        assert unknown.status == True
    finally:
        del f.types['UNKNOWN_SET']


def test_change_object_type(f):
    try:
        # Parse all parameters as if they where Channels
        dlisio.dlis.types['PARAMETER'] = dlisio.plumbing.Channel
        f.load()

        longname = f.object('LONG-NAME', 'PARAM1-LONG', 10, 0)
        axis     = f.object('AXIS', 'AXIS1', 10, 0)
        obj      = f.object('CHANNEL', 'PARAM1', 10, 0)

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
        dlisio.dlis.types['PARAMETER'] = dlisio.plumbing.Parameter

def test_remove_object_type(f):
    try:
        # Deleting object-type CHANNEL and reload
        del dlisio.dlis.types['CHANNEL']
        f.load()

        obj = f.object('CHANNEL', 'CHANN1', 10, 0)

        # Channel should be parsed as Unknown, but the type should still
        # reflects what's on file
        assert isinstance(obj, dlisio.plumbing.Unknown)
        assert obj in f.unknowns
        assert obj.type == 'CHANNEL'

    finally:
        # even if the test fails, make sure that types is reset to its default,
        # to not interfere with other tests
        f.types['CHANNEL'] = dlisio.plumbing.Channel

    f.load()
    obj = f.object('CHANNEL', 'CHANN1', 10, 0)

    # Channels should now be parsed as Channel.allobjects
    assert isinstance(obj, dlisio.plumbing.Channel)
    assert obj not in f.unknowns

def test_dynamic_instance_attribute(f):
    c = f.object('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)
    # update attributes only for one object
    c.attributes = dict(c.attributes)
    c.attributes['MY_PARAM'] = valuetypes.vector('myparams')

    c.load()
    assert c.myparams == ["wrong", "W"]

    # check that other object of the same type is not affected
    c = f.object('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)

    with pytest.raises(KeyError):
        _ = c.attributes['myparams']

def test_dynamic_class_attribute(f):
    try:
        # update attribute for the class
        Coefficient.attributes['MY_PARAM'] = valuetypes.vector('myparams')

        c = f.object('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)

        assert c.attributes['MY_PARAM'] == valuetypes.vector('myparams')
        c.load()
        assert c.myparams == ["wrong", "W"]

    finally:
        # manual cleanup. "reload" doesn't work
        del c.__class__.attributes['MY_PARAM']

def test_dynamic_linkage(f, assert_log):
    c = f.object('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)

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

    objects = {}
    for v in f.indexedobjects.values():
        objects.update(v)

    c.link(objects)

    param2 = f.object('PARAMETER', 'PARAM2', 10, 0)
    u      = f.object('UNKNOWN_SET', 'OBJ1', 10, 0)

    assert c.label        == "SMTH"
    assert c.paramlinks   == [param2, None]
    assert c.unknown_link == u

    assert_log("missing attribute")

def test_dynamic_change_through_instance(f):
    try:
        c = f.object('CALIBRATION-COEFFICIENT', 'COEFF1', 10, 0)
        c.attributes['MY_PARAM']            = valuetypes.vector('myparams')
        c.attributes['LINKS_TO_PARAMETERS'] = (
                    valuetypes.vector('paramlinks'))
        c.linkage['paramlinks']             = linkage.obname("PARAMETER")

        param2 = f.object('PARAMETER', 'PARAM2', 10, 0)
        c = f.object('CALIBRATION-COEFFICIENT', 'COEFF_BAD', 10, 0)
        c.load()

        objects = {}
        for v in f.indexedobjects.values():
            objects.update(v)

        c.link(objects)

        assert c.myparams     == ["wrong", "W"]
        assert c.paramlinks   == [param2, None]

    finally:
        del c.attributes['MY_PARAM']
        del c.attributes['LINKS_TO_PARAMETERS']
        del c.linkage['paramlinks']
