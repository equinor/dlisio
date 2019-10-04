import dlisio
import pytest

from dlisio.plumbing.channel import Channel
from dlisio.plumbing.frame import Frame
from dlisio.plumbing.unknown import Unknown

@pytest.fixture(scope="module")
def g():
    s = dlisio.open("tests/test_dlis.py") #any existing file is required
    g = dlisio.dlis(s, [], None, [])

    ch = Channel()
    ch.name = 'CHANNEL1'
    ch.origin = 0
    ch.copynumber = 0
    g.indexedobjects["CHANNEL"][ch.fingerprint] = ch

    ch = Channel()
    ch.name = 'CHANNEL1.V2'
    ch.origin = 0
    ch.copynumber = 0
    g.indexedobjects["CHANNEL"][ch.fingerprint] = ch

    ch = Channel()
    ch.name = 'CHANNEL1'
    ch.origin = 0
    ch.copynumber = 1
    g.indexedobjects["CHANNEL"][ch.fingerprint] = ch

    un = Unknown()
    un.name = 'UNEFRAME'
    un.origin = 0
    un.copynumber = 0
    un.type = "NONCHANNEL"
    g.indexedobjects["NONCHANNEL"][un.fingerprint] = un

    fr = Frame()
    fr.name = 'UNEFRAME'
    fr.origin = 0
    fr.copynumber = 0
    g.indexedobjects["FRAME"][fr.fingerprint] = fr

    un = Unknown()
    un.name = '440-CHANNEL'
    un.origin = 0
    un.copynumber = 0
    un.type = "440.TYPE"
    g.indexedobjects["440.TYPE"][un.fingerprint] = un

    ch = Channel()
    ch.name = '440.CHANNEL'
    ch.origin = 0
    ch.copynumber = 0
    ch.type = "440-TYPE"
    g.indexedobjects["440-TYPE"][ch.fingerprint] = ch

    return g

def test_object(g):
    channel = g.object("CHANNEL", "CHANNEL1", 0, 1)
    assert channel.name       == "CHANNEL1"
    assert channel.origin     == 0
    assert channel.copynumber == 1
    assert channel.type       == "CHANNEL"

def test_unknown_object(g):
    channel = g.object("NONCHANNEL", "UNEFRAME", 0, 0)
    assert channel.name       == "UNEFRAME"
    assert channel.origin     == 0
    assert channel.copynumber == 0
    assert channel.type       == "NONCHANNEL"

def test_nonexisting_object(g):
    with pytest.raises(ValueError) as exc:
        _ = g.object("UNKNOWN_TYPE", "SOME_OBJECT", 0, 0)
    assert "not found" in str(exc.value)

    with pytest.raises(ValueError):
        _ = g.object("CHANNEL", "CHANNEL1", 11, 0)

    with pytest.raises(TypeError):
        _ = g.object("WEIRD", "CHANNEL1", "-1", "-1")

def test_solo_object_nameonly(g):
    channel = g.object("CHANNEL", "CHANNEL1.V2")
    assert channel.name == "CHANNEL1.V2"
    assert channel.origin == 0
    assert channel.copynumber == 0
    assert channel.type == "CHANNEL"

def test_nonexisting_object_nameonly(g):
    with pytest.raises(ValueError) as exc:
        _ = g.object("CHANNEL", "NOTFOUND")
    assert "No objects" in str(exc.value)

def test_too_many_objects_nameonly(g):
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

