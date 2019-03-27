import pytest

import dlisio

@pytest.fixture(scope="module", name="f")
def load_206_DWL():
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        yield f

@pytest.fixture(scope="module", name="channels_f")
def load_only_channels():
    with dlisio.load('data/only-channels.dlis') as f:
        yield f
