import pytest
import hypothesis
from hypothesis import given
import hypothesis.strategies as st

import dlisio

def test_sul():
    label = ''.join([
                '   1',
                'V1.00',
                'RECORD',
                ' 8192',
                'Default Storage Set                                         ',
            ])

    sul = dlisio.core.sul(label)
    d = {
        'sequence': 1,
        'version': '1.0',
        'maxlen': 8192,
        'layout': 'record',
        'id': 'Default Storage Set                                         ',
    }

    assert sul == d

    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        assert f.sul == d

def test_file_properties():
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        assert len(f.bookmarks) == 3252

@given(st.integers(min_value = 0, max_value = 3251))
def test_get_raw_record(i):
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        assert f.raw_record(i)
