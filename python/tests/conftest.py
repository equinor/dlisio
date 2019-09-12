import pytest

import dlisio

@pytest.fixture(scope="module", name="DWL206")
def DWL206():
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as (f,):
        yield f

@pytest.fixture(scope="module")
def merge_files():
    def merge(fpath, flist, lrs_offset = None):
        b = bytearray()
        for file in flist:
            with open(file, 'rb') as source:
                b += bytearray(source.read())

        with open(fpath, "wb") as dest:
            update_envelope_VRL_and_LRSL(b, lrs_offset)
            dest.write(b)

    return merge

def update_envelope_VRL_and_LRSL(b, lrs_offset = None):
    if lrs_offset:
        lrsl = len(b) - lrs_offset
        padbytes_count = max(0, 20 - lrsl)

        if (len(b) + padbytes_count) % 2 :
            padbytes_count += 1
        else:
            padbytes_count += 2

        padbytes = bytearray([0x01] * (padbytes_count - 1))
        padbytes.extend([padbytes_count])

        b.extend(padbytes)

        lrsl = len(b) - lrs_offset
        b[lrs_offset]     = lrsl // 256
        b[lrs_offset + 1] = lrsl %  256

    vrl = len(b) - 80
    b[80] = vrl // 256
    b[81] = vrl %  256

@pytest.fixture
def assert_log(caplog):
    def assert_message(message_id):
        assert any([message_id in r.message for r in caplog.records])
    return assert_message

@pytest.fixture(scope="module")
def fpath(tmpdir_factory, merge_files):
    path = str(tmpdir_factory.mktemp('semantic').join('semantic.dlis'))
    content = [
        'data/semantic/envelope.dlis.part',
        'data/semantic/file-header.dlis.part',
        'data/semantic/origin.dlis.part',
        'data/semantic/well-reference-point.dlis.part',
        'data/semantic/axis.dlis.part',
        'data/semantic/long-name-record.dlis.part',
        'data/semantic/channel.dlis.part',
        'data/semantic/frame.dlis.part',
        'data/semantic/fdata-frame1-1.dlis.part',
        'data/semantic/fdata-frame1-2.dlis.part',
        'data/semantic/fdata-frame1-3.dlis.part',
        'data/semantic/path.dlis.part',
        'data/semantic/zone.dlis.part',
        'data/semantic/parameter.dlis.part',
        'data/semantic/equipment.dlis.part',
        'data/semantic/tool.dlis.part',
        'data/semantic/process.dlis.part',
        'data/semantic/computation.dlis.part',
        'data/semantic/measurement.dlis.part',
        'data/semantic/coefficient.dlis.part',
        'data/semantic/coefficient-wrong.dlis.part',
        'data/semantic/calibration.dlis.part',
        'data/semantic/group.dlis.part',
        'data/semantic/splice.dlis.part',
        'data/semantic/message.dlis.part',
        'data/semantic/comment.dlis.part',
        'data/semantic/update.dlis.part',
        'data/semantic/unknown.dlis.part',
        'data/semantic/channel-reprcode.dlis.part',
        'data/semantic/frame-reprcode.dlis.part',
        'data/semantic/fdata-reprcode.dlis.part',
        'data/semantic/file-header2.dlis.part',
        'data/semantic/origin2.dlis.part',
        'data/semantic/channel-dimension.dlis.part',
        'data/semantic/frame-dimension.dlis.part',
        'data/semantic/fdata-dimension.dlis.part',
    ]
    merge_files(path, content)
    return path

@pytest.fixture(scope="module")
def f(fpath):
    with dlisio.load(fpath) as (f, *_):
        yield f
