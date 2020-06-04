"""
Testing lowest level of data representation - Chapter 2.
"""

import dlisio
import pytest

from dlisio import core

def test_load_small_file():
    # <4K files infinite loop bug check
    with dlisio.load('data/chap2/small.dlis'):
        pass

def test_load_7K_file_with_several_LR():
    # 4K-8K files infinite loop bug check
    with dlisio.load('data/chap2/7K-file.dlis'):
        pass

def test_3lrs_in_lr_in_vr():
    with dlisio.load('data/chap2/3lrs-in-vr.dlis'):
        pass

def test_2_lr_in_vr():
    with dlisio.load('data/chap2/2lr-in-vr.dlis'):
        pass

def test_lr_in_2vrs():
    with dlisio.load('data/chap2/1lr-in-2vrs.dlis'):
        pass

def test_vrl_and_lrsh_mismatch():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/wrong-lrhs.dlis')
    assert "Incorrect format version" in str(excinfo.value)

@pytest.mark.xfail(reason="We do not fail when attributes are inconsistent "
                          "between lrs of same lr, but maybe we should",
                   strict=True)
def test_lrs_atributes_inconsistency():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/attrs-inconsistency-type-pred.dlis')
    assert "inconsistency" in str(excinfo.value)

def test_padbytes_as_large_as_record():
    # 180-byte long explicit record with padding, and padbytes are set to 180
    # (leaving the resulting len(data) == 0)
    f = dlisio.open('data/chap2/padbytes-large-as-record.dlis')
    try:
        rec = core.extract(f, [0])[0]
        assert rec.explicit
        assert len(memoryview(rec)) == 0
    finally:
        f.close()

def test_padbytes_as_large_as_segment():
    # 180-byte long explicit record with padding, and padbytes are set to 176
    # record is expected to not be present
    f = dlisio.open('data/chap2/padbytes-large-as-segment-body.dlis')
    try:
        rec = core.extract(f, [0])[0]
        assert len(memoryview(rec)) == 0
    finally:
        f.close()

def test_padbytes_bad():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/padbytes-bad.dlis')
    assert "bad segment trim" in str(excinfo.value)

def test_padbytes_encrypted():
    with dlisio.load('data/chap2/padbytes-encrypted.dlis'):
        pass

def test_notdlis():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/nondlis.txt')
    assert "could not find visible record envelope" in str(excinfo.value)

def test_old_vrs():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/old-vr.dlis')
    assert "could not find visible record" in str(excinfo.value)

def test_broken_sul():
    with dlisio.load('data/chap2/incomplete-sul.dlis') as (f,):
        obj = f.object('RANDOM_SET3', 'RANDOM_OBJECT3')
        assert obj['RANDOM_ATTRIBUTE3'] == [3]

        assert f.storage_label() is None

def test_broken_vr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/incomplete-vr.dlis')
    assert "file may be corrupted" in str(excinfo.value)

def test_truncated_in_second_lr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/truncated-in-second-lr.dlis')
    assert "unexpected EOF when reading record" in str(excinfo.value)

def test_truncated_in_lrsh():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/truncated-in-lrsh.dlis')
    assert "unexpected EOF when reading record" in str(excinfo.value)

def test_truncated_on_lrs():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/truncated-on-lrs.dlis')
    assert "unexpected EOF when reading record" in str(excinfo.value)

def test_truncated_on_full_lr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/chap2/truncated-on-full-lr.dlis')
    assert "unexpected EOF when reading record" in str(excinfo.value)

def test_too_small_record():
    with dlisio.load('data/chap2/too-small-record.dlis') as (f,):
        obj = f.object('VALID-SET', 'VALID-OBJ')
        assert obj['PARAM'] == ['PARAM-VALUE']

def test_sul():
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

    with dlisio.load('data/chap2/small.dlis') as (f, *_):
        assert f.storage_label() == d


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
    d = {
        'sequence': 1,
        'version': '1.0',
        'maxlen': 8192,
        'layout': 'record',
        'id': 'Default Storage Set                                         ',
    }
    with dlisio.load('data/chap2/pre-sul-garbage.dlis') as (f,):
        assert f.storage_label() == d


def test_load_pre_vrl_garbage():
    d = {
        'sequence': 1,
        'version': '1.0',
        'maxlen': 8192,
        'layout': 'record',
        'id': 'Default Storage Set                                         ',
    }
    with dlisio.load('data/chap2/pre-sul-pre-vrl-garbage.dlis') as (f,):
        assert f.storage_label() == d

def test_load_missing_sul():
    with dlisio.load('data/chap2/missing-sul.dlis') as files:
        for f in files:
            assert f.storage_label() is None
