"""
Testing division of one physical file into several logical files
"""

from dlisio import dlis, core

def test_partitioning():
    path = 'data/chap4-7/many-logical-files.dlis'
    with dlis.load(path) as (f1, f2, f3, *tail):
        assert len(tail) == 0

        def getobjects(f):
            return f.find('.*', '.*')

        assert len(getobjects(f1)) == 8
        assert len(getobjects(f2)) == 7
        assert len(getobjects(f3)) == 1

        key = core.fingerprint('FRAME', 'FRAME-INC', 10, 0)

        assert f1.object_pool.types == ['ORIGIN', 'CHANNEL', 'FRAME']
        assert not f1.fdata_index

        assert f2.object_pool.types == ['FILE-HEADER', 'ORIGIN', 'CHANNEL',
                                     'FRAME', 'FRAME']
        assert f2.fdata_index[key] == [824, 1060]

        assert f3.object_pool.types == ['FILE-HEADER']
        assert not f3.fdata_index

def test_objects_ownership():
    path = 'data/chap4-7/many-logical-files.dlis'
    with dlis.load(path) as (f1, f2, f3):
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

def test_objects_with_encrypted_records_ownership():
    path = 'data/chap4-7/many-logical-files-same-object.dlis'

    with dlis.load(path) as (f1, f2):
        f1_channel = f1.object('CHANNEL', 'CHANN1', 10, 0)
        f2_channel = f2.object('CHANNEL', 'CHANN1', 10, 0)

        assert len(f1_channel.dimension) == 3
        assert len(f2_channel.dimension) == 1

def test_linking():
    path = 'data/chap4-7/many-logical-files.dlis'
    with dlis.load(path) as (f1, f2, _):
        frame1  = f1.object('FRAME', 'FRAME1', 10, 0)
        frame2  = f2.object('FRAME', 'FRAME1', 10, 0)
        channel = f1.object('CHANNEL', 'CHANN1', 10, 0)

        # The same frame is present in two different logical files. The
        # channels in frame.channel are only present in the first
        # logical file. Thus links are not available in the second file.
        assert channel in frame1.channels
        assert channel not in frame2.channels

