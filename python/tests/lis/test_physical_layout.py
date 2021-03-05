from dlisio import lis, core

""" Test different file configurations/layouts w.r.t. TapeImageFormat and
padding. All tests/files contain the same LIS data, but with different
configurations of tapemarks and padding.

Please refer to data/lis/layouts/README.rst for what each file is designed to
test.
"""

def assert_load_correctly(fpath):
    with lis.load(fpath) as files:
        assert len(files) == 2

        for f in files:
            assert len(f.explicits()) == 2
            assert f.reel.rawheader.info.type  == core.lis_rectype.reel_header
            assert f.reel.rawtrailer.info.type == core.lis_rectype.reel_trailer
            assert f.tape.rawheader.info.type  == core.lis_rectype.tape_header
            assert f.tape.rawtrailer.info.type == core.lis_rectype.tape_trailer

def test_layout_tif_01():
    fpath = 'data/lis/layouts/layout_tif_01.lis'
    assert_load_correctly(fpath)

def test_layout_tif_02():
    fpath = 'data/lis/layouts/layout_tif_02.lis'
    assert_load_correctly(fpath)

def test_layout_tif_03():
    fpath = 'data/lis/layouts/layout_tif_03.lis'
    assert_load_correctly(fpath)

def test_layout_tif_04():
    fpath = 'data/lis/layouts/layout_tif_04.lis'
    assert_load_correctly(fpath)

def test_layout_tif_05():
    fpath = 'data/lis/layouts/layout_tif_05.lis'
    assert_load_correctly(fpath)

def test_layout_tif_06():
    fpath = 'data/lis/layouts/layout_tif_06.lis'
    assert_load_correctly(fpath)

def test_layout_tif_07():
    fpath = 'data/lis/layouts/layout_tif_07.lis'
    assert_load_correctly(fpath)

def test_layout_tif_08():
    fpath = 'data/lis/layouts/layout_tif_08.lis'
    assert_load_correctly(fpath)

def test_layout_tif_09():
    fpath = 'data/lis/layouts/layout_tif_09.lis'
    assert_load_correctly(fpath)

def test_broken_01():
    fpath = 'data/lis/layouts/broken_01.lis'
    assert_load_correctly(fpath)

def test_broken_02():
    fpath = 'data/lis/layouts/broken_02.lis'
    assert_load_correctly(fpath)

def test_broken_03(assert_error):
    fpath = 'data/lis/layouts/broken_03.lis'
    assert_load_correctly(fpath)
    assert_error('stopped indexing')

def test_broken_04(assert_error):
    """ The file only contains a RHLR and THLR, but with non-padbytes between
    the PR's. Indexing will fail on THLR, but with no LF, the RHLR is discarded
    too. Hence the test is reduced to checking that the issue is logged
    correctly.
    """
    fpath = 'data/lis/layouts/broken_04.lis'
    with lis.load(fpath) as files:
        assert len(files) == 0
    assert_error('File likely truncated')
