"""
Testing Logical file class (also known as dlis)
"""

import dlisio
import pytest

from dlisio.plumbing.channel import Channel
from dlisio.plumbing.frame import Frame
from dlisio.plumbing.unknown import Unknown

from dlisio import core

def test_object(f):
    channel = f.object("CHANNEL", "CHANN1", 10, 0)
    assert channel.name       == "CHANN1"
    assert channel.origin     == 10
    assert channel.copynumber == 0
    assert channel.type       == "CHANNEL"

def test_object_unknown(f):
    channel = f.object("UNKNOWN_SET", "OBJ1", 10, 0)
    assert channel.name       == "OBJ1"
    assert channel.origin     == 10
    assert channel.copynumber == 0
    assert channel.type       == "UNKNOWN_SET"

def test_object_nonexisting(f):
    with pytest.raises(ValueError) as exc:
        _ = f.object("UNKNOWN_TYPE", "SOME_OBJECT", 0, 0)
    assert "not found" in str(exc.value)

    with pytest.raises(ValueError):
        _ = f.object("CHANNEL", "CHANN1", 11, 0)

    with pytest.raises(TypeError):
        _ = f.object("WEIRD", "CHANN1", "-1", "-1")

def test_object_solo_nameonly(f):
    channel = f.object("CHANNEL", "CHANN2")
    assert channel.name       == "CHANN2"
    assert channel.origin     == 10
    assert channel.copynumber == 0
    assert channel.type       == "CHANNEL"

def test_object_nonexisting_nameonly(f):
    with pytest.raises(ValueError) as exc:
        _ = f.object("CHANNEL", "NOTFOUND")
    assert "No objects" in str(exc.value)

def test_object_many_objects_nameonly(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('lf').join('same-id.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.127-C.0.dlis.part',
    ]
    merge_files_manyLR(fpath, content)
    with dlisio.load(fpath) as (f, *_):
        with pytest.raises(ValueError) as exc:
            _ = f.object("CHANNEL", "MATCH1")
        assert "There are multiple" in str(exc.value)

def test_match(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('lf').join('match.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH111-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.127-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.440-TYPE-I.440.MATCH1-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.440.TYPE-I.440-MATCH1-O.16-C.0.dlis.part',
    ]
    merge_files_manyLR(fpath, content)
    with dlisio.load(fpath) as (f, *_):
        refs = []
        refs.append(f.object('CHANNEL', 'MATCH1', 16, 0))
        refs.append(f.object('CHANNEL', 'MATCH111', 16, 0))
        refs.append(f.object('CHANNEL', 'MATCH1', 127, 0))

        channels = f.match('.*match1.*')

        assert len(list(channels)) == 3
        for ch in channels:
            assert ch in refs

        channels = f.match('.*match1.*', ".*")
        assert len(list(channels)) == 5

def test_match_type(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('lf').join('match-type.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/match/T.FRAME-I.MATCH22-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.MATCH-I.MATCH22-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.16-C.0.dlis.part',
    ]
    merge_files_manyLR(fpath, content)
    with dlisio.load(fpath) as (f, *_):
        refs = []
        refs.append( f.object('MATCH', 'MATCH22', 16, 0) )
        refs.append( f.object('FRAME', 'MATCH22', 16, 0) )

        objs = f.match('MATCH2.*', type='MATCH|FRAME')

        assert len(list(objs)) == len(refs)
        for obj in objs:
            assert obj in refs

        objs = f.match('', type='MATCH|frame')

        assert len(list(objs)) == len(refs)
        for obj in objs:
            assert obj in refs

def test_match_invalid_regex(f):
    with pytest.raises(ValueError):
        _ = next(f.match('*'))

    with pytest.raises(ValueError):
        _ = next(f.match('AIBK', type='*'))

def test_match_special_characters(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('lf').join('match-special.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.440-TYPE-I.440.MATCH1-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.440.TYPE-I.440-MATCH1-O.16-C.0.dlis.part',
    ]
    merge_files_manyLR(fpath, content)
    with dlisio.load(fpath) as (f, *_):
        o1 = f.object('440.TYPE', '440-MATCH1', 16, 0)
        o2 = f.object('440-TYPE', '440.MATCH1', 16, 0)

        refs = [o1, o2]
        channels = f.match('440.MATCH1', '440.TYPE')

        assert len(list(channels)) == 2
        for ch in channels:
            assert ch in refs

        refs = [o1]
        channels = f.match('440-MATCH1', '440.TYPE')
        assert len(list(channels)) == 1
        for ch in channels:
            assert ch in refs

        refs = [o2]
        channels = f.match('440.MATCH1', '440-TYPE')
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
