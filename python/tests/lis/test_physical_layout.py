""" Test different file configurations/layouts w.r.t. TapeImageFormat and
padding. All tests/files contain the same LIS data, but with different
configurations of tapemarks and padding.

Please refer to data/lis/layouts/README.rst for what each file is designed to
test.
"""

from dlisio import lis, core
import pytest

class Expected:
    def __init__(self,
                 rhlr = core.lis_rectype.reel_header,
                 rtlr = core.lis_rectype.reel_trailer,
                 thlr = core.lis_rectype.tape_header,
                 ttlr = core.lis_rectype.tape_trailer,
                 records = 2,
                 ):
        self.rhlr = rhlr
        self.rtlr = rtlr
        self.thlr = thlr
        self.ttlr = ttlr
        self.records = records

def assert_load_correctly(fpath, expected):
    def assert_header_trailer(actual, expected):
        if expected:
            assert actual.info.type == expected
        else:
            assert actual == None

    with lis.load(fpath) as files:
        assert len(files) == len(expected)

        for i, f in enumerate(files):
            assert len(f.explicits()) == expected[i].records
            assert_header_trailer(f.reel.rawheader, expected[i].rhlr)
            assert_header_trailer(f.reel.rawtrailer, expected[i].rtlr)
            assert_header_trailer(f.tape.rawheader, expected[i].thlr)
            assert_header_trailer(f.tape.rawtrailer, expected[i].ttlr)


def test_layout_00():
    # standard non-tifed layout
    fpath = 'data/lis/layouts/layout_00.lis'
    assert_load_correctly(fpath, [Expected()])

def test_layout_01():
    # non-tifed file where some PRs have odd size
    fpath = 'data/lis/layouts/layout_01.lis'
    assert_load_correctly(fpath, [Expected()])


def test_layout_tif_00():
    # basic layout seen most often
    fpath = 'data/lis/layouts/layout_tif_00.lis'
    assert_load_correctly(fpath, [Expected()])

def test_layout_tif_01():
    # advanced layout with many reels
    fpath = 'data/lis/layouts/layout_tif_01.lis'
    assert_load_correctly(fpath,[Expected(), Expected(), Expected(), Expected()])

def test_layout_tif_02():
    # no TM(1) between files
    fpath = 'data/lis/layouts/layout_tif_02.lis'
    assert_load_correctly(fpath, [Expected()])

def test_layout_tif_03():
    # 3 TM(1)s at the end
    fpath = 'data/lis/layouts/layout_tif_03.lis'
    assert_load_correctly(fpath, [Expected()])

def test_layout_tif_04():
    # no TM(1)s at the end
    fpath = 'data/lis/layouts/layout_tif_04.lis'
    assert_load_correctly(fpath, [Expected()])

def test_layout_tif_05():
    # no TTLR/RTLR. 2 TM(1)s at the end
    fpath = 'data/lis/layouts/layout_tif_05.lis'
    lf = Expected(ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])

def test_layout_tif_06():
    # no TTLR/RTLR. 0 TM(1)s at the end
    fpath = 'data/lis/layouts/layout_tif_06.lis'
    lf = Expected(ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])

def test_layout_tif_07():
    # no TTLR/RTLR. 3 TM(1)s at the end
    fpath = 'data/lis/layouts/layout_tif_07.lis'
    lf = Expected(ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])

def test_layout_tif_08():
    # no TTLR/RTLR, next Reel follows.
    fpath = 'data/lis/layouts/layout_tif_08.lis'
    lf = Expected(ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf, Expected()])

def test_layout_tif_09():
    # no RTLR. 2 TM(1)s at the end
    fpath = 'data/lis/layouts/layout_tif_09.lis'
    lf = Expected(rtlr=None)
    assert_load_correctly(fpath, [lf])


def test_padding_01():
    # non-tifed file where some PR's sizes are not divisible by 4, no padding
    fpath = 'data/lis/layouts/padding_01.lis'
    assert_load_correctly(fpath, [Expected()])

def test_padding_02():
    # tifed file where some PR's sizes are not divisible by 4, no padding
    fpath = 'data/lis/layouts/padding_02.lis'
    assert_load_correctly(fpath, [Expected()])

def test_padding_03():
    # valid 00 padding to assure minimal record length
    fpath = 'data/lis/layouts/padding_03.lis'
    assert_load_correctly(fpath, [Expected()])

def test_padding_04():
    # 00 padding of some PRs to assure PR size % 4 = 0
    fpath = 'data/lis/layouts/padding_04.lis'
    assert_load_correctly(fpath, [Expected()])

@pytest.mark.xfail(strict=True)
def test_padding_05():
    # non-00 padding of some PRs to assure PR size % 4 = 0
    fpath = 'data/lis/layouts/padding_05.lis'
    assert_load_correctly(fpath, [Expected()])

def test_padding_06():
    # padding at the very end - 00
    fpath = 'data/lis/layouts/padding_06.lis'
    assert_load_correctly(fpath, [Expected()])


