"""
Testing that curves methods correctly reads values with various
representation codes
"""
import pytest
import numpy as np
import sys
from datetime import datetime

from dlisio import dlis

def load_curves(fpath):
    with dlis.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-REPRCODE', 10, 0)
        curves = frame.curves()
        return curves

def test_fshort():
    fpath = 'data/chap4-7/iflr/reprcodes/01-fshort.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == -1

def test_fsingl():
    fpath = 'data/chap4-7/iflr/reprcodes/02-fsingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 5.5

def test_fsing1():
    fpath = 'data/chap4-7/iflr/reprcodes/03-fsing1.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (-2, 2)

def test_fsing2():
    fpath = 'data/chap4-7/iflr/reprcodes/04-fsing2.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (117, -13.25, 32444)

def test_isingl():
    fpath = 'data/chap4-7/iflr/reprcodes/05-isingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == -12

def test_vsingl():
    fpath = 'data/chap4-7/iflr/reprcodes/06-vsingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 0.125

def test_fdoubl():
    fpath = 'data/chap4-7/iflr/reprcodes/07-fdoubl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 900000000000000.5

def test_fdoub1():
    fpath = 'data/chap4-7/iflr/reprcodes/08-fdoub1.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (-13.5, -27670)

def test_fdoub2():
    fpath = 'data/chap4-7/iflr/reprcodes/09-fdoub2.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (6728332223, -45.75, -0.0625)

def test_csingl():
    fpath = 'data/chap4-7/iflr/reprcodes/10-csingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == complex(93, -14)

def test_cdoubl():
    fpath = 'data/chap4-7/iflr/reprcodes/11-cdoubl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == complex(125533556, -4.75)

def test_sshort():
    fpath = 'data/chap4-7/iflr/reprcodes/12-sshort.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 89

def test_snorm():
    fpath = 'data/chap4-7/iflr/reprcodes/13-snorm.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == -153

def test_slong():
    fpath = 'data/chap4-7/iflr/reprcodes/14-slong.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 2147483647

def test_ushort():
    fpath = 'data/chap4-7/iflr/reprcodes/15-ushort.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 6

def test_unorm():
    fpath = 'data/chap4-7/iflr/reprcodes/16-unorm.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 32921

def test_ulong():
    fpath = 'data/chap4-7/iflr/reprcodes/17-ulong.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 1

def test_uvari():
    fpath = 'data/chap4-7/iflr/reprcodes/18-uvari.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 257

def test_ident():
    fpath = 'data/chap4-7/iflr/reprcodes/19-ident.dlis'
    curves = load_curves(fpath)
    # The backing C++ code heavily relies on the size of the string in bytes
    # being 255 * uint32, so make it an extra assert.
    #
    # If this test fails it's probably because of wrong platform assumptions,
    # unicode representation or similar issues, and implies revising the fdata
    # parsing logic.
    #
    # the +4 is the size of the frameno
    assert curves[0].dtype.itemsize == 4 + 255 * 4
    assert curves[0][1] == 'VALUE'

def test_ascii():
    # The backing C++ heavily relies on objects (in this case str) being
    # written to the array as just a pointer, because we're writing a new
    # pointer into the appropriate offset
    #
    # the +4 is the size of the frameno
    import ctypes
    dtype = np.dtype(object)
    assert dtype.itemsize == ctypes.sizeof(ctypes.c_void_p())

    fpath = 'data/chap4-7/iflr/reprcodes/20-ascii.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 'Thou shalt not kill'
    assert curves[0].dtype.itemsize == dtype.itemsize + 4

def test_dtime():
    fpath = 'data/chap4-7/iflr/reprcodes/21-dtime.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == datetime(1971, 3, 21, 18, 4, 14, 386000)

def test_origin():
    fpath = 'data/chap4-7/iflr/reprcodes/22-origin.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 16777217

def test_obname():
    fpath = 'data/chap4-7/iflr/reprcodes/23-obname.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (18, 5, 'OBNAME_I')

def test_objref():
    fpath = 'data/chap4-7/iflr/reprcodes/24-objref.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == ('OBJREF_I', (25, 3, 'OBJREF_OBNAME'))

def test_attref():
    fpath = 'data/chap4-7/iflr/reprcodes/25-attref.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == ('FIRST_INDENT',
                            (3, 2, 'ATTREF_OBNAME'),
                            'SECOND_INDENT')

def test_status():
    fpath = 'data/chap4-7/iflr/reprcodes/26-status.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == True

def test_units():
    fpath = 'data/chap4-7/iflr/reprcodes/27-units.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 'unit'


def test_fshort_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/01-fshort.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == -1
    assert curves[1][1] == 153

def test_fsingl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/02-fsingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 5.5
    assert curves[1][1] == -13.75

def test_fsing1_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/03-fsing1.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (-2, 2)
    assert curves[1][1] == (-2, 3.5)

def test_fsing2_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/04-fsing2.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (117, -13.25, 32444)
    assert curves[1][1] == (3524454, 10, 20)

def test_isingl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/05-isingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == -12
    assert curves[1][1] == 65536.5

def test_vsingl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/06-vsingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 0.125
    assert curves[1][1] == -21.25

def test_fdoubl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/07-fdoubl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 900000000000000.5
    assert curves[1][1] == -153

def test_fdoub1_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/08-fdoub1.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (-13.5, -27670)
    assert curves[1][1] == (5673345, 14)

def test_fdoub2_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/09-fdoub2.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (6728332223, -45.75, -0.0625)
    assert curves[1][1] == (95637722454, 20, 5)

def test_csingl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/10-csingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == complex(93, -14)
    assert curves[1][1] == complex(67, -37)

def test_cdoubl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/11-cdoubl.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == complex(125533556, -4.75)
    assert curves[1][1] == complex(67, -37)

def test_sshort_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/12-sshort.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 89
    assert curves[1][1] == -89

def test_snorm_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/13-snorm.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == -153
    assert curves[1][1] == 153

def test_slong_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/14-slong.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 2147483647
    assert curves[1][1] == -153

def test_ushort_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/15-ushort.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 6
    assert curves[1][1] == 217

def test_unorm_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/16-unorm.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 32921
    assert curves[1][1] == 256

def test_ulong_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/17-ulong.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 1
    assert curves[1][1] == 4294967143

def test_uvari_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/18-uvari.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 257
    assert curves[1][1] == 65536

def test_ident_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/19-ident.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == "VALUE"
    assert curves[1][1] == "SECOND-VALUE"

def test_ascii_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/20-ascii.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == "Theory of mind"
    assert curves[1][1] == "this looks terrible"

def test_dtime_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/21-dtime.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == datetime(1971, 3, 21, 18, 4, 14, 386000)
    assert curves[1][1] == datetime(1970, 3, 21, 18, 4, 14, 0)

def test_origin_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/22-origin.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == 16777217
    assert curves[1][1] == 3

def test_obname_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/23-obname.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == (18, 5, "OBNAME_I")
    assert curves[1][1] == (18, 5, "OBNAME_K")

def test_objref_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/24-objref.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == ("OBJREF_I", (25, 3, "OBJREF_OBNAME"))
    assert curves[1][1] == ("OBJREF_I", (25, 4, "OBJREF_OBNAME"))

def test_attref_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/25-attref.dlis'
    curves = load_curves(fpath)
    ex1_attref = ("FIRST_INDENT", (3, 2, "ATTREF_OBNAME"), "SECOND_INDENT")
    ex2_attref = ("FIRST_INDENT", (9, 2, "ATTREF_OBNAME"), "SECOND_INDENT")
    assert curves[0][1] == ex1_attref
    assert curves[1][1] == ex2_attref

def test_status_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/26-status.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == True
    assert curves[1][1] == False

def test_units_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/27-units.dlis'
    curves = load_curves(fpath)
    assert curves[0][1] == "unit"
    assert curves[1][1] == "unit2"

def test_all_reprcodes():
    fpath = 'data/chap4-7/iflr/all-reprcodes.dlis'
    curves = load_curves(fpath)
    c = curves[0]
    assert c[0]  == 1
    assert c[1]  == -1.0
    assert c[2]  == 5.5
    assert c[3]  == (-2, 2)
    assert c[4]  == (117, -13.25, 32444)
    assert c[5]  == -12
    assert c[6]  == 0.125
    assert c[7]  == 900000000000000.5
    assert c[8]  == (-13.5, -27670)
    assert c[9]  == (6728332223, -45.75, -0.0625)
    assert c[10] == complex(93, -14)
    assert c[11] == complex(125533556, -4.75)
    assert c[12] == 89
    assert c[13] == -153
    assert c[14] == 2147483647
    assert c[15] == 6
    assert c[16] == 32921
    assert c[17] == 1
    assert c[18] == 257
    assert c[19] == "VALUE"
    assert c[20] == "ASCII VALUE"
    assert c[21] == datetime(1971, 3, 21, 18, 4, 14, 386000)
    assert c[22] == 16777217
    assert c[23] == (18, 5, "OBNAME_I")
    assert c[24] == ("OBJREF_I", (25, 3, "OBJREF_OBNAME"))
    assert c[25] == ("FIRST_INDENT", (3, 2, "ATTREF_OBNAME"), "SECOND_INDENT")
    assert c[26] == True
    assert c[27] == "unit"

def test_ascii_big():
    fpath = 'data/chap4-7/iflr/big-ascii.dlis'
    curves = load_curves(fpath)
    assert 'Maecenas vulputate est.' in curves[0][1]
    assert len(curves[0][1]) == 2004

@pytest.mark.skip(reason="SIGSEGV due to reading outside of memory")
def test_ascii_broken():
    fpath = 'data/chap4-7/iflr/broken-ascii.dlis'
    with pytest.raises(RuntimeError) as exc:
        _ = load_curves(fpath)
    assert "fmtstr would read past end" in str(exc)

@pytest.mark.xfail(strict=True)
def test_ascii_broken_utf8():
    fpath = 'data/chap4-7/iflr/broken-utf8-ascii.dlis'
    _ = load_curves(fpath)

def test_datetime_invalid():
    fpath = 'data/chap4-7/iflr/invalid-dtime.dlis'
    # run this test from python 3.6 only as code doesn't fail on python 3.5
    # check might be removed once we remove support for python 3.5
    if sys.version_info.major >= 3 and sys.version_info.minor > 5:
        with pytest.raises(RuntimeError) as excinfo:
            _ = load_curves(fpath)
        assert "ValueError: day is out of range for month" in str(excinfo.value)

def test_fmt_broken():
    fpath = 'data/chap4-7/iflr/broken-fmt.dlis'
    with pytest.raises(RuntimeError) as exc:
        _ = load_curves(fpath)
    assert "fmtstr would read past end" in str(exc.value)
