import dlisio
import pytest

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

def test_notdlis():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/layout/nondlis.txt')
    assert "could not find storage label" in str(excinfo.value)

def test_broken_sul():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/layout/incomplete-sul.dlis')
    assert "file may be corrupted" in str(excinfo.value)

def test_load_pre_vrl_garbage():
    with dlisio.load('data/layout/pre-sul-pre-vrl-garbage.dlis') as (f,):
        assert f.storage_label() == f.storage_label()
        assert f.sul_offset == 12

def test_old_vrs():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/layout/old-vr.dlis')
    assert "could not find visible record" in str(excinfo.value)

def test_broken_vr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/layout/incomplete-vr.dlis')
    assert "file may be corrupted" in str(excinfo.value)

def test_load_small_file():
    # <4K files infinite loop bug check
    with dlisio.load('data/layout/small.dlis'):
        pass

def test_load_7K_file_with_several_LR():
    # 4K-8K files infinite loop bug check
    with dlisio.load('data/layout/7K-file.dlis'):
        pass

def test_truncated():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/layout/truncated.dlis')
    assert "file truncated" in str(excinfo.value)

def test_too_small_record():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/layout/too-small-record.dlis')
    assert "in record 0 corrupted" in str(excinfo.value)

def test_padbytes_as_large_as_record():
    # 180-byte long explicit record with padding, and padbytes are set to 180
    # (leaving the resulting len(data) == 0)
    f = dlisio.open('data/layout/padbytes-large-as-record.dlis')
    try:
        f.reindex([0], [180])

        rec = f.extract([0])[0]
        assert rec.explicit
        assert len(memoryview(rec)) == 0
    finally:
        f.close()

def test_padbytes_as_large_as_segment():
    # 180-byte long explicit record with padding, and padbytes are set to 176
    # record is expected to not be present
    f = dlisio.open('data/layout/padbytes-large-as-segment-body.dlis')
    try:
        f.reindex([0], [180])

        rec = f.extract([0])[0]
        assert len(memoryview(rec)) == 0
    finally:
        f.close()

def test_bad_padbytes():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/layout/padbytes-bad.dlis')
    assert "bad segment trim" in str(excinfo.value)

def test_padbytes_encrypted():
    with dlisio.load('data/layout/padbytes-encrypted.dlis'):
        pass

def test_load_fdata_VR_aligned():
    with dlisio.load('data/layout/fdata-vr-aligned.dlis') as (f, *_):
        assert len(f.fdata_index) == 1
        assert f.fdata_index['T.FRAME-I.DLIS-FRAME-O.3-C.1'] == [0]

def test_load_fdata_many_in_same_VR():
    with dlisio.load('data/layout/fdata-many-in-same-vr.dlis') as (f, *_):
        assert len(f.fdata_index) == 2
        assert f.fdata_index['T.FRAME-I.DLIS-FRAME-O.3-C.1'] == [0, 1]
        ident = '3'*255
        fingerprint = 'T.FRAME-I.'+ident+'-O.1073741823-C.255'
        assert f.fdata_index[fingerprint] == [3]

def test_3lrs_in_lr_in_vr():
    with dlisio.load('data/layout/example-record.dlis'):
        pass

def test_2_lr_in_vr():
    with dlisio.load('data/layout/2lr-in-vr.dlis'):
        pass

def test_lr_in_2vrs():
    with dlisio.load('data/layout/lr-in-2vrs.dlis'):
        pass

def test_vrl_and_lrsh_mismatch():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load('data/layout/wrong-lrhs.dlis')
    assert "visible record/segment inconsistency" in str(excinfo.value)
