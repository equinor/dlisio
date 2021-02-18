import pytest

from dlisio import lis

def test_file_header():
    with lis.load('data/lis/MUD_LOG_1.LIS') as (f, *tail):
        header = f.header()

        assert header.file_name           == 'LIS1  .001'
        assert header.service_sublvl_name == ' '*6
        assert header.version_number      == ' '*8
        assert header.date_of_generation  == ' '*8
        assert header.max_pr_length       == ' 1024'
        assert header.file_type           == ' '*2
        assert header.prev_file_name      == ' '*10

def test_file_trailer():
    with lis.load('data/lis/MUD_LOG_1.LIS') as (f, *tail):
        trailer = f.trailer()

        assert trailer.file_name           == 'LIS1  .001'
        assert trailer.service_sublvl_name == ' '*6
        assert trailer.version_number      == ' '*8
        assert trailer.date_of_generation  == ' '*8
        assert trailer.max_pr_length       == ' 1024'
        assert trailer.file_type           == ' '*2
        assert trailer.next_file_name      == ' '*10

def test_reel_header():
    with lis.load('data/lis/MUD_LOG_1.LIS') as (f, *tail):
        reel = f.reel.header()

        assert reel.service_name        == ' '*6
        assert reel.date                == '09/11/17'
        assert reel.origin_of_data      == ' '*4
        assert reel.name                == 'Georeel '
        assert reel.continuation_number == '01'
        assert reel.prev_reel_name      == ' '*8
        assert reel.comment             == ' '*74

def test_reel_trailer():
    with lis.load('data/lis/MUD_LOG_1.LIS') as (f, *tail):
        reel = f.reel.trailer()

        assert reel.service_name        == ' '*6
        assert reel.date                == '09/11/17'
        assert reel.origin_of_data      == ' '*4
        assert reel.name                == 'Georeel '
        assert reel.continuation_number == '01'
        assert reel.next_reel_name      == ' '*8
        assert reel.comment             == ' '*74

def test_tape_header():
    with lis.load('data/lis/MUD_LOG_1.LIS') as (f, *tail):
        tape = f.tape.header()

        assert tape.service_name        == ' '*6
        assert tape.date                == ' '*8
        assert tape.origin_of_data      == ' '*4
        assert tape.name                == 'Geotape '
        assert tape.continuation_number == '01'
        assert tape.prev_tape_name      == ' '*8
        assert tape.comment             == ' '*74

def test_tape_trailer():
    with lis.load('data/lis/MUD_LOG_1.LIS') as (f, *tail):
        tape = f.tape.trailer()

        assert tape.service_name        == ' '*6
        assert tape.date                == ' '*8
        assert tape.origin_of_data      == ' '*4
        assert tape.name                == 'Geotape '
        assert tape.continuation_number == '01'
        assert tape.next_tape_name      == ' '*8
        assert tape.comment             == ' '*74
