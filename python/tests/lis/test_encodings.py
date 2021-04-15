"""Encoding tests similar to dlis"""
import pytest
import os
import numpy as np

import dlisio
from dlisio import lis

def test_fixed_value_encoding(tmpdir, merge_lis_prs):

    fpath = os.path.join(str(tmpdir), 'encoded-fixed-value.dlis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-encoded.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings([])

    try:
        f, = lis.load(fpath)

        trailer = f.tape.trailer()
        with pytest.warns(UnicodeWarning):
            assert trailer.name == b'\xec\xc5\xce\xd4\xc1\x30\x30\x31'

        dlisio.common.set_encodings(['koi8_r'])
        trailer = f.tape.trailer()
        assert trailer.name == 'Лента001'

    finally:
        dlisio.common.set_encodings(prev_encodings)
        f.close()

def test_inforec_encoding(tmpdir, merge_lis_prs):

    fpath = os.path.join(str(tmpdir), 'encoded-inforec.dlis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/inforec-encoded.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings([])

    try:
        f, = lis.load(fpath)

        wellsite = f.wellsite_data()[0]

        with pytest.warns(UnicodeWarning):
            assert wellsite.table_name() == b'\xeb\xef\xe9\x38'

        dlisio.common.set_encodings(['koi8_r'])
        wellsite = f.wellsite_data()[0]

        components = wellsite.components()

        assert components[0].mnemonic  == 'ТАБЛ'
        assert components[0].units     == '    '
        assert components[0].component == 'КОИ8'

        assert components[1].mnemonic  == 'НАЗВ'
        assert components[1].units     == 'изме'
        assert components[1].component == 'ЗНАЧ'

        table = wellsite.table(simple=True)

        mnem = np.array(['ЗНАЧ'], dtype='O')
        np.testing.assert_array_equal(table['НАЗВ'], mnem)

    finally:
        dlisio.common.set_encodings(prev_encodings)
        f.close()

def test_dfsr_encoding(tmpdir, merge_lis_prs):

    fpath = os.path.join(str(tmpdir), 'encoded-curves.dlis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/curves/dfsr-encoded.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings([])

    try:
        f, = lis.load(fpath)

        dfs = f.data_format_specs()[0]
        with pytest.warns(UnicodeWarning):
            assert dfs.specs[0].mnemonic == b'\xeb\xe1\xee\x31'

        dlisio.common.set_encodings(['koi8_r'])
        dfs = f.data_format_specs()[0]

        entries = {entry.type: entry.value for entry in dfs.entries}
        assert entries[7] == "дюйм"

        ch1 = dfs.specs[0]
        assert ch1.mnemonic == "КАН1"
        assert ch1.units == "изме"

    finally:
        dlisio.common.set_encodings(prev_encodings)
        f.close()

@pytest.mark.xfail(strict=True, reason="both cases not supported")
def test_curves_encoding(tmpdir, merge_lis_prs):

    fpath = os.path.join(str(tmpdir), 'encoded-curves.dlis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/curves/dfsr-encoded.lis.part',
        'data/lis/records/curves/fdata-encoded.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings([])

    try:
        f, = lis.load(fpath)

        dfs = f.data_format_specs()[0]
        with pytest.warns(UnicodeWarning):
           cur = lis.curves(f, dfs)
        assert cur[b'\xeb\xe1\xee\x31'] == [b'\xda\xce\xc1\xde\xc5\xce\xc9\xc5']

        dlisio.common.set_encodings(['koi8_r'])

        dfs = f.data_format_specs()[0]
        curves = lis.curves(f, dfs)
        assert curves["КАН1"] == ["значение"]

    finally:
        dlisio.common.set_encodings(prev_encodings)
        f.close()
