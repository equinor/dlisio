import pytest
import numpy as np
from datetime import datetime

import dlisio

def load_curves(fpath):
    with dlisio.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-REPRCODE', 10, 0)
        curves = frame.curves()
        return curves

def test_fshort():
    fpath = 'data/chap4-7/iflr/reprcodes/01-fshort.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == -1

def test_fsingl():
    fpath = 'data/chap4-7/iflr/reprcodes/02-fsingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 5.5

def test_fsing1():
    fpath = 'data/chap4-7/iflr/reprcodes/03-fsing1.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (-2, 2)

def test_fsing2():
    fpath = 'data/chap4-7/iflr/reprcodes/04-fsing2.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (117, -13.25, 32444)

def test_isingl():
    fpath = 'data/chap4-7/iflr/reprcodes/05-isingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == -12

def test_vsingl():
    fpath = 'data/chap4-7/iflr/reprcodes/06-vsingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 0.125

def test_fdoubl():
    fpath = 'data/chap4-7/iflr/reprcodes/07-fdoubl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 900000000000000.5

def test_fdoub1():
    fpath = 'data/chap4-7/iflr/reprcodes/08-fdoub1.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (-13.5, -27670)

def test_fdoub2():
    fpath = 'data/chap4-7/iflr/reprcodes/09-fdoub2.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (6728332223, -45.75, -0.0625)

def test_csingl():
    fpath = 'data/chap4-7/iflr/reprcodes/10-csingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == complex(93, -14)

def test_cdoubl():
    fpath = 'data/chap4-7/iflr/reprcodes/11-cdoubl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == complex(125533556, -4.75)

def test_sshort():
    fpath = 'data/chap4-7/iflr/reprcodes/12-sshort.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 89

def test_snorm():
    fpath = 'data/chap4-7/iflr/reprcodes/13-snorm.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == -153

def test_slong():
    fpath = 'data/chap4-7/iflr/reprcodes/14-slong.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 2147483647

def test_ushort():
    fpath = 'data/chap4-7/iflr/reprcodes/15-ushort.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 6

def test_unorm():
    fpath = 'data/chap4-7/iflr/reprcodes/16-unorm.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 32921

def test_ulong():
    fpath = 'data/chap4-7/iflr/reprcodes/17-ulong.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 1

def test_uvari():
    fpath = 'data/chap4-7/iflr/reprcodes/18-uvari.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 257

def test_ident():
    fpath = 'data/chap4-7/iflr/reprcodes/19-ident.dlis'
    curves = load_curves(fpath)
    # The backing C++ code heavily relies on the size of the string in bytes
    # being 255 * uint32, so make it an extra assert.
    #
    # If this test fails it's probably because of wrong platform assumptions,
    # unicode representation or similar issues, and implies revising the fdata
    # parsing logic.
    assert curves[0].dtype.itemsize == 255 * 4
    assert curves[0][0] == 'VALUE'

def test_ascii():
    # The backing C++ heavily relies on objects (in this case str) being
    # written to the array as just a pointer, because we're writing a new
    # pointer into the appropriate offset
    import ctypes
    dtype = np.dtype(object)
    assert dtype.itemsize == ctypes.sizeof(ctypes.c_void_p())

    fpath = 'data/chap4-7/iflr/reprcodes/20-ascii.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 'Thou shalt not kill'
    assert curves[0].dtype.itemsize == dtype.itemsize

def test_dtime():
    fpath = 'data/chap4-7/iflr/reprcodes/21-dtime.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == datetime(1971, 3, 21, 18, 4, 14, 386000)

def test_origin():
    fpath = 'data/chap4-7/iflr/reprcodes/22-origin.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 16777217

def test_obname():
    fpath = 'data/chap4-7/iflr/reprcodes/23-obname.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (18, 5, 'OBNAME_I')

def test_objref():
    fpath = 'data/chap4-7/iflr/reprcodes/24-objref.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == ('OBJREF_I', (25, 3, 'OBJREF_OBNAME'))

def test_attref():
    fpath = 'data/chap4-7/iflr/reprcodes/25-attref.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == ('FIRST_INDENT',
                            (3, 2, 'ATTREF_OBNAME'),
                            'SECOND_INDENT')

def test_status():
    fpath = 'data/chap4-7/iflr/reprcodes/26-status.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == True

def test_units():
    fpath = 'data/chap4-7/iflr/reprcodes/27-units.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 'unit'


@pytest.mark.xfail(strict=True)
def test_fshort_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/01-fshort.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == -1
    assert curves[1][0] == 153

@pytest.mark.xfail(strict=True)
def test_fsingl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/02-fsingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 5.5
    assert curves[1][0] == -13.75

@pytest.mark.xfail(strict=True)
def test_fsing1_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/03-fsing1.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (-2, 2)
    assert curves[1][0] == (-2, 3.5)

@pytest.mark.xfail(strict=True)
def test_fsing2_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/04-fsing2.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (117, -13.25, 32444)
    assert curves[1][0] == (3524454, 10, 20)

@pytest.mark.xfail(strict=True)
def test_isingl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/05-isingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == -12
    assert curves[1][0] == 65536.5

@pytest.mark.xfail(strict=True)
def test_vsingl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/06-vsingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 0.125
    assert curves[1][0] == -26.5

@pytest.mark.xfail(strict=True)
def test_fdoubl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/07-fdoubl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 900000000000000.5
    assert curves[1][0] == -153

@pytest.mark.xfail(strict=True)
def test_fdoub1_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/08-fdoub1.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (-13.5, -27670)
    assert curves[1][0] == (5673345, 14)

@pytest.mark.xfail(strict=True)
def test_fdoub2_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/09-fdoub2.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (6728332223, -45.75, -0.0625)
    assert curves[1][0] == (95637722454, 20, 5)

@pytest.mark.xfail(strict=True)
def test_csingl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/10-csingl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == complex(93, -14)
    assert curves[1][0] == complex(67, -37)

@pytest.mark.xfail(strict=True)
def test_cdoubl_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/11-cdoubl.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == complex(125533556, -4.75)
    assert curves[1][0] == complex(67, -37)

@pytest.mark.xfail(strict=True)
def test_sshort_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/12-sshort.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 89
    assert curves[1][0] == -89

@pytest.mark.xfail(strict=True)
def test_snorm_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/13-snorm.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == -153
    assert curves[1][0] == 153

@pytest.mark.xfail(strict=True)
def test_slong_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/14-slong.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 2147483647
    assert curves[1][0] == -153

@pytest.mark.xfail(strict=True)
def test_ushort_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/15-ushort.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 6
    assert curves[1][0] == 217

@pytest.mark.xfail(strict=True)
def test_unorm_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/16-unorm.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 32921
    assert curves[1][0] == 256

@pytest.mark.xfail(strict=True)
def test_ulong_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/17-ulong.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 1
    assert curves[1][0] == 4294967143

@pytest.mark.xfail(strict=True)
def test_uvari_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/18-uvari.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 257
    assert curves[1][0] == 65536

@pytest.mark.xfail(strict=True)
def test_ident_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/19-ident.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == "VALUE"
    assert curves[1][0] == "SECOND-VALUE"

@pytest.mark.xfail(strict=True)
def test_ascii_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/20-ascii.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == "Theory of mind"
    assert curves[1][0] == "this looks terrible"

@pytest.mark.xfail(strict=True)
def test_dtime_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/21-dtime.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == datetime(1971, 3, 21, 18, 4, 14, 386000)
    assert curves[1][0] == datetime(1970, 3, 21, 18, 4, 14, 0)

@pytest.mark.xfail(strict=True)
def test_origin_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/22-origin.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == 16777217
    assert curves[1][0] == 3

@pytest.mark.xfail(strict=True)
def test_obname_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/23-obname.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == (18, 5, "OBNAME_I")
    assert curves[1][0] == (18, 5, "OBNAME_K")

@pytest.mark.xfail(strict=True)
def test_objref_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/24-objref.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == ("OBJREF_I", (25, 3, "OBJREF_OBNAME"))
    assert curves[1][0] == ("OBJREF_I", (25, 4, "OBJREF_OBNAME"))

@pytest.mark.xfail(strict=True)
def test_attref_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/25-attref.dlis'
    curves = load_curves(fpath)
    ex1_attref = ("FIRST_INDENT", (3, 2, "ATTREF_OBNAME"), "SECOND_INDENT")
    ex2_attref = ("FIRST_INDENT", (9, 2, "ATTREF_OBNAME"), "SECOND_INDENT")
    assert curves[0][0] == ex1_attref
    assert curves[1][0] == ex2_attref

@pytest.mark.xfail(strict=True)
def test_status_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/26-status.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == True
    assert curves[1][0] == False

@pytest.mark.xfail(strict=True)
def test_units_x2():
    fpath = 'data/chap4-7/iflr/reprcodes-x2/27-units.dlis'
    curves = load_curves(fpath)
    assert curves[0][0] == "unit"
    assert curves[1][0] == "unit2"

@pytest.mark.xfail(strict=True)
def test_multiple_fdata_in_frame_has_correct_shape():
    # to enable more efficient resizing, larger-than-output temporaries can be
    # useful, but the *final array* must still be exactly as large as the
    # number-of-frames
    fpath = 'data/chap4-7/iflr/reprcodes-x2/27-units.dlis'
    curves = load_curves(fpath)
    assert curves.shape == (2,)

def test_all_reprcodes():
    fpath = 'data/chap4-7/iflr/all-reprcodes.dlis'
    curves = load_curves(fpath)
    c = curves[0]
    assert c[0]  == -1.0
    assert c[1]  == 5.5
    assert c[2]  == (-2, 2)
    assert c[3]  == (117, -13.25, 32444)
    assert c[4]  == -12
    assert c[5]  == 0.125
    assert c[6]  == 900000000000000.5
    assert c[7]  == (-13.5, -27670)
    assert c[8]  == (6728332223, -45.75, -0.0625)
    assert c[9]  == complex(93, -14)
    assert c[10] == complex(125533556, -4.75)
    assert c[11] == 89
    assert c[12] == -153
    assert c[13] == 2147483647
    assert c[14] == 6
    assert c[15] == 32921
    assert c[16] == 1
    assert c[17] == 257
    assert c[18] == "VALUE"
    assert c[19] == "ASCII VALUE"
    assert c[20] == datetime(1971, 3, 21, 18, 4, 14, 386000)
    assert c[21] == 16777217
    assert c[22] == (18, 5, "OBNAME_I")
    assert c[23] == ("OBJREF_I", (25, 3, "OBJREF_OBNAME"))
    assert c[24] == ("FIRST_INDENT", (3, 2, "ATTREF_OBNAME"), "SECOND_INDENT")
    assert c[25] == True
    assert c[26] == "unit"

def test_channel_curves():
    fpath = 'data/chap4-7/iflr/all-reprcodes.dlis'
    with dlisio.load(fpath) as (f, *_):
        channel = f.object('CHANNEL', 'CH26', 10, 0)
        curves = channel.curves()
        assert curves[0] == True

        channel = f.object('CHANNEL', 'CH22', 10, 0)
        curves = channel.curves()
        assert curves[0] == 16777217

def test_big_ascii():
    fpath = 'data/chap4-7/iflr/big-ascii.dlis'
    curves = load_curves(fpath)
    assert 'Maecenas vulputate est.' in curves[0][0]
    assert len(curves[0][0]) == 2004

@pytest.mark.skip(reason="SIGSEGV due to reading outside of memory")
def test_broken_ascii():
    fpath = 'data/chap4-7/iflr/broken-ascii.dlis'
    with pytest.raises(RuntimeError) as exc:
        _ = load_curves(fpath)
    assert "fmtstr would read past end" in str(exc)

@pytest.mark.xfail(strict=True)
def test_two_various_fdata_in_one_iflr():
    fpath = 'data/chap4-7/iflr/two-various-fdata-in-one-iflr.dlis'

    curves = load_curves(fpath)
    assert curves[0][0] == datetime(1971, 3, 21, 18, 4, 14, 386000)
    assert curves[0][1] == "VALUE"
    assert curves[0][2] == 89
    assert curves[1][0] == datetime(1970, 3, 21, 18, 4, 14, 0)
    assert curves[1][1] == "SECOND-VALUE"
    assert curves[1][2] == -89

@pytest.mark.xfail(strict=True)
def test_out_of_order_framenos_one_frame(assert_log):
    fpath = 'data/chap4-7/iflr/out-of-order-framenos-one-frame.dlis'

    curves = load_curves(fpath)
    assert curves[0][0] == False
    assert curves[1][0] == True

    assert_log("Non-sequential frames")

@pytest.mark.xfail(strict=True)
def test_out_of_order_framenos_two_frames(assert_log):
    fpath = 'data/chap4-7/iflr/out-of-order-framenos-two-frames.dlis'

    curves = load_curves(fpath)
    assert curves[0][0] == False
    assert curves[1][0] == True

    assert_log("Non-sequential frames")

@pytest.mark.xfail(strict=True)
def test_out_of_order_frames_two_framenos_multidata(assert_log):
    fpath = 'data/chap4-7/iflr/out-of-order-framenos-two-frames-multifdata.dlis'

    curves = load_curves(fpath)
    assert curves[0][0] == False
    assert curves[1][0] == True
    assert curves[2][0] == False
    assert curves[3][0] == True

    assert_log("Non-sequential frames")

@pytest.mark.xfail(strict=True)
def test_missing_numbers_frames(assert_log):
    fpath = 'data/chap4-7/iflr/missing-framenos.dlis'

    curves = load_curves(fpath)
    assert curves[0][0] == True
    assert curves[1][0] == False

    assert_log("Missing frames")

@pytest.mark.xfail(strict=True)
def test_duplicate_framenos(assert_log):
    fpath = 'data/chap4-7/iflr/duplicate-framenos.dlis'

    curves = load_curves(fpath)
    assert curves[0][0] == True
    assert curves[1][0] == False

    assert_log("Duplicated frames")


@pytest.mark.xfail(strict=True)
def test_duplicate_framenos_same_frames(assert_log):
    fpath = 'data/chap4-7/iflr/duplicate-framenos-same-frames.dlis'

    curves = load_curves(fpath)
    assert curves[0][0] == True
    assert curves[1][0] == True

    assert_log("Duplicated frames")

def test_fdata_dimension():
    fpath = 'data/chap4-7/iflr/multidimensions-ints-various.dlis'

    with dlisio.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-DIMENSION', 11, 0)
        curves = frame.curves()

        np.testing.assert_array_equal(curves[0][0], [[1, 2, 3], [4, 5, 6]])
        np.testing.assert_array_equal(curves[0][1], [[1, 2], [3, 4], [5, 6]])

        arr2 = [
            [[1, 2],   [3, 4],   [5, 6]],
            [[7, 8],   [9, 10],  [11, 12]],
            [[13, 14], [15, 16], [17, 18]],
            [[19, 20], [21, 22], [23, 24]]
        ]
        np.testing.assert_array_equal(curves[0][2], arr2)
        np.testing.assert_array_equal(curves[0][3], [[1, 2]])
        np.testing.assert_array_equal(curves[0][4], [[1], [2]])
        np.testing.assert_array_equal(curves[0][5], [[1]])
        np.testing.assert_array_equal(curves[0][6], [1, 2, 3, 4])

def test_fdata_tuple_dimension():
    fpath = 'data/chap4-7/iflr/multidimensions-validated.dlis'

    with dlisio.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-VALIDATE', 10, 0)
        curves = frame.curves()

        assert curves[0][0].size == 3

        assert curves[0][0][0] == (56, 0.0625, 0.0625)
        assert curves[0][0][1] == (43, 0.0625, 0.0625)
        assert curves[0][0][2] == (71, 0.5, 0.5)

@pytest.mark.xfail(strict=True)
def test_fdata_dimensions_in_multifdata():
    fpath = 'data/chap4-7/iflr/multidimensions-multifdata.dlis'

    with dlisio.load(fpath) as (f, *_):
        frame = f.object('FRAME', 'FRAME-DIMENSION', 11, 0)
        curves = frame.curves()

        np.testing.assert_array_equal(curves[0][0], [[1, 2, 3], [4, 5, 6]])
        np.testing.assert_array_equal(curves[1][0], [[7, 8, 9], [10, 11, 12]])
