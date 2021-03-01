"""
Testing lowest level of data representation - Chapter 2.
"""

import pytest

from dlisio import dlis, core

def test_load_small_file():
    # <4K files infinite loop bug check
    with dlis.load('data/chap2/small.dlis'):
        pass

def test_load_7K_file_with_several_LR():
    # 4K-8K files infinite loop bug check
    with dlis.load('data/chap2/7K-file.dlis'):
        pass

def test_load_file_ending_on_FF_01():
    with dlis.load('data/chap2/ends-on-FF-01.dlis'):
        pass

def test_3lrs_in_lr_in_vr():
    with dlis.load('data/chap2/3lrs-in-vr.dlis'):
        pass

def test_2_lr_in_vr():
    with dlis.load('data/chap2/2lr-in-vr.dlis'):
        pass

def test_lr_in_2vrs():
    with dlis.load('data/chap2/1lr-in-2vrs.dlis'):
        pass

def test_vrl_and_lrsh_mismatch():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/wrong-lrhs.dlis')
    assert "Problem:      rp66: Incorrect format version" in str(excinfo.value)

@pytest.mark.xfail(reason="We do not fail when attributes are inconsistent "
                          "between lrs of same lr, but maybe we should",
                   strict=True)
def test_lrs_atributes_inconsistency():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/attrs-inconsistency-type-pred.dlis')
    assert "inconsistency" in str(excinfo.value)

def test_logical_file_lrs_inconsistency():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/lf-lrs-inconsistency.dlis')
    msg = "logical file, but last logical record segment expects successor"
    assert msg in str(excinfo.value)

def test_padbytes_as_large_as_record(assert_info):
    path = 'data/chap2/padbytes-large-as-record.dlis'
    with dlis.load(path) as (f,):
        assert len(f.find('.*', '.*')) == 0
        assert len(f.fdata_index) == 0
        assert_info("= logical record segment length")

def test_padbytes_as_large_as_segment_explicit():
    path = 'data/chap2/padbytes-large-as-seg-explict.dlis'
    with dlis.load(path) as (f,):
        assert len(f.find('.*', '.*')) == 0
        assert len(f.fdata_index) == 0

def test_padbytes_as_large_as_segment_implicit():
    path = 'data/chap2/padbytes-large-as-seg-implicit.dlis'
    with dlis.load(path) as (f,):
        assert len(f.find('.*', '.*')) == 0
        assert len(f.fdata_index) == 0

def test_padbytes_bad():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/padbytes-bad.dlis')
    assert "bad segment trim" in str(excinfo.value)

def test_padbytes_encrypted():
    with dlis.load('data/chap2/padbytes-encrypted.dlis'):
        pass

def test_notdlis():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/nondlis.txt')
    assert "could not find visible record envelope" in str(excinfo.value)

def test_old_vrs():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/old-vr.dlis')
    assert "could not find visible record" in str(excinfo.value)

def test_broken_sul(assert_info):
    with dlis.load('data/chap2/incomplete-sul.dlis') as (f,):
        obj = f.object('RANDOM_SET3', 'RANDOM_OBJECT3')
        assert obj['RANDOM_ATTRIBUTE3'] == [3]

        assert f.storage_label() is None
    assert_info("found something that could be parts of a SUL")

def test_broken_vr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/incomplete-vr.dlis')
    assert "file may be corrupted" in str(excinfo.value)

def test_truncated_in_sul(assert_log):
    with dlis.load('data/chap2/truncated-in-sul.dlis') as files:
        pass
    assert len(files) == 0
    assert_log("SUL is expected to be 80 bytes, but was 32")

def test_truncated_in_iflr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/truncated-in-iflr.dlis')
    assert "File truncated in Logical Record Segment" in str(excinfo.value)

def test_truncated_in_second_lr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/truncated-in-second-lr.dlis')
    assert "File truncated in Logical Record Segment" in str(excinfo.value)

def test_truncated_in_lrsh():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/truncated-in-lrsh.dlis')
    assert "unexpected EOF when reading record" in str(excinfo.value)

def test_truncated_in_lrsh_vr_over():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/truncated-in-lrsh-vr-over.dlis')
    assert "File truncated in Logical Record Header" in str(excinfo.value)

def test_truncated_after_lrsh():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/truncated-after-lrsh.dlis')
    assert "File truncated in Logical Record Segment" in str(excinfo.value)

def test_truncated_lr_missing_lrs_in_vr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/truncated-lr-no-lrs-in-vr.dlis')
    assert "unexpected EOF when reading record" in str(excinfo.value)

def test_truncated_lr_missing_lrs_vr_over():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/truncated-lr-no-lrs-vr-over.dlis')
    msg = "last logical record segment expects successor"
    assert msg in str(excinfo.value)

def test_truncated_on_full_lr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/truncated-on-full-lr.dlis')
    assert "unexpected EOF when reading record" in str(excinfo.value)

def test_too_small_record():
    with dlis.load('data/chap2/too-small-record.dlis') as (f,):
        obj = f.object('VALID-SET', 'VALID-OBJ')
        assert obj['PARAM'] == ['PARAM-VALUE']

def test_zeroed_in_1st_lr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/zeroed-in-1st-lr.dlis')
    assert "Too short logical record" in str(excinfo.value)
    dbg = "Physical tell: 188 (dec), Logical Record tell: 100 (dec), " \
          "Logical Record Segment tell: 100 (dec)"
    assert dbg in str(excinfo.value)

def test_zeroed_in_2nd_lr():
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlis.load('data/chap2/zeroed-in-2nd-lr.dlis')
    # message propagated from lfp
    assert "Problem:      rp66: Incorrect format version" in str(excinfo.value)

def test_sul():
    label = ''.join([
                '   1',
                'V1.00',
                'RECORD',
                ' 8192',
                'Default Storage Set                                         ',
            ])

    sul = core.storage_label(label.encode('ascii'))
    d = {
        'sequence': 1,
        'version': '1.0',
        'maxlen': 8192,
        'layout': 'record',
        'id': 'Default Storage Set                                         ',
    }

    assert sul == d

    with dlis.load('data/chap2/small.dlis') as (f, *_):
        assert f.storage_label() == d


def test_sul_error_values():
    label = "too short"
    with pytest.raises(ValueError) as excinfo:
       core.storage_label(label.encode('ascii'))
    assert 'buffer to small' in str(excinfo.value)

    label = ''.join([
                '   1',
                'V2.00',
                'RECORD',
                ' 8192',
                'Default Storage Set                                         ',
            ])

    with pytest.raises(ValueError) as excinfo:
        core.storage_label(label.encode('ascii'))
    assert 'unable to parse' in str(excinfo.value)


    label = ''.join([
                '  2 ',
                'V1.00',
                'TRASH1',
                'ZZZZZ',
                'Default Storage Set                                         ',
    ])

    with pytest.warns(RuntimeWarning) as warninfo:
        sul = core.storage_label(label.encode('ascii'))
    assert len(warninfo) == 1
    assert "label inconsistent" in warninfo[0].message.args[0]
    assert sul['layout'] == 'unknown'


def test_load_pre_sul_garbage(assert_info):
    d = {
        'sequence': 1,
        'version': '1.0',
        'maxlen': 8192,
        'layout': 'record',
        'id': 'Default Storage Set                                         ',
    }
    with dlis.load('data/chap2/pre-sul-garbage.dlis') as (f,):
        assert f.storage_label() == d
    assert_info("SUL found at ptell 12 (dec), but expected at 0")


def test_load_pre_vrl_garbage(assert_info):
    d = {
        'sequence': 1,
        'version': '1.0',
        'maxlen': 8192,
        'layout': 'record',
        'id': 'Default Storage Set                                         ',
    }
    with dlis.load('data/chap2/pre-sul-pre-vrl-garbage.dlis') as (f,):
        assert f.storage_label() == d
    assert_info("VR found at ptell 116 (dec), but expected at 92")

def test_load_missing_sul(assert_info):
    with dlis.load('data/chap2/missing-sul.dlis') as files:
        for f in files:
            assert f.storage_label() is None
    assert_info("Exactly one SUL is expected at the start of the file")
