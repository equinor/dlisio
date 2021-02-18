import pytest

from dlisio import lis

def test_file_header():
    with lis.load('data/lis/MUD_LOG_1.LIS') as (_, f, *tail):
        header = f.header()

        assert header.file_name           == 'LIS1  .001'
        assert header.service_sublvl_name == ' '*6
        assert header.version_number      == ' '*8
        assert header.date_of_generation  == ' '*8
        assert header.max_pr_length       == ' 1024'
        assert header.file_type           == ' '*2
        assert header.prev_file_name      == ' '*10

def test_file_trailer():
    with lis.load('data/lis/MUD_LOG_1.LIS') as (_, f, *tail):
        trailer = f.trailer()

        assert trailer.file_name           == 'LIS1  .001'
        assert trailer.service_sublvl_name == ' '*6
        assert trailer.version_number      == ' '*8
        assert trailer.date_of_generation  == ' '*8
        assert trailer.max_pr_length       == ' 1024'
        assert trailer.file_type           == ' '*2
        assert trailer.next_file_name      == ' '*10
