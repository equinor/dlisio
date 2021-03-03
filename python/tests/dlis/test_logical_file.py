"""
Testing Logical file class (also known as dlis)
"""

import pytest
import os

from dlisio import core, dlis

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
    assert ("Object not found: type=UNKNOWN_TYPE, name=SOME_OBJECT, "
            "origin=0, copynumber=0") in str(exc.value)

    with pytest.raises(ValueError):
        _ = f.object("CHANNEL", "CHANN1", 11, 0)

    with pytest.raises(ValueError):
        _ = f.object("CHANNEL", "CHANN1", "-1", "-1")

def test_object_solo_nameonly(f):
    channel = f.object("CHANNEL", "CHANN2")
    assert channel.name       == "CHANN2"
    assert channel.origin     == 10
    assert channel.copynumber == 0
    assert channel.type       == "CHANNEL"

def test_object_nonexisting_nameonly(f):
    with pytest.raises(ValueError) as exc:
        _ = f.object("CHANNEL", "NOTFOUND")
    assert "Object not found" in str(exc.value)

def test_object_many_objects_nameonly(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('lf').join('same-id.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.127-C.0.dlis.part',
    ]
    merge_files_manyLR(fpath, content)
    with dlis.load(fpath) as (f, *_):
        with pytest.raises(ValueError) as exc:
            _ = f.object("CHANNEL", "MATCH1")
        assert "Candidates are" in str(exc.value)
        assert "origin=16, copy=0" in str(exc.value)
        assert "origin=127, copy=0" in str(exc.value)

def test_object_ducplicated_object(tmpdir_factory, merge_files_manyLR):
    # Spec violation: Two objects with the same signature AND identical content
    fpath = str(tmpdir_factory.mktemp('lf').join('same-id.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.127-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.127-C.0.dlis.part',
    ]
    merge_files_manyLR(fpath, content)
    with dlis.load(fpath) as (f, *_):
        ch = f.object("CHANNEL", "MATCH1")

        assert ch.name       == "MATCH1"
        assert ch.origin     == 127
        assert ch.copynumber == 0

        assert ch == f.object("CHANNEL", "MATCH1", 127, 0)

def test_object_same_signature_diff_content(tmpdir_factory, merge_files_manyLR):
    # Spec violation: Two objects with the same signature BUT different content
    fpath = str(tmpdir_factory.mktemp('lf').join('same-id.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
        'data/chap4-7/eflr/channel-same-objects.dlis.part',
    ]
    merge_files_manyLR(fpath, content)

    with dlis.load(fpath) as (f, *_):
        with pytest.raises(ValueError) as exc:
            _ = f.object("CHANNEL", "CHANN1", 10, 0)
        assert "Candidates are" in str(exc.value)

        # They can still be reached through find
        chs = f.find("CHANNEL", "CHANN1")
        assert len(chs) == 2

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
    with dlis.load(fpath) as (f, *_):
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
    with dlis.load(fpath) as (f, *_):
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
    with dlis.load(fpath) as (f, *_):
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

def test_find(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('lf').join('find.dlis'))
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
    with dlis.load(fpath) as (f, *_):
        refs = []
        refs.append(f.object('CHANNEL', 'MATCH1', 16, 0))
        refs.append(f.object('CHANNEL', 'MATCH111', 16, 0))
        refs.append(f.object('CHANNEL', 'MATCH1', 127, 0))

        channels = f.find('CHANNEL', '.*match1.*')

        assert len(list(channels)) == 3
        for ch in channels:
            assert ch in refs

        channels = f.find('.*', '.*match1.*')
        assert len(list(channels)) == 5

def test_find_type(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('lf').join('find-type.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/match/T.FRAME-I.MATCH22-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.MATCH-I.MATCH22-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.16-C.0.dlis.part',
    ]
    merge_files_manyLR(fpath, content)
    with dlis.load(fpath) as (f, *_):
        refs = []
        refs.append( f.object('MATCH', 'MATCH22', 16, 0) )
        refs.append( f.object('FRAME', 'MATCH22', 16, 0) )

        objs = f.find('MATCH|FRAME', 'MATCH2.*')

        assert len(list(objs)) == len(refs)
        for obj in objs:
            assert obj in refs

        objs = f.find('match|frame', '')

        assert len(list(objs)) == len(refs)
        for obj in objs:
            assert obj in refs

def test_find_invalid_regex(f):
    with pytest.raises(ValueError):
        _ = next(f.find('*'))

    with pytest.raises(ValueError):
        _ = next(f.find('*', 'AIBK'))

def test_find_special_characters(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('lf').join('find-special.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/match/T.CHANNEL-I.MATCH1-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.440-TYPE-I.440.MATCH1-O.16-C.0.dlis.part',
        'data/chap4-7/eflr/match/T.440.TYPE-I.440-MATCH1-O.16-C.0.dlis.part',
    ]
    merge_files_manyLR(fpath, content)
    with dlis.load(fpath) as (f, *_):
        o1 = f.object('440.TYPE', '440-MATCH1', 16, 0)
        o2 = f.object('440-TYPE', '440.MATCH1', 16, 0)

        refs = [o1, o2]
        channels = f.find('440.TYPE', '440.MATCH1')

        assert len(list(channels)) == 2
        for ch in channels:
            assert ch in refs

        refs = [o1]
        channels = f.find('440.TYPE', '440-MATCH1')
        assert len(list(channels)) == 1
        for ch in channels:
            assert ch in refs

        refs = [o2]
        channels = f.find('440-TYPE', '440.MATCH1')
        assert len(list(channels)) == 1
        for ch in channels:
            assert ch in refs

def test_dlis_types(f):
    assert f.fileheader.name   == "N"
    assert len(f.origins)      == 2
    assert len(f.axes)         == 3
    assert len(f.longnames)    == 5
    assert len(f.channels)     == 4
    assert len(f.frames)       == 2
    assert len(f.zones)        == 1
    assert len(f.tools)        == 2
    assert len(f.parameters)   == 3
    assert len(f.processes)    == 2
    assert len(f.groups)       == 3
    assert len(f.wellrefs)     == 1
    assert len(f.splices)      == 1
    assert len(f.paths)        == 2
    assert len(f.equipments)   == 1
    assert len(f.computations) == 3
    assert len(f.measurements) == 2
    assert len(f.coefficients) == 2
    assert len(f.calibrations) == 1
    assert len(f.comments)     == 1
    assert len(f.messages)     == 1
    assert len(f.noformats)    == 2

def test_load_unknowns():
    with dlis.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as (f,):
        assert len(f.unknowns) == 5

def test_unknowns_multiple_sets(tmpdir_factory, merge_files_manyLR):
    # Multiple sets of the same type are loaded correctly. All objects are
    # unique.
    fpath = str(tmpdir_factory.mktemp('lf').join('two-ch-sets.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/unknown.dlis.part',
        'data/chap4-7/eflr/unknown2.dlis.part',
    ]
    merge_files_manyLR(fpath, content)

    with dlis.load(fpath) as (f, *_):
        assert len(f.unknowns['UNKNOWN_SET']) == 2

def test_noform_data(tmpdir):
    fpath = 'data/chap4-7/iflr/noform.dlis'
    with dlis.load(fpath) as (f, *_):

        assert len(f.fdata_index) == 3

        noform_text = f.object('NO-FORMAT', 'NOFORMAT-TEXT', 10, 0)
        expected_text = "This is a test data and it has no meaning."
        actual_text = noform_text.data()
        assert actual_text.decode("utf-8") == expected_text

        # handling of images is essentially same as handling of text
        # it's present only because text and images are common noform
        noform_image = f.object('NO-FORMAT', 'NOFORMAT-IMAGE', 10, 0)
        imagepath = str(tmpdir.join("dlisio-logo.png"))
        out = open(imagepath, 'wb')
        out.write(noform_image.data())
        out.close()
        assert os.path.getsize(imagepath) == 12977

        noform_unused = f.object('NO-FORMAT', 'NOFORMAT-UNUSED', 10, 0)
        assert len(noform_unused.data()) == 0
