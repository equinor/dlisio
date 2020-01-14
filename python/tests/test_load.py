import pytest

import shutil
import os

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

def test_closed_filehandles(tmpdir):
    # Check that both the memory mapping and regular filehandle is closed
    # property. This test uses the fact that os.remove fails on windows if the
    # file is in use as a proxy for testing that dlisio dont leak filehandles.
    # From the python docs [1]:
    #
    #   On Windows, attempting to remove a file that is in use causes an
    #   exception to be raised; on Unix, the directory entry is removed but the
    #   storage allocated to the file is not made available until the original
    #   file is no longer in use.
    #
    # On linux on the other hand, os.remove does not fail even if there are
    # open filehandles, hence this test only makes sence on Windows.
    #
    # [1] https://docs.python.org/3/library/os.html

    # Copy the test file to a tmpdir in order to make this test reliable.
    tmp = str(tmpdir.join('206_05a-_3_DWL_DWL_WIRE_258276498.DLIS'))
    shutil.copyfile('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS', tmp)

    with dlisio.load(tmp) as _:
        pass

    os.remove(tmp)

def test_close_filehandles_when_load_fails(tmpdir):
    # Check that both the memory mapping and regular filehandle is closed
    # property. This test uses the fact that os.remove fails on windows if the
    # file is in use as a proxy for testing that dlisio dont leak filehandles.
    # From the python docs [1]:
    #
    #   On Windows, attempting to remove a file that is in use causes an
    #   exception to be raised; on Unix, the directory entry is removed but the
    #   storage allocated to the file is not made available until the original
    #   file is no longer in use.
    #
    # On linux on the other hand, os.remove does not fail even if there are
    # open filehandles, hence this test only makes sence on Windows.
    #
    # [1] https://docs.python.org/3/library/os.html

    # Copy the test files to a tmpdir in order to make this test reliable.
    offsets = str(tmpdir.join('offsets'))
    shutil.copyfile('data/chap2/too-small-record.dlis', offsets)

    extract = str(tmpdir.join('extract'))
    shutil.copyfile('data/chap2/padbytes-bad.dlis', extract)

    fdata = str(tmpdir.join('fdata'))
    shutil.copyfile('data/chap2/fdata-encrypted.dlis', fdata)

    # dlisio.load fails at core.findoffsets
    with pytest.raises(RuntimeError):
        _ =  dlisio.load(offsets)

    # dlisio.load fails at core.stream.extract
    with pytest.raises(RuntimeError):
        _ =  dlisio.load(extract)

    # dlisio.load fails at core.findfdata
    with pytest.raises(UnicodeDecodeError):
        _ =  dlisio.load(fdata)

    # If dlisio have properly closed the files, removing them should work.
    os.remove(offsets)
    os.remove(extract)
    os.remove(fdata)

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

    assert wellref.coordinates['longitude']  == 1
    assert wellref.coordinates['latitude']   == 2
    assert wellref.coordinates['elevation']  == 3

    del wellref.attic['COORDINATE-3-VALUE']
    assert wellref.coordinates['latitude']   == 2
    assert wellref.coordinates['elevation']  == None

    del wellref.attic['COORDINATE-2-NAME']
    assert wellref.coordinates['longitude']    == 1
    assert wellref.coordinates['COORDINATE-2'] == 2

    del wellref.attic['COORDINATE-1-NAME']
    del wellref.attic['COORDINATE-1-VALUE']
    assert len(wellref.coordinates) == 3
    assert wellref.coordinates['COORDINATE-1'] == None

def test_valuetype_mismatch(assert_log):
    tool = dlisio.plumbing.tool.Tool()
    tool.attic = {
        'DESCRIPTION' : ["Description", "Unexpected description"],
        'STATUS'      : ["Yes", 0],
    }

    assert tool.description == "Description"
    assert tool.status      == True
    assert_log('Expected only 1 value')
    assert_log('Expected only 1 value')
