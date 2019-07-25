import dlisio
import pytest
from . import DWL206

def test_sul(DWL206):
    label = ''.join([
                '   1',
                'V1.00',
                'RECORD',
                ' 8192',
                'Default Storage Set                                         ',
            ])

    sul = dlisio.core.storage_label(label.encode('ascii'))
    d = {
        'sequence': 1,
        'version': '1.0',
        'maxlen': 8192,
        'layout': 'record',
        'id': 'Default Storage Set                                         ',
    }

    assert sul == d

    assert DWL206.storage_label() == d


def test_sul_error_values():
    label = "too short"
    with pytest.raises(ValueError) as excinfo:
       dlisio.core.storage_label(label.encode('ascii'))
    assert 'buffer to small' in str(excinfo.value)

    label = ''.join([
                '   1',
                'V2.00',
                'RECORD',
                ' 8192',
                'Default Storage Set                                         ',
            ])

    with pytest.raises(ValueError) as excinfo:
        dlisio.core.storage_label(label.encode('ascii'))
    assert 'unable to parse' in str(excinfo.value)


    label = ''.join([
                '  2 ',
                'V1.00',
                'TRASH1',
                'ZZZZZ',
                'Default Storage Set                                         ',
    ])

    with pytest.warns(RuntimeWarning) as warninfo:
        sul = dlisio.core.storage_label(label.encode('ascii'))
    assert len(warninfo) == 1
    assert "label inconsistent" in warninfo[0].message.args[0]
    assert sul['layout'] == 'unknown'

def test_load_pre_sul_garbage():
    with dlisio.load('data/layout/pre-sul-garbage.dlis') as (f,):
        assert f.storage_label() == f.storage_label()
        assert f.sul_offset == 12

def test_load_pre_vrl_garbage():
    with dlisio.load('data/layout/pre-sul-pre-vrl-garbage.dlis') as (f,):
        assert f.storage_label() == f.storage_label()
        assert f.sul_offset == 12

def test_load_small_file():
    # <4K files infinite loop bug check
    with dlisio.load('data/layout/example-record.dlis'):
        pass

def test_load_7K_file_with_several_LR():
    # 4K-8K files infinite loop bug check
    with dlisio.load('data/layout/7K-file.dlis'):
        pass

def test_padbytes_as_large_as_record():
    # 180-byte long explicit record with padding, and padbytes are set to 180
    # (leaving the resulting len(data) == 0)
    try:
        f = dlisio.open('data/layout/padbytes-large-as-record.dlis')
        f.reindex([0], [180])

        rec = f.extract([0])[0]
        assert rec.explicit
        assert len(memoryview(rec)) == 0
    finally:
        f.close()

def test_padbytes_as_large_as_segment():
    # 180-byte long explicit record with padding, and padbytes are set to 176
    # record is expected to not be present
    try:
        f = dlisio.open('data/layout/padbytes-large-as-segment-body.dlis')
        f.reindex([0], [180])

        rec = f.extract([0])[0]
        assert len(memoryview(rec)) == 0
    finally:
        f.close()

