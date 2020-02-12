"""
Testing division of one physical file into several logical files
"""

import dlisio

def test_partitioning(multifpath):
    with dlisio.load(multifpath) as (f1, f2, f3, *tail):
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

def test_objects_ownership(multifpath):
    with dlisio.load(multifpath) as (f1, f2, f3):
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

def test_objects_with_encrypted_records_ownership(tmpdir_factory, merge_files_manyLR):
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

def test_linking(multifpath):
    with dlisio.load(multifpath) as (f1, f2, _):
        frame1  = f1.object('FRAME', 'FRAME1', 10, 0)
        frame2  = f2.object('FRAME', 'FRAME1', 10, 0)
        channel = f1.object('CHANNEL', 'CHANN1', 10, 0)

        # The same frame is present in two different logical files. The
        # channels in frame.channel are only present in the first
        # logical file. Thus links are not available in the second file.
        assert channel in frame1.channels
        assert channel not in frame2.channels

