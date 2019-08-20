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

