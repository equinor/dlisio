"""
Testing Logical file class (also known as dlis)
"""

import dlisio
import pytest

from dlisio.plumbing.channel import Channel
from dlisio.plumbing.frame import Frame
from dlisio.plumbing.unknown import Unknown

from dlisio import core

@pytest.fixture(scope="module")
def g():
    s = dlisio.open("tests/test_logical_file.py") #any existing file is required
    g = dlisio.dlis(s, [], [], [])

    ch = Channel()
    ch.name = 'CHANNEL1'
    ch.origin = 0
    ch.copynumber = 0
    ch.logicalfile = g
    g.indexedobjects["CHANNEL"][ch.fingerprint] = ch

    ch = Channel()
    ch.name = 'CHANNEL1.V2'
    ch.origin = 0
    ch.copynumber = 0
    ch.logicalfile = g
    g.indexedobjects["CHANNEL"][ch.fingerprint] = ch

    ch = Channel()
    ch.name = 'CHANNEL1'
    ch.origin = 0
    ch.copynumber = 1
    ch.logicalfile = g
    g.indexedobjects["CHANNEL"][ch.fingerprint] = ch

    un = Unknown()
    un.name = 'UNEFRAME'
    un.origin = 0
    un.copynumber = 0
    un.type = "NONCHANNEL"
    un.logicalfile = g
    g.indexedobjects["NONCHANNEL"][un.fingerprint] = un

    fr = Frame()
    fr.name = 'UNEFRAME'
    fr.origin = 0
    fr.copynumber = 0
    fr.logicalfile = g
    g.indexedobjects["FRAME"][fr.fingerprint] = fr

    un = Unknown()
    un.name = '440-CHANNEL'
    un.origin = 0
    un.copynumber = 0
    un.type = "440.TYPE"
    un.logicalfile = g
    g.indexedobjects["440.TYPE"][un.fingerprint] = un

    ch = Channel()
    ch.name = '440.CHANNEL'
    ch.origin = 0
    ch.copynumber = 0
    ch.type = "440-TYPE"
    ch.logicalfile = g
    g.indexedobjects["440-TYPE"][ch.fingerprint] = ch

    g.record_types = list(g.indexedobjects.keys())

    # Simulate the occurance of multiple Channel sets
    g.record_types.append('CHANNEL')
    return g

def test_object(g):
    channel = g.object("CHANNEL", "CHANNEL1", 0, 1)
    assert channel.name       == "CHANNEL1"
    assert channel.origin     == 0
    assert channel.copynumber == 1
    assert channel.type       == "CHANNEL"

def test_object_unknown(g):
    channel = g.object("NONCHANNEL", "UNEFRAME", 0, 0)
    assert channel.name       == "UNEFRAME"
    assert channel.origin     == 0
    assert channel.copynumber == 0
    assert channel.type       == "NONCHANNEL"

def test_object_nonexisting(g):
    with pytest.raises(ValueError) as exc:
        _ = g.object("UNKNOWN_TYPE", "SOME_OBJECT", 0, 0)
    assert "not found" in str(exc.value)

    with pytest.raises(ValueError):
        _ = g.object("CHANNEL", "CHANNEL1", 11, 0)

    with pytest.raises(TypeError):
        _ = g.object("WEIRD", "CHANNEL1", "-1", "-1")

def test_object_solo_nameonly(g):
    channel = g.object("CHANNEL", "CHANNEL1.V2")
    assert channel.name == "CHANNEL1.V2"
    assert channel.origin == 0
    assert channel.copynumber == 0
    assert channel.type == "CHANNEL"

def test_object_nonexisting_nameonly(g):
    with pytest.raises(ValueError) as exc:
        _ = g.object("CHANNEL", "NOTFOUND")
    assert "No objects" in str(exc.value)

def test_object_many_objects_nameonly(g):
    with pytest.raises(ValueError) as exc:
        _ = g.object("CHANNEL", "CHANNEL1")
    assert "There are multiple" in str(exc.value)

def test_match(g):
    refs = []
    refs.append( g.object('CHANNEL', 'CHANNEL1', 0, 0) )
    refs.append( g.object('CHANNEL', 'CHANNEL1.V2', 0, 0) )
    refs.append( g.object('CHANNEL', 'CHANNEL1', 0, 1) )

    channels = g.match('.*chan.*')

    assert len(list(channels)) == 3
    for ch in channels:
        assert ch in refs

    channels = g.match('.*chan.*', ".*")
    assert len(list(channels)) == 5

def test_match_type(g):
    refs = []

    refs.append( g.object('NONCHANNEL', 'UNEFRAME', 0, 0) )
    refs.append( g.object('FRAME', 'UNEFRAME', 0, 0) )

    objs = g.match('UNEFR.*', type='NONCHANNEL|FRAME')

    assert len(list(objs)) == len(refs)
    for obj in objs:
        assert obj in refs

    objs = g.match('', type='NONCHANNEL|frame')

    assert len(list(objs)) == len(refs)
    for obj in objs:
        assert obj in refs

def test_match_invalid_regex(g):
    with pytest.raises(ValueError):
        _ = next(g.match('*'))

    with pytest.raises(ValueError):
        _ = next(g.match('AIBK', type='*'))

def test_match_special_characters(g):
    o1 = g.object('440.TYPE', '440-CHANNEL', 0, 0)
    o2 = g.object('440-TYPE', '440.CHANNEL', 0, 0)

    refs = [o1, o2]
    channels = g.match('440.CHANNEL', '440.TYPE')

    assert len(list(channels)) == 2
    for ch in channels:
        assert ch in refs

    refs = [o1]
    channels = g.match('440-CHANNEL', '440.TYPE')
    assert len(list(channels)) == 1
    for ch in channels:
        assert ch in refs

    refs = [o2]
    channels = g.match('440.CHANNEL', '440-TYPE')
    assert len(list(channels)) == 1
    for ch in channels:
        assert ch in refs

def test_indexedobjects(f):
    assert f.fileheader.name   == "N"
    assert len(f.origins)      == 2
    assert len(f.axes)         == 3
    assert len(f.longnames)    == 4
    assert len(f.channels)     == 4
    assert len(f.frames)       == 2
    assert len(f.zones)        == 1
    assert len(f.tools)        == 1
    assert len(f.parameters)   == 3
    assert len(f.processes)    == 2
    assert len(f.groups)       == 3
    assert len(f.wellrefs)     == 1
    assert len(f.splices)      == 1
    assert len(f.paths)        == 2
    assert len(f.equipments)   == 1
    assert len(f.computations) == 3
    assert len(f.measurements) == 2
    assert len(f.coefficients) == 3
    assert len(f.calibrations) == 1
    assert len(f.comments)     == 1
    assert len(f.messages)     == 1

def test_indexedobjects_initial_load(fpath):
    with dlisio.load(fpath) as (f, *tail):
        # Only fileheader, origin, frame, and channel should be loaded
        assert len(f.indexedobjects) == 4


def test_indexedobjects_load_all(fpath):
    with dlisio.load(fpath) as (f, *_):
        f.load()
        assert len(f.indexedobjects) == 23

def test_indexedobjects_load_unknowns():
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as (f,):
        assert len(f.indexedobjects) == 4 #FILE-HEADER, ORIGIN, FRAME, CHANNEL
        assert len(f.unknowns)       == 5
        assert len(f.indexedobjects) == 9

def test_indexedobjects_load_by_typeloading(fpath):
    with dlisio.load(fpath) as (f, *tail):
        fp = core.fingerprint('PARAMETER', 'PARAM1', 10, 0)
        parameters = f.parameters

        assert len(parameters) == 3
        assert fp in f.indexedobjects['PARAMETER']

def test_indexedobjects_load_by_direct_call(fpath):
    with dlisio.load(fpath) as (f, *tail):
        fp = core.fingerprint('TOOL', 'TOOL1', 10, 0)
        _ = f.object('TOOL', 'TOOL1', 10, 0)

        assert fp in f.indexedobjects['TOOL']

def test_indexedobjects_load_by_match(fpath):
    with dlisio.load(fpath) as (f, *tail):
        fp = core.fingerprint('MESSAGE', 'MESSAGE1', 10, 0)

        _ = list(f.match('.*' , type='MESSAGE'))

        assert fp in f.indexedobjects['MESSAGE']

def test_indexedobjects_load_by_link(fpath):
    with dlisio.load(fpath) as (f, *tail):
        fp = core.fingerprint('LONG-NAME', 'CHANN1-LONG-NAME', 10, 0)
        ch = f.object('CHANNEL', 'CHANN1')

        # Accessing long-name should trigger loading of all long-names
        _ = ch.long_name
        assert fp in f.indexedobjects['LONG-NAME']
        assert len(f.indexedobjects['LONG-NAME']) == 4
