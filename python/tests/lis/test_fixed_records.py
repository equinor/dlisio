import pytest

from dlisio import lis
import os

@pytest.fixture(scope="module")
def fpath(tmpdir_factory, merge_lis_prs):
    """
    Reel, Tape and File Header.
    """
    path = str(tmpdir_factory.mktemp('lis-semantic').join('fixed.lis'))
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
        'data/lis/records/RHLR-2.lis.part',
        'data/lis/records/THLR-2.lis.part',
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
        'data/lis/records/TTLR-2.lis.part',
        'data/lis/records/RTLR-2.lis.part',
    ]
    merge_lis_prs(path, content)
    return path

@pytest.fixture(scope="module")
def f(fpath):
    with lis.load(fpath) as (f1, f2, *_):
        yield (f1, f2)


def test_file_header(f):
    def assert_header(header, file_name, prev_file_name):
        assert header.file_name           == file_name
        assert header.service_sublvl_name == 'PRTEST'
        assert header.version_number      == '0.000001'
        assert header.date_of_generation  == '81/02/28'
        assert header.max_pr_length       == ' 1024'
        assert header.file_type           == 'LO'
        assert header.prev_file_name      == prev_file_name

    f1, f2 = f
    assert_header(f1.header(), 'LISTST.001', ' '*10)
    assert_header(f2.header(), 'LISTST.002', 'LISTST.001')

def test_file_trailer(f):
    def assert_trailer(trailer, file_name, next_file_name):
        assert trailer.file_name           == file_name
        assert trailer.service_sublvl_name == 'PRTEST'
        assert trailer.version_number      == '0.000001'
        assert trailer.date_of_generation  == '81/02/28'
        assert trailer.max_pr_length       == ' 1024'
        assert trailer.file_type           == 'LO'
        assert trailer.next_file_name      == next_file_name

    f1, f2 = f
    assert_trailer(f1.trailer(), 'LISTST.001', 'LISTST.002')
    assert_trailer(f2.trailer(), 'LISTST.002', ' '*10)

def test_reel_header(f):
    def assert_reel(reel_header, name, cont_number, prev_reel_name, comment):
        assert reel_header.service_name        == 'LISTST'
        assert reel_header.date                == '81/02/28'
        assert reel_header.origin_of_data      == 'OURS'
        assert reel_header.name                == name
        assert reel_header.continuation_number == cont_number
        assert reel_header.prev_reel_name      == prev_reel_name
        assert reel_header.comment.strip()     == comment

    f1, f2 = f
    assert_reel(f1.reel.header(), 'Reel1234', '01', ' ' * 8,
                'This is supposed to be the first reel on the stack')
    assert_reel(f2.reel.header(), 'Reel5678', '02', 'Reel1234',
                'This is supposed to be the second reel on the stack')

def test_reel_trailer(f):
    def assert_reel(reel_trailer, name, cont_number, next_reel_name, comment):
        assert reel_trailer.service_name        == 'LISTST'
        assert reel_trailer.date                == '81/02/28'
        assert reel_trailer.origin_of_data      == 'OURS'
        assert reel_trailer.name                == name
        assert reel_trailer.continuation_number == cont_number
        assert reel_trailer.next_reel_name      == next_reel_name
        assert reel_trailer.comment.strip()     == comment

    f1, f2 = f
    assert_reel(f1.reel.trailer(), 'Reel1234', '01', 'Reel5678',
                'This is supposed to be the first reel on the stack')
    assert_reel(f2.reel.trailer(), 'Reel5678', '02', ' ' * 8,
                'This is supposed to be the second reel on the stack')

def test_tape_header(f):
    def assert_tape(tape_header, name, cont_number, prev_tape_name, comment):
        assert tape_header.service_name        == 'LISTST'
        assert tape_header.date                == '81/02/28'
        assert tape_header.origin_of_data      == 'OURS'
        assert tape_header.name                == name
        assert tape_header.continuation_number == cont_number
        assert tape_header.prev_tape_name      == prev_tape_name
        assert tape_header.comment.strip()     == comment

    f1, f2 = f
    assert_tape(f1.tape.header(), 'Tape0001', '01', ' ' * 8,
                'This is supposed to be the first tape on the reel')
    assert_tape(f2.tape.header(), 'Tape0002', '02', 'Tape0001',
                'This is supposed to be the second tape on the reel')

def test_tape_trailer(f):
    def assert_tape(tape_trailer, name, cont_number, next_tape_name, comment):
        assert tape_trailer.service_name        == 'LISTST'
        assert tape_trailer.date                == '81/02/28'
        assert tape_trailer.origin_of_data      == 'OURS'
        assert tape_trailer.name                == name
        assert tape_trailer.continuation_number == cont_number
        assert tape_trailer.next_tape_name      == next_tape_name
        assert tape_trailer.comment.strip()     == comment

    f1, f2 = f
    assert_tape(f1.tape.trailer(), 'Tape0001', '01', 'Tape0002',
                'This is supposed to be the first tape on the reel')
    assert_tape(f2.tape.trailer(), 'Tape0002', '02', ' ' * 8,
                'This is supposed to be the second tape on the reel')


# note that message is different from similar in Tape/Reel
def test_fixed_file_header_too_short(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'FHLR-too-short.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-too-short.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f, *_):
        with pytest.raises(RuntimeError) as exc:
            _ = f.header()
        msg = 'File Header Records are 56 bytes, raw record is only 46'
        assert msg in str(exc.value)

@pytest.mark.xfail(strict=True, reason="no upper bound check. do we want it?")
def test_fixed_file_header_too_long(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'FHLR-too-long.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-too-long.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f, *_):
        with pytest.raises(RuntimeError) as exc:
            _ = f.header()
        msg = 'File Header Records are 56 bytes, raw record is 58'
        assert msg in str(exc.value)

@pytest.mark.xfail(strict=True, reason="no structure check, unclear if we want "
                                       "to return broken data")
def test_fixed_file_trailer_broken_structure(tmpdir, merge_lis_prs):
    """
    Real files situation: Fixed record doesn't match the structure per spaces
    """
    fpath = os.path.join(str(tmpdir), 'FTLR-broken-structure.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-broken-structure.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f, *_):
        with pytest.raises(RuntimeError) as exc:
            _ = f.trailer()
        assert 'structure is broken' in str(exc.value)

def test_fixed_tape_trailer_too_short(tmpdir, merge_lis_prs):
    """
    Real files situation: Fixed record is shorter than expected
    """
    fpath = os.path.join(str(tmpdir), 'TTLR-too-short.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-too-short.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f, *_):
        with pytest.raises(RuntimeError) as exc:
            _ = f.tape.trailer()
        assert 'Expected 126 bytes, raw record is only 124' in str(exc.value)

@pytest.mark.xfail(strict=True, reason="no upper bound check. do we want it?")
def test_fixed_tape_trailer_too_long(tmpdir, merge_lis_prs):
    fpath = os.path.join(str(tmpdir), 'TTLR-too-long.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-too-long.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f, *_):
        with pytest.raises(RuntimeError) as exc:
            _ = f.tape.trailer()
        assert 'Expected 126 bytes, raw record is 138' in str(exc.value)
