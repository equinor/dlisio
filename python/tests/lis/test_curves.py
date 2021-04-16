from dlisio import lis, core
import numpy as np
import os
import pytest

def test_dfsr_fmtstring():
    path = 'data/lis/MUD_LOG_1.LIS'

    with lis.load(path) as (lf, *tail):
        dfsr = lf.data_format_specs()[0]

        fmt = core.dfs_formatstring(dfsr)
        assert fmt == 'f' * 44

def test_dfsr_dtype():
    path = 'data/lis/MUD_LOG_1.LIS'

    with lis.load(path) as (lf, *tail):
        dfsr = lf.data_format_specs()[0]

        dtype = lis.dfsr_dtype(dfsr)

        expected = np.dtype([
            (ch.mnemonic, np.float32)
            for ch in dfsr.specs
        ])

        assert dtype == expected

def test_read_curves():
    path = 'data/lis/MUD_LOG_1.LIS'

    #TODO proper curves testing
    with lis.load(path) as (lf, *tail):
        dfs = lf.data_format_specs()[1]
        curves = lis.curves(lf, dfs)

        assert len(curves) == 3946

        ch = curves['DEPT'][0:5]
        expected = np.array([145.0, 146.0, 147.0, 148.0, 149.0])
        np.testing.assert_array_equal(expected, ch)

        ch = curves['BDIA'][0:5]
        expected = np.array([36.0, 36.0, 36.0, 36.0, 36.0])
        np.testing.assert_array_equal(expected, ch)


headers = [
    'data/lis/records/RHLR-1.lis.part',
    'data/lis/records/THLR-1.lis.part',
    'data/lis/records/FHLR-1.lis.part',
    ]

trailers = [
    'data/lis/records/FTLR-1.lis.part',
    'data/lis/records/TTLR-1.lis.part',
    'data/lis/records/RTLR-1.lis.part',
]


def test_entries(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'entries.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-entries-defined.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        assert len(dfs.entries) == 17

        # TODO: better interface, now user doesn't know what entries mean
        entries = {entry.type : entry.value for entry in dfs.entries}
        assert entries[0]  == 60
        assert entries[1]  == 0
        assert entries[2]  == 0
        assert entries[3]  == 32
        assert entries[4]  == 0 #"none"
        assert entries[5]  == 255 #"meters"
        assert entries[6]  == -4
        assert entries[7]  == "INCH"
        assert entries[8]  == 60
        assert entries[9]  == "INCH"
        assert entries[10] == "UNDEFINE" #field undefined, should be missing
        assert entries[11] == 8
        assert entries[12] == -15988.0
        assert entries[13] == 1 #True
        assert entries[14] == "INCH"
        assert entries[15] == 73 #reprc_int_32
        assert entries[16] == 1

@pytest.mark.xfail(strict=True, reason="default values not supported yet")
def test_entries_default_values(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'entries-default.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-entries-default.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        assert len(dfs.entries) == 17

        entries = {entry.type : entry.value for entry in dfs.entries}
        assert entries[0]  == 60
        assert entries[1]  == 0
        assert entries[2]  == 0
        assert entries[3]  == None
        assert entries[4]  == 1 #"up"
        assert entries[5]  == 1 #"feet"
        assert entries[6]  == None
        assert entries[7]  == ".1IN"
        assert entries[8]  == None
        assert entries[9]  == ".1IN"
        assert entries[10] == None #field undefined, should be missing
        assert entries[11] == None
        #assert entries[12] == -999.25 or None: unknown
        assert entries[13] == 0 #False
        assert entries[14] == ".1IN"
        assert entries[15] == None
        assert entries[16] == 0

def test_entries_cut_in_fixed():
    path = 'data/lis/records/curves/dfsr-entries-cut-fixed.lis.part'
    with lis.load(path) as (f,):
        with pytest.raises(RuntimeError) as exc:
            _ = f.data_format_specs()
        assert "2 bytes left in record, expected at least 3" in str(exc.value)

def test_entries_cut_in_value():
    path = 'data/lis/records/curves/dfsr-entries-cut-value.lis.part'
    with lis.load(path) as (f,):
        with pytest.raises(RuntimeError) as exc:
            _ = f.data_format_specs()
        assert "lis::entry_block: 6 bytes left in record" in str(exc.value)

def test_entries_cut_before_terminator():
    path = 'data/lis/records/curves/dfsr-entries-cut-end.lis.part'
    with lis.load(path) as (f,):
        with pytest.raises(RuntimeError) as exc:
            _ = f.data_format_specs()
        assert "0 bytes left in record, expected at least 3" in str(exc.value)

@pytest.mark.xfail(strict=True, reason="check missing")
def test_entries_invalid_type():
    path = 'data/lis/records/curves/dfsr-entries-bad-type.lis.part'
    with lis.load(path) as (f,):
        with pytest.raises(RuntimeError) as exc:
            _ = f.data_format_specs()
        assert "invalid type" in str(exc.value)

def test_entries_invalid_repcode():
    path = 'data/lis/records/curves/dfsr-entries-bad-reprc.lis.part'
    with lis.load(path) as (f,):
        with pytest.raises(RuntimeError) as exc:
            _ = f.data_format_specs()
        assert "unknown representation code 83" in str(exc.value)

#TODO:
# depending on where transformation is going to happen, next tests are needed
# in Python or in C++:
# - Terminator of 00 length (at the moment random value is returned to python)
# - UP/DOWN flag, Optical Log Scale Units, Depth mode values


def test_dfsr_subtype0(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dfsr-subtype0.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-subtype0.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        ch1 = dfs.specs[0]
        assert ch1.mnemonic == "CH01"
        assert ch1.service_id == "testCH"
        assert ch1.service_order_nr == "  1234  "
        assert ch1.units == "INCH"
        #assert ch1.api_codes == "45310011" #unsupported
        assert ch1.filenr == 1
        assert ch1.reserved_size == 4
        #assert ch1.process_level == "FF" #unsupported
        assert ch1.samples == 1
        assert ch1.reprc == 73 #should this be int32 instead?

        curves = lis.curves(f, dfs)
        assert len(curves) == 0

def test_dfsr_subtype1(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dfsr-subtype1.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-subtype1.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        ch1 = dfs.specs[0]
        assert ch1.mnemonic == "CH01"
        assert ch1.service_id == "testCH"
        assert ch1.service_order_nr == "  1234  "
        assert ch1.units == "INCH"
        #assert ch1.api_codes == "45310011" #unsupported
        assert ch1.filenr == 1
        assert ch1.reserved_size == 4
        assert ch1.samples == 1
        assert ch1.reprc == 73 #should this be int32 instead?
        #assert ch1.process_indicators == "FF FF FF FF FF" #unsupported

        curves = lis.curves(f, dfs)
        assert len(curves) == 0

def test_dfsr_cut():
    path = 'data/lis/records/curves/dfsr-cut.lis.part'
    with lis.load(path) as (f,):
        with pytest.raises(RuntimeError) as exc:
            _ = f.data_format_specs()
        assert "lis::spec_block: 32 bytes left in record" in str(exc.value)

def test_dfsr_many(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dfsr-many.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-simple.lis.part',
        'data/lis/records/curves/dfsr-simple.lis.part',
        'data/lis/records/curves/fdata-simple.lis.part',
        'data/lis/records/curves/dfsr-simple.lis.part',
        'data/lis/records/curves/dfsr-simple.lis.part',
        'data/lis/records/curves/fdata-simple.lis.part',
        'data/lis/records/curves/fdata-simple.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        assert len(lis.curves(f, f.data_format_specs()[0])) == 0
        assert len(lis.curves(f, f.data_format_specs()[1])) == 1
        assert len(lis.curves(f, f.data_format_specs()[2])) == 0
        assert len(lis.curves(f, f.data_format_specs()[3])) == 2

def test_dfsr_invalid_tell(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dfsr-prerequisites.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-simple.lis.part',
        'data/lis/records/curves/fdata-simple.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

    fpath = os.path.join(str(tmpdir), 'dfsr-invalid-tell.lis')

    content = headers + [
        'data/lis/records/curves/fdata-simple.lis.part',
        'data/lis/records/curves/fdata-simple.lis.part',
        'data/lis/records/curves/dfsr-simple.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
    assert "Could not find DFS record at tell" in str(exc.value)


def test_fdata_repcodes_fixed_size(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fdata-repcodes-fixed.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-repcodes-fixed.lis.part',
        'data/lis/records/curves/fdata-repcodes-fixed.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        fmt = core.dfs_formatstring(dfs)
        assert fmt == 'bsilefrp'

        curves = lis.curves(f, dfs)
        assert curves['BYTE'] == [89]
        assert curves['I8  '] == [-128]
        assert curves['I16 '] == [153]
        assert curves['I32 '] == [-153]
        assert curves['F16 '] == [1.0]
        assert curves['F32 '] == [-1.0]
        assert curves['F32L'] == [-0.25]
        assert curves['F32F'] == [153.25]

def test_fdata_repcodes_string(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fdata-repcodes-string.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-repcodes-string.lis.part',
        'data/lis/records/curves/fdata-repcodes-string.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        fmt = core.dfs_formatstring(dfs)
        assert fmt == 'a32'

        curves = lis.curves(f, dfs)
        assert curves['STR '] == "Now this is a string of size 32 "

def test_fdata_repcodes_mask(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fdata-repcodes-mask.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-repcodes-mask.lis.part',
        'data/lis/records/curves/fdata-repcodes-mask.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(NotImplementedError):
            fmt = core.dfs_formatstring(dfs)
            assert fmt == 'm'

        with pytest.raises(NotImplementedError):
            curves = lis.curves(f, dfs)
            assert curves['MASK'] == bytearray([0xFF, 0xFF, 0xFF, 0xFF])

def test_fdata_repcodes_invalid(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fdata-repcodes-invalid.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-repcodes-invalid.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Invalid repcode (170) in channel (WTF )" in str(exc.value)


@pytest.mark.xfail(strict=True)
def test_fdata_samples_0(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dfsr-samples-0.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-samples-0.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert "samples < 1 (was: 0)" in str(exc.value)


@pytest.mark.skip(reason="1, 3: infinite loop, 2: data read as 2 frames, "
                         "4: segmentation fault. Divide tests if needed")
@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-size-0-one-block.lis.part',
    'dfsr-size-0-two-blocks.lis.part',
    'dfsr-entries-default.lis.part',
    'dfsr-size-0-string.lis.part',
])
def test_fdata_size_0_one_channel(tmpdir, merge_lis_prs, dfsr_filename):
    fpath = os.path.join(str(tmpdir), 'dfsr-size-0.lis')

    content = headers + [
        'data/lis/records/curves/' + dfsr_filename,
        'data/lis/records/curves/fdata-size.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert "size == 0" in str(exc.value)

def test_fdata_size_less_than_repcode_size(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dfsr-size-lt-repcode-size.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-size-lt-repcode.lis.part',
        'data/lis/records/curves/fdata-size.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "number of entries from size (2) / repcode(73)" in str(exc.value)


# DEPTH:
# 1. placeholders. currently expected behavior may be changed on implementation
# 2. more tests needed if depth can be negative
# 3. might need test mode = 0, direction flag inconsistent with actual direction
# if we decide to implement any checks
# 4. Issues with inconsistent spacing and units: if depth units (14) != frame
# spacing units (9), we might have problems with defining inconsistency
# 5. Some information can be checked or deduced if certain entries are missing.
# Suggestion is to fail on all wrong or missing important information cases
# until we get the real file with these situations.

@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-depth-dir-down.lis.part',
    'dfsr-depth-reprc-size.lis.part',
    'dfsr-depth-spacing-no.lis.part', #put it into own test if not supported
])
def test_depth_mode_1_direction_down(tmpdir, merge_lis_prs, dfsr_filename):
    fpath = os.path.join(str(tmpdir), 'depth-dir-down.lis')

    content = headers + [
        'data/lis/records/curves/' + dfsr_filename,
        'data/lis/records/curves/fdata-depth-down-PR-2.lis.part',
        'data/lis/records/curves/fdata-depth-down-PR-1.lis.part',
        'data/lis/records/curves/fdata-depth-down-PR1.lis.part',
        'data/lis/records/curves/fdata-depth-down-PR2.lis.part',
        'data/lis/records/curves/fdata-depth-down-PR3.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        curves = lis.curves(f, dfs)
        assert curves['DEPT'] == [-3, -2, -1, 0, 1, 2, 3, 4, 5]
        assert curves['CH01'] == [12, 13, 14, 15, 16, 17, 18, 19, 20]

@pytest.mark.xfail(strict=True)
def test_depth_mode_1_direction_up(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'depth-dir-up.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-depth-dir-up.lis.part',
        'data/lis/records/curves/fdata-depth-up-PR1.lis.part',
        'data/lis/records/curves/fdata-depth-up-PR2.lis.part',
        'data/lis/records/curves/fdata-depth-up-PR3.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        curves = lis.curves(f, dfs)
        assert curves['DEPT'] == [53, 52, 51, 50, 49]
        assert curves['CH01'] == [37, 36, 35, 34, 33]

# unclear if we want to support something from here
@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-depth-dir-none.lis.part',
    'dfsr-depth-dir-invalid.lis.part',
    'dfsr-depth-dir-no.lis.part', #should we try to deduce direction from data?
])
def test_depth_mode_1_direction_bad(tmpdir, merge_lis_prs, dfsr_filename):
    fpath = os.path.join(str(tmpdir), 'depth-dir-bad.lis')

    content = headers + [
        'data/lis/records/curves/' + dfsr_filename,
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Direction flag incompatible with depth mode = 1" in str(exc.value)

# unclear if we want to check it. (If we do, depth mode 0 tests would be useful)
@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-depth-dir-down.lis.part',
    'dfsr-depth-dir-up.lis.part',
])
def test_depth_mode_1_direction_no_match(tmpdir, merge_lis_prs, dfsr_filename):
    fpath = os.path.join(str(tmpdir), 'depth-dir-no-data-match.lis')

    content = headers + [
        'data/lis/records/curves/' + dfsr_filename,
        'data/lis/records/curves/fdata-depth-up-PR1.lis.part',
        'data/lis/records/curves/fdata-depth-down-PR2.lis.part',
        'data/lis/records/curves/fdata-depth-up-PR3.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Declared direction doesn't match actual data" in str(exc.value)

# unclear if we want to check it and if that should count as failure or warning
@pytest.mark.xfail(strict=True)
def test_depth_mode_1_direction_inconsistent(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'depth-dir-inconsistent')

    content = headers + [
        'data/lis/records/curves/dfsr-depth-dir-down.lis.part',
        'data/lis/records/curves/fdata-depth-up-PR1.lis.part',
        'data/lis/records/curves/fdata-depth-up-PR2.lis.part',
        'data/lis/records/curves/fdata-depth-up-PR3.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Declared direction doesn't match actual data" in str(exc.value)

@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-depth-reprc-bad.lis.part',
    'dfsr-depth-reprc-none.lis.part',
])
def test_depth_mode_1_repcode_invalid(tmpdir, merge_lis_prs, dfsr_filename):
    fpath = os.path.join(str(tmpdir), 'depth-reprc-invalid.lis')

    content = headers + [
        'data/lis/records/curves/' + dfsr_filename,
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Depth reprc is invalid or missing." in str(exc.value)

@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-depth-dir-down.lis.part',
    'dfsr-depth-spacing-no.lis.part',
])
def test_depth_mode_1_spacing_inconsistent(tmpdir, merge_lis_prs, dfsr_filename):
    fpath = os.path.join(str(tmpdir), 'depth-spacing-inconsistent.lis')

    content = headers + [
        'data/lis/records/curves/' + dfsr_filename,
        'data/lis/records/curves/fdata-depth-down-PR1.lis.part',
        'data/lis/records/curves/fdata-depth-down-PR3.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Depth spacing is inconsistent." in str(exc.value)


@pytest.mark.xfail(strict=True)
def test_depth_mode_1_conversion(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'depth-int-float-conversion')

    content = headers + [
        'data/lis/records/curves/dfsr-depth-conversion.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Spacing is float, depth repcode is int" in str(exc.value)


def test_fdata_dimensional_ints(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dimensional-ints.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-dimensional-int.lis.part',
        'data/lis/records/curves/fdata-dimensional-int.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        curves = lis.curves(f, dfs)

        expected = np.array([[1, 2], [4, 5]])
        np.testing.assert_array_equal(expected, curves['CH01'])

        expected = np.array([3, 6])
        np.testing.assert_array_equal(expected, curves['CH02'])

# fdata - should we allow skipping broken channels for whatever reason?
# at the moment we do that for suppressed and fast channels, but not in case
# where samples=1, size>0
# while the situation is unlikely to arise in real world, it creates
# inconsistency
def test_fdata_dimensional_bad(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dimensional-bad.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-dimensional-bad.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Cannot compute an integral number of entries from size (5) / " \
               "repcode(79) for channel CH01" in str(exc.value)

@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-suppressed.lis.part',
    'dfsr-suppressed-bad.lis.part', #broken channels can be suppressed
])
def test_fdata_suppressed(tmpdir, merge_lis_prs, dfsr_filename):
    fpath = os.path.join(str(tmpdir), 'suppressed.lis')

    content = headers + [
        'data/lis/records/curves/' + dfsr_filename,
        'data/lis/records/curves/fdata-suppressed.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        curves = lis.curves(f, dfs)
        assert len(curves) == 1
        assert curves['CH01'] == [1]
        assert curves['CH03'] == [3]
        with pytest.raises(ValueError):
            _ = curves['CH02']
        with pytest.raises(ValueError):
            _ = curves['CH04']


@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-fast-int.lis.part',
    'dfsr-fast-int-bad.lis.part', #broken channel can be skipped if size matches
])
def test_fdata_fast_channel_skip(tmpdir, merge_lis_prs, dfsr_filename):
    fpath = os.path.join(str(tmpdir), 'fast-channel-ints.lis')

    content = headers + [
        'data/lis/records/curves/' + dfsr_filename,
        'data/lis/records/curves/fdata-fast-int.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(NotImplementedError) as exc:
            _ = lis.curves(f, dfs)
        assert "Fast channel not implemented" in str(exc.value)

        curves = lis.curves(f, dfs, skip_fast=True)
        assert curves.dtype == np.dtype([('CH01', 'i4'), ('CH03', 'i4')])
        np.testing.assert_array_equal(curves['CH01'], np.array([1, 5]))
        np.testing.assert_array_equal(curves['CH03'], np.array([4, 8]))

@pytest.mark.xfail(strict=True, reason="coming soon, interface unclear")
def test_fdata_fast_channel_ints(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-ints.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-int.lis.part',
        'data/lis/records/curves/fdata-fast-int.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        # interface unclear.
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Call other method to get fast channel data" in str(exc.value)
        # CH01 is index, CH02 is fast, CH03 is not
        # Data: 1, (2, 3)s, 4;
        #       5, (6, 7)s, 8;

@pytest.mark.xfail(strict=True, reason="would we support sampled strings")
def test_fdata_fast_channel_strings(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-strings.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-str.lis.part',
        'data/lis/records/curves/fdata-fast-str.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Call other method to get fast channel data" in str(exc.value)
        # CH01 is index, CH02 is fast, CH03 is not
        # Data: 1, ("STR sample 1    ", "STR sample 2    ")s, "STR not sampled ";

@pytest.mark.xfail(strict=True, reason="coming soon")
def test_fdata_fast_channel_bad(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-bad.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-int-bad.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        # call correct method to get the error
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Cannot compute an integral size for samples" in str(exc.value)

# we have no confirmation that our understanding is correct
@pytest.mark.xfail(strict=True, reason="coming soon, interface unclear")
def test_fdata_fast_channel_dimensional(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-dimensional.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-dimensional.lis.part',
        'data/lis/records/curves/fdata-fast-dimensional.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Call other method to get fast channel data" in str(exc.value)
        # CH01 is index, CH02 is fast, CH03 is not
        # Data: 1, ([2, 3, 4],  [5, 6, 7])s,     8;
        #       9, ([10, 11, 12], [13, 14, 15])s, 16;

# 1. depending on implementation might need test where depth_mode=1,
# but spacing is not present. We still might try to deduce it.
# 2. unclear if this must have any impact on depth when depth_mode=0
@pytest.mark.xfail(strict=True, reason="coming soon?")
def test_fdata_fast_channel_depth(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-depth.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-depth.lis.part',
        'data/lis/records/curves/fdata-fast-depth.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Call other method to get fast channel data" in str(exc.value)
        # CH01 is fast, CH02 is not, depth is recorded separately
        # frame1: depth 1.
        #   sample1: CH01: 2, CH02: 4, Depth: 1.5
        #   sample2: CH01: 3, CH02: 4, Depth: 2
        # frame2: depth 2.
        #   sample1: CH01: 5, CH02: 7, Depth: 2.5
        #   sample2: CH01: 6, CH02: 7, Depth: 3

@pytest.mark.xfail(strict=True)
def test_fdata_fast_channel_down(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-index-dir-down.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-index-down.lis.part',
        'data/lis/records/curves/fdata-fast-index-2.lis.part',
        'data/lis/records/curves/fdata-fast-index-1.lis.part',
        'data/lis/records/curves/fdata-fast-index1.lis.part',
        'data/lis/records/curves/fdata-fast-index2.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        curves = lis.curves(f, dfs, skip_fast=True)
        np.testing.assert_array_equal(curves['CH01'], np.array([-5, -1, 1, 5]))

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Call other method to get fast channel data" in str(exc.value)

@pytest.mark.xfail(strict=True)
def test_fdata_fast_channel_up(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-index-dir-up.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-index-up.lis.part',
        'data/lis/records/curves/fdata-fast-index2.lis.part',
        'data/lis/records/curves/fdata-fast-index1.lis.part',
        'data/lis/records/curves/fdata-fast-index-1.lis.part',
        'data/lis/records/curves/fdata-fast-index-2.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        curves = lis.curves(f, dfs, skip_fast=True)
        np.testing.assert_array_equal(curves['CH01'], np.array([5, 1, -1, -5]))

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Call other method to get fast channel data" in str(exc.value)

# broken DEPTH0 as index
# unclear if that should matter at all for non-fast channels setups
# also unclear if we should care, or if inconsistent index is user's problem
# at least warning would be nice though.
@pytest.mark.xfail(strict=True)
def test_fdata_fast_channel_index_direction_mixed(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-index-dir-mixed.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-index-down.lis.part',
        'data/lis/records/curves/fdata-fast-index1.lis.part',
        'data/lis/records/curves/fdata-fast-index4.lis.part',
        'data/lis/records/curves/fdata-fast-index2.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        curves = lis.curves(f, dfs, skip_fast=True)
        np.testing.assert_array_equal(curves['CH01'], np.array([1, 13, 5]))

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Index is inconsistent" in str(exc.value)

@pytest.mark.xfail(strict=True)
def test_fdata_fast_channel_index_direction_mismatch(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-index-dir-mismatch.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-index-down.lis.part',
        'data/lis/records/curves/fdata-fast-index3.lis.part',
        'data/lis/records/curves/fdata-fast-index2.lis.part',
        'data/lis/records/curves/fdata-fast-index1.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        curves = lis.curves(f, dfs, skip_fast=True)
        np.testing.assert_array_equal(curves['CH01'], np.array([9, 5, 1]))

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        # warning?
        assert "Index direction mismatches declared: DOWN" in str(exc.value)

@pytest.mark.xfail(strict=True)
def test_fdata_fast_channel_index_spacing_inconsistent(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-index-bad-spacing.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-index-down.lis.part',
        'data/lis/records/curves/fdata-fast-index1.lis.part',
        'data/lis/records/curves/fdata-fast-index2.lis.part',
        'data/lis/records/curves/fdata-fast-index4.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        curves = lis.curves(f, dfs, skip_fast=True)
        np.testing.assert_array_equal(curves['CH01'], np.array([1, 5, 13]))

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Index spacing is DOWN, but inconsistent" in str(exc.value)

@pytest.mark.xfail(strict=True, reason="coming soon, interface unclear")
def test_fdata_fast_channel_two_different(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channels-sampled-differently.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-two-diff.lis.part',
        'data/lis/records/curves/fdata-fast-two-diff.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        # interface unclear.
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Call other method to get fast channel data" in str(exc.value)
        # CH01 is index, CH02 is fast, CH03 is fast, CH04 is not
        # frame1: CHO1: 1, CH02: (2, 3)s, CH03: (4, 5, 6)s, CH04: 13
        # frame2: CH01: 7, CH02: (8, 9)s, CH03: (10, 11, 12)s, CH04: 14

@pytest.mark.xfail(strict=True, reason="coming soon, interface unclear")
def test_fdata_fast_channel_two_same(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channels-sampled-same.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-two-same.lis.part',
        'data/lis/records/curves/fdata-fast-two-same.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        # interface unclear.
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Call other method to get fast channel data" in str(exc.value)
        # CH01 is index, CH02 is fast, CH03 is fast
        # frame1: CHO1: 1, CH02: (2, 3)s, CH03: (4, 5)s
        # frame2: CH01: 9, CH02: (10, 11)s, CH03: (12, 13)s

@pytest.mark.xfail(strict=True, reason="coming soon, interface unclear")
def test_fdata_fast_channel_index_conversion(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channels-index-conversion.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-conversion.lis.part',
        'data/lis/records/curves/fdata-fast-conversion.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        # interface unclear.
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "You index is bad" in str(exc.value)
        # CH01 is index, CH02 is fast
        # frame1: CHO1: 1, CH02: (5, 6)s
        # frame2: CH01: 2, CH02: (7, 8)s

@pytest.mark.xfail(strict=True, reason="coming soon, interface unclear")
def test_fdata_fast_channel_first_fast(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-is-first.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-first.lis.part',
        'data/lis/records/curves/fdata-fast-int.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Index is fast. You can't define index channel" in str(exc.value)


def test_fdata_bad_data(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fdata-bad-data.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-simple.lis.part',
        'data/lis/records/curves/fdata-bad-fdata.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "corrupted record: fmtstr would read past end" in str(exc.value)


def test_duplicated_mnemonics(tmpdir, merge_lis_prs, assert_error,
                              assert_message_count):
    fpath = os.path.join(str(tmpdir), 'same-mnemonics.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-mnemonics-same.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)
    with lis.load(fpath) as (f, *_):
        dfs = f.data_format_specs()[0]
        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert "field 'NAME' occurs more than once" in str(exc.value)
        assert_error("duplicated mnemonics")

        curves = lis.curves(f, dfs, strict=False)
        assert_message_count("duplicated mnemonics", 2)

        names  = curves.dtype.names
        assert names == ('NAME(0)', 'NAME(1)', 'TEST', 'NAME(2)')
