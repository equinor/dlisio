import pytest

import dlisio

@pytest.fixture(scope="module")
def fpath(tmpdir_factory, merge_files_manyLR):
    path = str(tmpdir_factory.mktemp('load').join('manylogfiles.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        # First logical file, does not have FILE-HEADER
        'data/chap4-7/eflr/origin.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
        'data/chap4-7/eflr/frame.dlis.part',
        # Second logical file
        'data/chap4-7/eflr/file-header2.dlis.part',
        'data/chap4-7/eflr/origin2.dlis.part',
        'data/chap4-7/eflr/channel-inc.dlis.part',
        'data/chap4-7/eflr/frame-inc.dlis.part',
        'data/chap4-7/eflr/fdata-frame-inc-1.dlis.part',
        'data/chap4-7/eflr/frame.dlis.part',
        'data/chap4-7/eflr/fdata-frame-inc-2.dlis.part',
        # Third logical file, only has a FILE-HEADER
        'data/chap4-7/eflr/file-header.dlis.part',
    ]
    merge_files_manyLR(path, content)
    return path

def test_context_manager(fpath):
    f, *_ = dlisio.load(fpath)
    _ = f.fileheader
    f.close()

    files = dlisio.load(fpath)
    for f in files:
        _ = f.fileheader
        f.close()

    f, *files = dlisio.load(fpath)
    _ = f.fileheader
    for g in files:
        _ = g.fileheader
        g.close()

def test_context_manager_with(fpath):
    with dlisio.load(fpath) as (f, *_):
        _ = f.fileheader

    with dlisio.load(fpath) as files:
        for f in files:
            _ = f.fileheader

    with dlisio.load(fpath) as (f, *files):
        _ = f.fileheader
        for g in files:
            _ = g.fileheader

def test_partitioning(fpath):
    with dlisio.load(fpath) as (f1, f2, f3, *tail):
        assert len(tail) == 0

        def getobjects(f):
            objects = {}
            for v in f.indexedobjects.values():
                objects.update(v)
            return objects

        assert len(getobjects(f1)) == 8
        assert len(getobjects(f2)) == 7
        assert len(getobjects(f3)) == 1

        key = dlisio.core.fingerprint('FRAME', 'FRAME-INC', 10, 0)

        assert f1.explicit_indices == [0, 1, 2]
        assert not f1.fdata_index

        assert f2.explicit_indices == [0, 1, 2, 3, 5]
        assert f2.fdata_index[key] == [4, 6]

        assert f3.explicit_indices == [0]
        assert not f3.fdata_index

def test_objects(fpath):
    with dlisio.load(fpath) as (f1, f2, f3):
        fh2 = f2.object('FILE-HEADER', 'N', 11, 0)
        fh3 = f3.object('FILE-HEADER', 'N', 10, 0)

        assert f1.fileheader == None
        assert len(f1.origins)    == 2
        assert len(f1.channels)   == 4
        assert len(f1.frames)     == 2

        assert fh2.sequencenr == '10'
        assert fh2.id         == 'Yet another logical file'

        assert len(f2.origins)  == 1
        assert len(f2.channels) == 2
        assert len(f2.frames)   == 3

        assert fh3.sequencenr == '8'
        assert fh3.id         == 'some logical file'

def test_objects_with_encrypted_records(tmpdir_factory, merge_files_manyLR):
    fpath = str(tmpdir_factory.mktemp('load').join('same-object.dlis'))
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        # First logical file
        'data/chap4-7/eflr/file-header.dlis.part',
        'data/chap4-7/eflr/origin.dlis.part',
        'data/chap4-7/eflr/channel.dlis.part',
        'data/chap4-7/eflr/axis-encrypted.dlis.part',
        # Second logical file
        'data/chap4-7/eflr/file-header2.dlis.part',
        'data/chap4-7/eflr/origin2.dlis.part',
        'data/chap4-7/eflr/axis-encrypted.dlis.part',
        'data/chap4-7/eflr/channel-same-objects.dlis.part',
    ]
    merge_files_manyLR(fpath, content)

    with dlisio.load(fpath) as (f1, f2):
        f1_channel = f1.object('CHANNEL', 'CHANN1', 10, 0)
        f2_channel = f2.object('CHANNEL', 'CHANN1', 10, 0)

        assert len(f1_channel.dimension) == 3
        assert len(f2_channel.dimension) == 1

def test_link(fpath):
    with dlisio.load(fpath) as (f1, f2, _):
        frame1  = f1.object('FRAME', 'FRAME1', 10, 0)
        frame2  = f2.object('FRAME', 'FRAME1', 10, 0)
        channel = f1.object('CHANNEL', 'CHANN1', 10, 0)

        # The same frame is present in two different logical files. The
        # channels in frame.channel are only present in the first
        # logical file. Thus links are not available in the second file.
        assert channel in frame1.channels
        assert channel not in frame2.channels

def test_curves(fpath):
    with dlisio.load(fpath) as (_, f2, _):
        frame = f2.object('FRAME', 'FRAME-INC', 10, 0)
        curves = frame.curves()

        # Read the first value of the first frame of channel CH01
        assert curves['INC-CH1'][0] == 150
        assert curves[0]['INC-CH1'] == 150

        # Read the first value of the second frame of channel CH01
        assert curves['INC-CH1'][1] == 100
        assert curves[1]['INC-CH1'] == 100

def test_wellref_coordinates():
    wellref = dlisio.plumbing.wellref.Wellref()
    wellref.attic = {
        'COORDINATE-2-VALUE' : [2],
        'COORDINATE-1-NAME'  : ['longitude'],
        'COORDINATE-3-NAME'  : ['elevation'],
        'COORDINATE-1-VALUE' : [1],
        'COORDINATE-3-VALUE' : [3],
        'COORDINATE-2-NAME'  : ['latitude'],
    }

    wellref.load()

    assert wellref.coordinates['longitude']  == 1
    assert wellref.coordinates['latitude']   == 2
    assert wellref.coordinates['elevation']  == 3

    del wellref.attic['COORDINATE-3-VALUE']
    wellref.load()
    assert wellref.coordinates['latitude']   == 2
    assert wellref.coordinates['elevation']  == None

    del wellref.attic['COORDINATE-2-NAME']
    wellref.load()
    assert wellref.coordinates['longitude']    == 1
    assert wellref.coordinates['COORDINATE-2'] == 2

    del wellref.attic['COORDINATE-1-NAME']
    del wellref.attic['COORDINATE-1-VALUE']
    wellref.load()
    assert len(wellref.coordinates) == 3
    assert wellref.coordinates['COORDINATE-1'] == None

def test_valuetype_mismatch(assert_log):
    tool = dlisio.plumbing.tool.Tool()
    tool.attic = {
        'DESCRIPTION' : ["Description", "Unexpected description"],
        'STATUS'      : ["Yes", 0],
    }
    tool.load()

    assert tool.description == "Description"
    assert tool.status      == True
    assert_log("1 value in the attribute DESCRIPTION")
    assert_log("1 value in the attribute STATUS")
