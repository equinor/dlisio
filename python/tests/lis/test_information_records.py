import pytest
import numpy as np

from dlisio import lis, core

@pytest.fixture(scope="module")
def fpath(tmpdir_factory, merge_lis_prs):
    """
    Resulted file contains examples of Information Records
    """
    path = str(tmpdir_factory.mktemp('lis-semantic').join('inforecs.lis'))
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/job-identification.lis.part',
        'data/lis/records/wellsite-data.lis.part',
        'data/lis/records/tool-string-info.lis.part',
        'data/lis/records/encrypted-table-dump.lis.part',
        'data/lis/records/table-dump.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(path, content)
    return path

@pytest.fixture(scope="module")
def f(fpath):
    with lis.load(fpath) as (f, *_):
        yield f


def test_inforec_components():
    path = 'data/lis/records/inforec_01.lis'
    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]
    assert len(wellsite.components()) == 16

def test_inforec_table_name():
    path = 'data/lis/records/inforec_01.lis'
    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]

    assert wellsite.isstructured()
    name = wellsite.table_name()

    assert name == 'CONS'

def test_inforec_table_dtype():
    path = 'data/lis/records/inforec_01.lis'
    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]

    assert wellsite.isstructured()
    table = wellsite.table()

    expected_dtype = np.dtype([
        ('MNEM', 'O'),
        ('STAT', 'O'),
        ('PUNI', 'O'),
        ('TUNI', 'O'),
        ('VALU', 'O')
    ])

    assert table.dtype == expected_dtype

def test_inforec_dense_table():
    path = 'data/lis/records/inforec_01.lis'
    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]

    assert wellsite.isstructured()
    table = wellsite.table(simple=True)

    mnem = np.array(['WN  ', 'CN  ', 'SRVC'], dtype='O')
    np.testing.assert_array_equal(table['MNEM'], mnem)

    stat = np.array(['ALLO', 'ALLO', 'ALLO'], dtype='O')
    np.testing.assert_array_equal(table['STAT'], stat)

    puni = np.array(['    ', '    ', '    '], dtype='O')
    np.testing.assert_array_equal(table['PUNI'], puni)

    tuni = np.array(['    ', '    ', '    '], dtype='O')
    np.testing.assert_array_equal(table['TUNI'], tuni)

    valu = np.array(['15/9-F-15 ', 'StatoilHydro', 'Geoservices '], dtype='O')
    np.testing.assert_array_equal(table['VALU'], valu)

def test_inforec_sparse_table():
    path = 'data/lis/records/inforec_02.lis'

    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]

    assert wellsite.isstructured()
    table = wellsite.table(simple=True)

    mnem = np.array([None, 'CN  ', 'SRVC'], dtype='O')
    np.testing.assert_array_equal(table['MNEM'], mnem)

    stat = np.array(['ALLO', None, 'ALLO'], dtype='O')
    np.testing.assert_array_equal(table['STAT'], stat)

    puni = np.array(['    ', '    ', '    '], dtype='O')
    np.testing.assert_array_equal(table['PUNI'], puni)

    tuni = np.array(['    ', '    ', '    '], dtype='O')
    np.testing.assert_array_equal(table['TUNI'], tuni)

    valu = np.array(['15/9-F-15 ', 'StatoilHydro', None], dtype='O')
    np.testing.assert_array_equal(table['VALU'], valu)


@pytest.mark.parametrize('filename', ['inforec_03.lis', 'inforec_04.lis'])
def test_inforec_unstructured(filename):
    # inforec_03.lis and inforec_04.lis are identical except for the type_nb
    # field in the CBs. In 03 all CB's have type_nb==0, in 04 the value of
    # type_nb vary. Regardless, none of them are table records and should
    # behave the same.
    path = 'data/lis/records/' + filename

    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]
    components = wellsite.components()

    assert wellsite.isstructured() == False
    assert len(components) == 15

    expected = [
        'WN  ', 'ALLO', '    ', '    ', '15/9-F-15 ',
        'CN  ', 'ALLO', '    ', '    ', 'StatoilHydro',
        'SRVC', 'ALLO', '    ', '    ', 'Geoservices '
    ]

    for i, cb in enumerate(components):
        assert cb.component == expected[i]

    with pytest.raises(ValueError):
        _ = wellsite.table()

    with pytest.raises(ValueError):
        _ = wellsite.table_name()

def test_inforec_illformed():
    path = 'data/lis/records/inforec_05.lis'
    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]

    assert wellsite.isstructured() == True

    # The table name can still be read
    name = wellsite.table_name()
    assert name == 'CONS'

    # The table itself cannot be read
    with pytest.raises(ValueError):
        _ = wellsite.table()

def test_inforec_empty():
    path = 'data/lis/records/inforec_06.lis'
    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]

    assert wellsite.isstructured() == False
    assert len(wellsite.components()) == 0

    with pytest.raises(ValueError) as exc:
        _ = wellsite.table_name()
    assert "Record is not structured as a table" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        _ = wellsite.table()
    assert "Record is not structured as a table" in str(exc.value)

def test_inforec_empty_table():
    path = 'data/lis/records/inforec_07.lis'
    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]

    assert wellsite.isstructured() == True
    assert len(wellsite.components()) == 1

    name = wellsite.table_name()
    assert name == 'CONS'

    np.testing.assert_array_equal(wellsite.table(), np.empty(0))

def test_inforec_empty_components():
    path = 'data/lis/records/inforec_08.lis'
    f, = lis.load(path)
    wellsite = f.wellsite_data()[0]

    assert wellsite.isstructured()
    table = wellsite.table(simple=True)

    mnem = np.array(['MN1 ', 'MN2 '], dtype='O')
    np.testing.assert_array_equal(table['MNEM'], mnem)

    puni = np.array(['val1', 'val2'], dtype='O')
    np.testing.assert_array_equal(table['VALU'], puni)

    valu = np.array([None, None,], dtype='O')
    np.testing.assert_array_equal(table['ATTR'], valu)

def test_inforec_cut_in_fixed_size():
    path = 'data/lis/records/inforec-cut-in-fixed.lis.part'
    f, = lis.load(path)

    with pytest.raises(RuntimeError) as exc:
        _ = f.wellsite_data()
    assert "lis::component_block: 10 bytes left in record" in str(exc.value)

def test_inforec_cut_in_component():
    path = 'data/lis/records/inforec-cut-in-value.lis.part'
    f, = lis.load(path)

    with pytest.raises(RuntimeError) as exc:
        _ = f.wellsite_data()
    assert "2 bytes left in record, expected at least 4" in str(exc.value)

def test_inforecords(f):
    assert len(f.job_identification()) == 1
    assert len(f.wellsite_data())      == 1
    assert len(f.tool_string_info())   == 1

    data = {
        f.job_identification()[0] : 'JOB ',
        f.wellsite_data()[0]      : 'WELL',
        f.tool_string_info()[0]   : 'TOOL',
    }

    for inforec, type in data.items():
        components = inforec.components()

        assert len(components) == 3

        assert components[0].type_nb   == 73
        assert components[0].reprc     == 65
        assert components[0].size      == 4
        assert components[0].category  == 0
        assert components[0].mnemonic  == 'TYPE'
        assert components[0].units     == '    '
        assert components[0].component == type

        assert components[1].type_nb   == 0
        assert components[1].reprc     == 65
        assert components[1].size      == 6
        assert components[1].category  == 1
        assert components[1].mnemonic  == 'R1C1'
        assert components[1].units     == '    '
        assert components[1].component == 'VALue1'

        assert components[2].type_nb   == 69
        assert components[2].reprc     == 73
        assert components[2].size      == 4
        assert components[2].category  == 0
        assert components[2].mnemonic  == 'R1C2'
        assert components[2].units     == 'unit'
        assert components[2].component == 89

def test_table_dump(f):
    with pytest.raises(NotImplementedError) as exc:
        f.parse_records(core.lis_rectype.table_dump)
    assert "No parsing rule for Table Dump Records" in str(exc.value)

def test_encrypted_table_dump(f):
    with pytest.raises(NotImplementedError) as exc:
        f.parse_records(core.lis_rectype.enc_table_dump)
    assert "No parsing rule for Encrypted Table Dump Records" in str(exc.value)

