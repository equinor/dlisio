from dlisio import lis, core
import numpy as np

def test_dfsr_fmtstring():
    path = 'data/lis/MUD_LOG_1.LIS'

    with lis.load(path) as (lf, *tail):
        dfsr = lf.data_format_specs()[0]

        fmt = core.dfs_formatstring(dfsr)
        assert fmt == 'D' * 44

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
