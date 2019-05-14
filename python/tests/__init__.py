import pytest

import dlisio

@pytest.fixture(scope="module", name="DWL206")
def DWL206():
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        yield f

@pytest.fixture(scope="module", name="only_channels")
def only_channels():
    with dlisio.load('data/only-channels.dlis') as f:
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
