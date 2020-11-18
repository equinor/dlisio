import pytest
import dlisio

def assure_load(fpath, expected_logical_files_number = 2):
    with dlisio.load(fpath) as batch:
        for f in batch:
            f.load()
        assert len(batch) == expected_logical_files_number

def test_template_1():
    fpath = 'data/tif/templates/1.dlis'
    assure_load(fpath)


def test_template_2():
    fpath = 'data/tif/templates/2.dlis'
    assure_load(fpath)

def test_template_3():
    fpath = 'data/tif/templates/3.dlis'
    assure_load(fpath)

def test_template_4():
    fpath = 'data/tif/templates/4.dlis'
    assure_load(fpath)

def test_template_5():
    fpath = 'data/tif/templates/5.dlis'
    assure_load(fpath)

def test_template_6():
    fpath = 'data/tif/templates/6.dlis'
    assure_load(fpath)

def test_template_7():
    fpath = 'data/tif/templates/7.dlis'
    assure_load(fpath)

def test_template_8():
    fpath = 'data/tif/templates/8.dlis'
    assure_load(fpath)

def test_template_9():
    fpath = 'data/tif/templates/9.dlis'
    assure_load(fpath)

def test_template_inconsistency():
    fpath = 'data/tif/templates/inconsistency.dlis'
    assure_load(fpath)

@pytest.mark.xfail
def test_template_misalignment():
    fpath = 'data/tif/irregular/misalignment.dlis'
    assure_load(fpath)

@pytest.mark.xfail
def test_template_padding():
    fpath = 'data/tif/irregular/padding.dlis'
    assure_load(fpath)

@pytest.mark.xfail
def test_template_suls():
    fpath = 'data/tif/irregular/suls.dlis'
    assure_load(fpath)

def test_layout_LR_aligned():
    fpath = 'data/tif/layout/LR-aligned.dlis'
    assure_load(fpath, 1)

def test_layout_LR_disaligned():
    fpath = 'data/tif/layout/LR-disaligned.dlis'
    assure_load(fpath, 1)

@pytest.mark.xfail
def test_layout_FF01():
    fpath = 'data/tif/layout/FF01.dlis'
    assure_load(fpath, 1)

def test_layout_fdata_aligned():
    fpath = 'data/tif/layout/fdata-aligned.dlis'
    with dlisio.load(fpath) as (f, *_):
        f.load()
        frame = f.object('FRAME', 'FRAME-REPRCODE', 10, 0)
        curves = frame.curves()
        assert len(curves) == 1

def test_layout_fdata_disaligned():
    fpath = 'data/tif/layout/fdata-disaligned.dlis'
    with dlisio.load(fpath) as (f, *_):
        f.load()
        frame = f.object('FRAME', 'FRAME-REPRCODE', 10, 0)
        curves = frame.curves()
        assert len(curves) == 1

def test_layout_truncated_in_data():
    fpath = 'data/tif/layout/truncated-in-data.dlis'
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load(fpath)
    assert "findoffsets: file truncated" in str(excinfo.value)

def test_layout_truncated_in_header():
    fpath = 'data/tif/layout/truncated-in-header.dlis'
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load(fpath)
    assert "unexpected EOF" in str(excinfo.value)

def test_layout_truncated_after_header():
    fpath = 'data/tif/layout/truncated-after-header.dlis'
    with pytest.raises(RuntimeError) as excinfo:
        _ = dlisio.load(fpath)
    assert "unexpected EOF" in str(excinfo.value)
