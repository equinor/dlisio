""" Test different file configurations/layouts w.r.t. TapeImageFormat and
padding. All tests/files contain the same LIS data, but with different
configurations of tapemarks and padding.

Please refer to data/lis/layouts/README.rst for what each file is designed to
test.
"""

from dlisio import lis, core, common
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

    errorhandler = common.ErrorHandler(
        critical=common.Actions.LOG_ERROR)

    with lis.load(fpath, errorhandler) as files:
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


@pytest.mark.parametrize('filename', [
    'attributes_01.lis',
    'attributes_02.lis',
    'attributes_03.lis',
])
def test_attributes(filename):
    # various present attributes shouldn't make a difference
    fpath = 'data/lis/layouts/' + filename
    assert_load_correctly(fpath, [Expected()])

@pytest.mark.xfail(strict=True, reason="No error or warning reported at the "
                                       "moment. Expected behavior undefined.")
@pytest.mark.parametrize('filename', [
    'attributes_04.lis',
    'attributes_05.lis',
])
def test_attributes_error(filename, assert_error):
    # checksum/parity error
    fpath = 'data/lis/layouts/' + filename
    lf = Expected(records=1, ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])
    assert_error("Attribute error") # or warning

def test_attributes_too_short(assert_error):
    # record is too short
    fpath = 'data/lis/layouts/attributes_06.lis'
    lf = Expected(records=1, ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])
    assert_error("Too short record length (was 6 bytes)")


def test_successor_00():
    # LRs are correctly divided into PRs
    fpath = 'data/lis/layouts/successor_00.lis'
    lf = Expected(records=3)
    assert_load_correctly(fpath, [lf])

@pytest.mark.parametrize('filename', [
    'data/lis/layouts/successor_01.lis',
    'data/lis/layouts/successor_02.lis',
    'data/lis/layouts/successor_03.lis',
    'data/lis/layouts/successor_04.lis',
])
def test_successor(filename, assert_error):
    lf = Expected(records=1, ttlr=None, rtlr=None)
    assert_load_correctly(filename, [lf])
    assert_error("predecessor/successor inconsistency")

tif_eof = 'tapeimage: unexpected EOF when reading record - '
@pytest.mark.parametrize('filename, specific_error',[
    ('truncated_01.lis', 'index_record: Missing next PRH'),
    ('truncated_02.lis', 'index_record: physical record truncated'),
    ('truncated_03.lis', 'index_record: physical record truncated'),
    ('truncated_04.lis', 'read_logical_header: could not read full header'),
    ('truncated_05.lis', 'read_logical_header: unexpected end-of-file'),
    ('truncated_06.lis', 'read_physical_header: unexpected end-of-file'),
    ('truncated_07.lis', 'index_record: Missing next PRH'),
    ('truncated_08.lis', tif_eof + 'got 0 bytes, expected there to be 1 more'),
    ('truncated_09.lis', tif_eof + 'got 0 bytes, expected there to be 1 more'),
    ('truncated_10.lis', tif_eof + 'got 1 bytes, expected there to be 47 more'),
    ('truncated_11.lis', tif_eof + 'got 0 bytes, expected there to be 48 more'),
    ('truncated_12.lis', tif_eof + 'got 2 bytes, expected there to be 50 more'),
    ('truncated_13.lis', tif_eof + 'got 0 bytes, expected there to be 52 more'),
    ('truncated_14.lis', 'tapeimage: unexpected EOF when reading header'),
    ('truncated_16.lis', 'index_record: Missing next PRH'),
])
def test_truncated(filename, assert_error, specific_error):
    # Truncation happens in various places of the data
    # problematic LF is still added to the logical files list
    # problematic PR is not stored
    fpath = 'data/lis/layouts/' + filename
    lf = Expected(records=1, ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])
    assert_error("Indexing stopped")
    assert_error(specific_error)

@pytest.mark.parametrize('filename', [
    'wrong_01.lis',
    'wrong_02.lis',
])
def test_wrong_not_lis(filename, assert_error):
    # not a LIS file
    fpath = 'data/lis/layouts/' + filename
    assert_load_correctly(fpath, [])
    assert_error("index_record: Missing next PRH")

@pytest.mark.xfail(strict=True, reason="Current behavior: File is loaded OK."
                                       "Expected behavior: undefined")
def test_wrong_zeroed(assert_error):
    # file is zeroed from certain point
    fpath = 'data/lis/layouts/wrong_03.lis'
    lf = Expected(records=1, ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])
    assert_error("Stopped indexing")

def test_wrong_TM(assert_error):
    # TM before File Trailer fails the prev < next check
    fpath = 'data/lis/layouts/wrong_04.lis'
    lf = Expected(records=1, ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])
    assert_error("file corrupt: head.next")

def test_wrong_LR_type(assert_error):
    # due to wrong PR length (real error) "LR" for the next "PR" has wrong type
    fpath = 'data/lis/layouts/wrong_05.lis'
    lf = Expected(records=1, ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])
    assert_error("Found invalid record type")

def test_wrong_TM_on_open(assert_error):
    # based on real error
    # due to wrong PR length next "PR" has type 80
    # file is TIFed, so rewind happens and next "logical file" is spoiled
    fpath = 'data/lis/layouts/wrong_06.lis'
    lf = Expected(records=1, ttlr=None, rtlr=None)
    assert_load_correctly(fpath, [lf])
    assert_error("lis::open: Cannot open lis::iodevice (ptell=206)")
