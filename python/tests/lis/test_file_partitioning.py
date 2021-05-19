import os

from dlisio import lis

def test_1reel_1tape(tmpdir, merge_lis_prs):
    # A well formatted, simple file
    #
    # file.lis
    # |
    # |->Reel 1
    #    |-> Tape 1
    #        |-> Logical File 1
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), '1reel1tape.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 1 and Tape 1
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == ' '*8
        assert f2.tape.trailer().next_tape_name == 'Tape0002'
        assert f2.reel.header().prev_reel_name  == ' '*8
        assert f2.reel.trailer().next_reel_name == 'Reel5678'

def test_1reel_2tape(tmpdir, merge_lis_prs):
    # A well formatted, simple file
    #
    # file.lis
    # |
    # |->Reel 1
    #    |-> Tape 1
    #    |   |-> Logical File 1
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), '1reel2tape.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/THLR-2.lis.part',
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
        'data/lis/records/TTLR-2.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 1 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == 'Tape0001'
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header().prev_reel_name  == ' '*8
        assert f2.reel.trailer().next_reel_name == 'Reel5678'

def test_2reel_1tape(tmpdir, merge_lis_prs):
    # A well formatted, simple file
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), '2reel1tape.lis')
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
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == 'Tape0001'
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header().prev_reel_name  == 'Reel1234'
        assert f2.reel.trailer().next_reel_name == ' '*8

def test_missing_fhlr(tmpdir, merge_lis_prs, assert_log):
    # A file with missing delimiter:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing_first_rh.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        # Missing first FHLR
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
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header()            == None
        assert_log('No File Header Logical Record')
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == 'Tape0001'
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header().prev_reel_name  == 'Reel1234'
        assert f2.reel.trailer().next_reel_name == ' '*8

def test_missing_ftlr(tmpdir, merge_lis_prs, assert_info):
    # A file with missing delimiter:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing_first_rh.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        # Missing first FTLR
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
        'data/lis/records/RHLR-2.lis.part',
        'data/lis/records/THLR-2.lis.part',
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
        'data/lis/records/TTLR-2.lis.part',
        'data/lis/records/RTLR-2.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer()           == None
        assert_info('No File Trailer Logical Record')
        print(f1.explicits())
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == 'Tape0001'
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header().prev_reel_name  == 'Reel1234'
        assert f2.reel.trailer().next_reel_name == ' '*8

def test_missing_first_rhlr(tmpdir, merge_lis_prs):
    # A file with missing delimiter:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing_first_rh.lis')
    content = [
        # Missing first RHLR
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
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header()                 == None
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == 'Tape0001'
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header().prev_reel_name  == 'Reel1234'
        assert f2.reel.trailer().next_reel_name == ' '*8

def test_missing_other_rhlr(tmpdir, merge_lis_prs, assert_log):
    # A file with missing delimiter:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing_other_rh.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
        # Missing non-first (last in this case) RHLR
        'data/lis/records/THLR-2.lis.part',
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
        'data/lis/records/TTLR-2.lis.part',
        'data/lis/records/RTLR-2.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == 'Tape0001'
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header()                 == None
        assert_log('Missing Header Record')
        assert f2.reel.trailer().next_reel_name == ' '*8

def test_missing_last_rtlr(tmpdir, merge_lis_prs, assert_info):
    # A file with missing delimiter:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing_last_rt.lis')
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
        # Missing last RTLR
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == 'Tape0001'
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header().prev_reel_name  == 'Reel1234'
        assert f2.reel.trailer()                == None
        assert_info('No (optional) Trailer Record present')

def test_missing_other_rtlr(tmpdir, merge_lis_prs, assert_info):
    # A file with missing delimiter:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing_other_rt.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        # Missing non-last (first in this case) RTLR
        'data/lis/records/RHLR-2.lis.part',
        'data/lis/records/THLR-2.lis.part',
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
        'data/lis/records/TTLR-2.lis.part',
        'data/lis/records/RTLR-2.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer() == None
        assert_info('No (optional) Trailer Record present')

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == 'Tape0001'
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header().prev_reel_name  == 'Reel1234'
        assert f2.reel.trailer().next_reel_name == ' '*8

def test_missing_other_thlr(tmpdir, merge_lis_prs, assert_log):
    # A file with missing delimiter:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing_other_th.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
        'data/lis/records/RHLR-2.lis.part',
        # Missing non-first (last in this case) THLR
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
        'data/lis/records/TTLR-2.lis.part',
        'data/lis/records/RTLR-2.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header()                 == None
        assert_log('Missing Header Record')
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header().prev_reel_name  == 'Reel1234'
        assert f2.reel.trailer().next_reel_name == ' '*8

def test_missing_other_ttlr(tmpdir, merge_lis_prs, assert_info):
    # A file with missing delimiter:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing_other_tt.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        # Missing non-last (in this case the first) TTLR
        'data/lis/records/RTLR-1.lis.part',
        'data/lis/records/RHLR-2.lis.part',
        'data/lis/records/THLR-2.lis.part',
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
        'data/lis/records/TTLR-2.lis.part',
        'data/lis/records/RTLR-2.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header().prev_tape_name  == ' '*8
        assert f1.tape.trailer()                == None
        assert_info('No (optional) Trailer Record present')
        assert f1.reel.header().prev_reel_name  == ' '*8
        assert f1.reel.trailer().next_reel_name == 'Reel5678'

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header().prev_tape_name  == 'Tape0001'
        assert f2.tape.trailer().next_tape_name == ' '*8
        assert f2.reel.header().prev_reel_name  == 'Reel1234'
        assert f2.reel.trailer().next_reel_name == ' '*8

def test_missing_many_delimiters(tmpdir, merge_lis_prs):
    # A file with missing delimiter:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing_many_delimiters.lis')
    content = [
        # Missing first RHLR
        # Missing first THLR
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        # Missing non-last (in this case the first) RTLR
        'data/lis/records/RHLR-2.lis.part',
        # Missing non-first (in this case the last) THLR
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
        # Missing last TTLR
        # Missing last RTLR
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header()                 == None
        assert f1.tape.trailer().next_tape_name == 'Tape0002'
        assert f1.reel.header()                 == None
        assert f1.reel.trailer()                == None

        # f2 belongs to Reel 2 and Tape 2
        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header()                 == None
        assert f2.tape.trailer()                == None
        assert f2.reel.header().prev_reel_name  == 'Reel1234'
        assert f2.reel.trailer()                == None

def test_nodelimiters(tmpdir, merge_lis_prs, assert_log):
    # A file that misses all delimiters:
    #
    # file.lis
    # |
    # |->Reel 1
    # |  |-> Tape 1
    # |      |-> Logical File 1
    # |->Reel 2
    #    |-> Tape 2
    #        |-> Logical File 2
    #
    # This is now essentially just a file with 2 Logical Files without tape or
    # reel information. I.e. all structure is lost
    fpath = os.path.join(str(tmpdir), 'nodelimiters.lis')
    content = [
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/FHLR-2.lis.part',
        'data/lis/records/FTLR-2.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0
        #  Check that f1, f2 is partitioned correctly by investigating their
        #  FHLR/FTLR.
        #  Check that f1, f2 "belongs" to the correct Reel and Tape by
        #  investigating the assigned RHLR/RTLR and THLR/TTLR. The fields
        #  checked are arbitrary as long as they can uniquely identify the
        #  record.

        assert f1.header().file_name  == 'LISTST.001'
        assert f1.trailer().file_name == 'LISTST.001'
        assert f1.tape.header()  == None
        assert f1.tape.trailer() == None
        assert f1.reel.header()  == None
        assert f1.reel.trailer() == None

        assert f2.header().file_name  == 'LISTST.002'
        assert f2.trailer().file_name == 'LISTST.002'
        assert f2.tape.header()  == None
        assert f2.tape.trailer() == None
        assert f2.reel.header()  == None
        assert f2.reel.trailer() == None

def test_missing_logical_file(tmpdir, merge_lis_prs):
    # Real-world example:
    #
    # file.lis
    # |
    # |->Reel 1
    #    |-> Tape 1
    #        |-> data (seen as Logical File 1)
    #        |-> Logical File 2
    #
    fpath = os.path.join(str(tmpdir), 'missing-logical-file.lis')
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/wellsite-data.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(fpath, content)

    with lis.load(fpath) as (f1, f2, *tail):
        assert len(tail) == 0

        # f1 belongs to Reel 1 and Tape 1
        assert f1.header()  == None
        assert f1.trailer() == None
        assert f1.tape.header().name  == 'Tape0001'
        assert f1.tape.trailer().name == 'Tape0001'
        assert f1.reel.header().name  == 'Reel1234'
        assert f1.reel.trailer().name == 'Reel1234'
        assert len(f1.explicits()) == 1

        # f2 belongs to Reel 1 and Tape 1
        assert f2.header().file_name  == 'LISTST.001'
        assert f2.trailer().file_name == 'LISTST.001'
        assert f2.tape.header().name  == 'Tape0001'
        assert f2.tape.trailer().name == 'Tape0001'
        assert f2.reel.header().name  == 'Reel1234'
        assert f2.reel.trailer().name == 'Reel1234'
