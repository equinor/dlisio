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
