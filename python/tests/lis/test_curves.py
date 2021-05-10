from dlisio import lis, core
import numpy as np
import os
import pytest

def test_dfsr_fmtstring():
    path = 'data/lis/MUD_LOG_1.LIS'

    with lis.load(path) as (lf, *tail):
        dfsr = lf.data_format_specs()[0]

        indexfmt, fmt = lis.dfsr_fmtstr(dfsr, sample_rate=1)
        assert indexfmt == 'f1'
        assert fmt      == 'f1' * 43

def test_dfsr_dtype():
    path = 'data/lis/MUD_LOG_1.LIS'

    with lis.load(path) as (lf, *tail):
        dfsr = lf.data_format_specs()[0]

        dtype = lis.dfsr_dtype(dfsr, sample_rate=1)

        expected = np.dtype([
            (ch.mnemonic, np.float32)
            for ch in dfsr.specs
        ])

        assert dtype == expected


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

        entries = {entry.type : entry.value for entry in dfs.entries}
        assert entries[0]  == 60         # Terminator, no interface defined
        assert entries[10] == "UNDEFINE" # field undefined, should be missing

        assert dfs.record_type             == 0
        assert dfs.spec_block_type         == 0
        assert dfs.frame_size              == 32
        assert dfs.direction               == 0 #"none"
        assert dfs.optical_log_depth_units == 255 #"meters"
        assert dfs.reference_point         == -4
        assert dfs.reference_point_units   == "INCH"
        assert dfs.spacing                 == 60
        assert dfs.spacing_units           == "INCH"
        assert dfs.max_frames              == 8
        assert dfs.absent_value            == -15988.0
        assert dfs.depth_mode              == 1 #True
        assert dfs.depth_units             == "INCH"
        assert dfs.depth_reprc             == 73 #reprc_int_32
        assert dfs.spec_block_subtype      == 1

def test_entries_default_values(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'entries-default.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-entries-default.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        assert len(dfs.entries) == 1

        entries = {entry.type : entry.value for entry in dfs.entries}
        assert entries[0]  == 60 # defined with value

        assert dfs.record_type             == 0
        assert dfs.spec_block_type         == 0
        assert dfs.frame_size              == None
        assert dfs.direction               == 1 #"up"
        assert dfs.optical_log_depth_units == 1 #"feet"
        assert dfs.reference_point         == None
        assert dfs.reference_point_units   == ".1IN"
        assert dfs.spacing                 == None
        assert dfs.spacing_units           == ".1IN"
        assert dfs.max_frames              == None
        assert dfs.absent_value            == -999.25
        assert dfs.depth_mode              == 0 #False
        assert dfs.depth_units             == ".1IN"
        assert dfs.depth_reprc             == None
        assert dfs.spec_block_subtype      == 0

def test_entries_size_0_values(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'entries-size-0.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-entries-size-0.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        assert len(dfs.entries) == 16

        entries = {entry.type : entry.value for entry in dfs.entries}
        assert entries[0]  == None #defined with size 0

        assert dfs.record_type             == None
        assert dfs.spec_block_type         == None
        assert dfs.frame_size              == None
        assert dfs.direction               == None
        assert dfs.optical_log_depth_units == None
        assert dfs.reference_point         == None
        assert dfs.reference_point_units   == None
        assert dfs.spacing                 == None
        assert dfs.spacing_units           == None
        assert dfs.max_frames              == None
        assert dfs.absent_value            == None
        assert dfs.depth_mode              == None
        assert dfs.depth_units             == None
        assert dfs.depth_reprc             == None
        assert dfs.spec_block_subtype      == None

def test_entries_same_type(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'entries-same-type.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-entries-same-type.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        entries = [entry.value
                   for entry in dfs.entries
                   if entry.type == int(core.lis_ebtype.up_down_flag)]
        assert entries  == [1, 255]

        with pytest.raises(ValueError) as exc:
            _ = dfs.direction
        msg = "Multiple Entry Blocks of type lis_ebtype.up_down_flag"
        assert msg in str(exc.value)

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

def test_entries_invalid_type():
    path = 'data/lis/records/curves/dfsr-entries-bad-type.lis.part'
    with lis.load(path) as (f,):
        with pytest.raises(RuntimeError) as exc:
            _ = f.data_format_specs()
        assert "unknown entry type 65" in str(exc.value)

def test_entries_invalid_repcode():
    path = 'data/lis/records/curves/dfsr-entries-bad-reprc.lis.part'
    with lis.load(path) as (f,):
        with pytest.raises(RuntimeError) as exc:
            _ = f.data_format_specs()
        assert "unknown representation code 83" in str(exc.value)


def test_dfsr_subtype0(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dfsr-subtype0.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-subtype0.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        ch1 = dfs.specs[0]
        assert ch1.mnemonic         == "CH01"
        assert ch1.service_id       == "testCH"
        assert ch1.service_order_nr == "  1234  "
        assert ch1.units            == "INCH"
        assert ch1.api_log_type     == 2
        assert ch1.api_curve_type   == 179
        assert ch1.api_curve_class  == 96
        assert ch1.api_modifier     == 59
        assert ch1.filenr           == 1
        assert ch1.reserved_size    == 4
        assert ch1.process_level    == 255
        assert ch1.samples          == 1
        assert ch1.reprc            == 73

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
        assert ch1.mnemonic           == "CH01"
        assert ch1.service_id         == "testCH"
        assert ch1.service_order_nr   == "  1234  "
        assert ch1.units              == "INCH"
        assert ch1.api_codes          == 45310011
        assert ch1.filenr             == 1
        assert ch1.reserved_size      == 4
        assert ch1.samples            == 1
        assert ch1.reprc              == 73

        flags = ch1.process_indicators
        assert flags["original logging direction"]     == 3
        assert flags["true vertical depth correction"] == True
        assert flags["data channel not on depth"]      == True
        assert flags["data channel is filtered"]       == True
        assert flags["data channel is calibrated"]     == True
        assert flags["computed"]                       == True
        assert flags["derived"]                        == True
        assert flags["tool defined correction nb 2"]   == True
        assert flags["tool defined correction nb 1"]   == True
        assert flags["mudcake correction"]             == True
        assert flags["lithology correction"]           == True
        assert flags["inclinometry correction"]        == True
        assert flags["pressure correction"]            == True
        assert flags["hole size correction"]           == True
        assert flags["temperature correction"]         == True
        assert flags["auxiliary data flag"]            == True
        assert flags["schlumberger proprietary"]       == True

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

        indexfmt, fmt = lis.dfsr_fmtstr(dfs, sample_rate=1)
        assert indexfmt == 'b1'
        assert      fmt == 's1i1l1e1f1r1p1'

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

        indexfmt, fmt = lis.dfsr_fmtstr(dfs, sample_rate=1)
        assert indexfmt == 'i1'
        assert fmt      == 'a32'

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
            lis.validate_dfsr(dfs)

        assert lis.dfsr_fmtstr(dfs, sample_rate=1) == ('i1', 'm4')

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

        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert "Invalid representation code (170)" in str(exc.value)


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
        assert "Invalid number of samples (0) for curve BAD" in str(exc.value)

@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-size-0-one-block.lis.part',
    'dfsr-size-0-two-blocks.lis.part',
    'dfsr-size-0-string.lis.part',
])
def test_fdata_size_0(tmpdir, merge_lis_prs, dfsr_filename):
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
        msg = "Invalid size (0) for curve BAD , should be != 0"
        assert msg in str(exc.value)

def test_fdata_no_channels(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dfsr-no-channels.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-entries-default.lis.part',
        'data/lis/records/curves/fdata-size.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        msg = "DataFormatSpec() has no channels"
        assert msg in str(exc.value)

def test_fdata_size_less_than_repcode_size(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dfsr-size-lt-repcode-size.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-size-lt-repcode.lis.part',
        'data/lis/records/curves/fdata-size.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert "Invalid number of entries per sample" in str(exc.value)


def test_fdata_many_frames_per_record(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'many-frames-per-record.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-simple.lis.part',
        'data/lis/records/curves/fdata-frames-in-record.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        curves = lis.curves(f, dfs)
        assert len(curves) == 4
        expected = np.array([1, 4, 7, 10])
        np.testing.assert_array_equal(curves['CH01'], expected)
        expected = np.array([2, 5, 8, 11])
        np.testing.assert_array_equal(curves['CH02'], expected)
        expected = np.array([3, 6, 9, 12])
        np.testing.assert_array_equal(curves['CH03'], expected)


def test_depth_mode_1_dir_down_nospace(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'depth-dir-down.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-depth-spacing-no.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert "No spacing recorded" in str(exc.value)

@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-depth-dir-down.lis.part',
    'dfsr-depth-reprc-size.lis.part',
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

        expected = np.array([-3, -2, -1, 0, 1, 2, 3, 4, 5])
        np.testing.assert_array_equal(curves['DEPT'], expected)

        expected = np.array([12, 13, 14, 15, 16, 17, 18, 19, 20])
        np.testing.assert_array_equal(curves['CH01'], expected)

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

        expected = np.array([53, 52, 51, 50, 49])
        np.testing.assert_array_equal(curves['DEPT'], expected)

        expected = np.array([37, 36, 35, 34, 33])
        np.testing.assert_array_equal(curves['CH01'], expected)

@pytest.mark.parametrize('dfsr_filename', [
    'dfsr-depth-dir-none.lis.part',
    'dfsr-depth-dir-invalid.lis.part',
])
def test_depth_mode_1_direction_bad(tmpdir, merge_lis_prs, dfsr_filename):
    fpath = os.path.join(str(tmpdir), 'depth-dir-bad.lis')

    content = headers + [
        'data/lis/records/curves/' + dfsr_filename,
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert "Invalid direction (UP/DOWN flag)" in str(exc.value)

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
        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert "Invalid representation code" in str(exc.value)

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


def test_depth_mode_1_conversion(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'depth-int-float-conversion')

    content = headers + [
        'data/lis/records/curves/dfsr-depth-conversion.lis.part',
        'data/lis/records/curves/fdata-depth-down-PR1.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Unable to create integral index" in str(exc.value)


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

def test_fdata_dimensional_bad(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'dimensional-bad.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-dimensional-bad.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert 'cannot have multiple entries per sample' in str(exc.value)


def test_fdata_suppressed(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'suppressed.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-suppressed.lis.part',
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

def test_fdata_suppressed_bad(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'suppressed-bad.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-suppressed-bad.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert 'Invalid number of entries per sample' in str(exc.value)


def test_fdata_fast_channel_skip(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-ints.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-int.lis.part',
        'data/lis/records/curves/fdata-fast-int.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Multiple sampling rates in file" in str(exc.value)

        curves = lis.curves(f, dfs, sample_rate=1)
        assert curves.dtype == np.dtype([('CH01', 'i4'), ('CH03', 'i4')])
        np.testing.assert_array_equal(curves['CH01'], np.array([1, 5]))
        np.testing.assert_array_equal(curves['CH03'], np.array([4, 8]))

def test_fdata_fast_channel_ints(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-ints.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-int.lis.part',
        'data/lis/records/curves/fdata-fast-int.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "Multiple sampling rates in file" in str(exc.value)

        curves = lis.curves(f, dfs, sample_rate=1)
        assert curves.dtype == np.dtype([('CH01', 'i4'), ('CH03', 'i4')])
        expected = np.array([1, 5])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([4, 8])
        np.testing.assert_array_equal(curves['CH03'], expected)

        curves = lis.curves(f, dfs, sample_rate=2)
        assert curves.dtype == np.dtype([('CH01', 'i4'), ('CH02', 'i2')])
        expected = np.array([0, 1, 3, 5])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([2, 3, 6, 7])
        np.testing.assert_array_equal(curves['CH02'], expected)

def test_fdata_fast_channel_strings(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-strings.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-str.lis.part',
        'data/lis/records/curves/fdata-fast-str.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        curves = lis.curves(f, dfs, sample_rate=1)
        np.testing.assert_array_equal(curves['CH01'], np.array([1]))

        expected = np.array(["STR not sampled "])
        np.testing.assert_array_equal(curves['CH03'], expected)

        curves = lis.curves(f, dfs, sample_rate=2)
        np.testing.assert_array_equal(curves['CH01'], np.array([0, 1]))

        expected = np.array(["STR sample 1    ", "STR sample 2    "])
        np.testing.assert_array_equal(curves['CH02'], expected)

def test_fdata_fast_channel_bad(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-bad.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-int-bad.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs, sample_rate=1)
        assert "Invalid sample size" in str(exc.value)

        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs, sample_rate=2)
        assert "Invalid sample size" in str(exc.value)

def test_fdata_fast_channel_dimensional(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-dimensional.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-dimensional.lis.part',
        'data/lis/records/curves/fdata-fast-dimensional.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        curves = lis.curves(f, dfs, sample_rate=1)
        expected = np.array([1, 9])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([8, 16])
        np.testing.assert_array_equal(curves['CH03'], expected)

        # Curves with sampling rate x2 the index.
        curves = lis.curves(f, dfs, sample_rate=2)

        expected = np.array([0, 1, 5, 9])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([[2, 3, 4],  [5, 6, 7], [10, 11, 12], [13, 14, 15]])
        np.testing.assert_array_equal(curves['CH02'], expected)


def test_fdata_fast_channel_depth(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-depth.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-depth.lis.part',
        'data/lis/records/curves/fdata-fast-depth-1.lis.part',
        'data/lis/records/curves/fdata-fast-depth-2.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs)
        assert "please explicitly specify which to read" in str(exc.value)

        # Curves with sampling rate x1 the index.
        curves = lis.curves(f, dfs, sample_rate=1)

        expected = np.array([1, 3, 5, 7])
        np.testing.assert_array_equal(curves['DEPT'], expected)

        expected = np.array([4, 7, 10, 13])
        np.testing.assert_array_equal(curves['CH02'], expected)

        # Curves with sampling rate x2 the index.
        curves = lis.curves(f, dfs, sample_rate=2)

        expected = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        np.testing.assert_array_equal(curves['DEPT'], expected)

        expected = np.array([2,  3,  5,  6,  8,  9, 11, 12])
        np.testing.assert_array_equal(curves['CH01'], expected)


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

        curves = lis.curves(f, dfs, sample_rate=2)
        expected = np.array([0, -5, -3, -1, 0, 1, 3, 5])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([-6, -7, -2, -3, 2, 3, 6, 7])
        np.testing.assert_array_equal(curves['CH02'], expected)

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

        curves = lis.curves(f, dfs, sample_rate=2)
        expected = np.array([0, 5, 3,  1, 0, -1, -3, -5])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([6, 7, 2, 3, -2, -3, -6, -7])
        np.testing.assert_array_equal(curves['CH02'], expected)

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

def test_fdata_fast_channel_two_different(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channels-sampled-differently.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-two-diff.lis.part',
        'data/lis/records/curves/fdata-fast-two-diff.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        assert lis.dfsr_fmtstr(dfs, sample_rate=1) == ('l1', 'S2S3l1')
        curves = lis.curves(f, dfs, sample_rate=1)

        expected = np.array([1, 7])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([13, 14])
        np.testing.assert_array_equal(curves['CH04'], expected)

        assert lis.dfsr_fmtstr(dfs, sample_rate=2) == ('l1', 'b1S3S4')
        curves = lis.curves(f, dfs, sample_rate=2)

        expected = np.array([0, 1, 4, 7])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([2, 3, 8, 9])
        np.testing.assert_array_equal(curves['CH02'], expected)

        assert lis.dfsr_fmtstr(dfs, sample_rate=3) ==  ('l1', 'S2b1S4')
        curves = lis.curves(f, dfs, sample_rate=3)

        expected = np.array([0, 0, 1, 3, 5, 7])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([4, 5, 6, 10, 11, 12])
        np.testing.assert_array_equal(curves['CH03'], expected)

def test_fdata_fast_channel_two_same(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channels-sampled-same.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-two-same.lis.part',
        'data/lis/records/curves/fdata-fast-two-same.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]
        curves = lis.curves(f, dfs, sample_rate=2)

        expected = np.array([0, 1, 5, 9])
        np.testing.assert_array_equal(curves['CH01'], expected)

        expected = np.array([2, 3, 10, 11])
        np.testing.assert_array_equal(curves['CH02'], expected)

        expected = np.array([4, 5, 12, 13])
        np.testing.assert_array_equal(curves['CH03'], expected)

def test_fdata_fast_channel_index_conversion(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channels-index-conversion.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-conversion.lis.part',
        'data/lis/records/curves/fdata-fast-conversion.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(RuntimeError) as exc:
            _ = lis.curves(f, dfs, sample_rate=2)
        assert "Unable to create integral index" in str(exc.value)

def test_fdata_fast_channel_first_fast(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'fast-channel-is-first.lis')

    content = headers + [
        'data/lis/records/curves/dfsr-fast-first.lis.part',
        'data/lis/records/curves/fdata-fast-int.lis.part',
    ] + trailers

    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f,):
        dfs = f.data_format_specs()[0]

        with pytest.raises(ValueError) as exc:
            _ = lis.curves(f, dfs)
        assert "Index channel cannot be a fast channel" in str(exc.value)


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
