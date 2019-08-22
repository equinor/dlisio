import pytest

from dlisio.core import fingerprint
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

        def __init__(self, obj = None, name = None):
            super().__init__(obj, name = name, type = "UNKNOWN_SET")
            self.list = []
            self.value = None
            self.status = None

    key = fingerprint('UNKNOWN_SET', 'OBJ1', 10, 0)
    unknown = f.objects[key]
    with pytest.raises(AttributeError):
        assert unknown.value == "VAL1"

    try:
        f.types['UNKNOWN_SET'] = ActuallyKnown
        f.load()

        key = fingerprint('UNKNOWN_SET', 'OBJ1', 10, 0)
        unknown = f.objects[key]

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
        dlisio.dlis.types['PARAMETER'] = dlisio.plumbing.Parameter

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
        f.types['CHANNEL'] = dlisio.plumbing.Channel

    f.load()
    obj = f.objects[key]

    # Channels should now be parsed as Channel.allobjects
    assert isinstance(obj, dlisio.plumbing.Channel)
    assert obj not in f.unknowns

def test_dynamic_instance_attribute(f):
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
        _ = c.attributes['myparams']

def test_dynamic_class_attribute(f):
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

def test_dynamic_linkage(f, assert_log):
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

    assert_log("missing attribute")

def test_dynamic_change_through_instance(f):
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
