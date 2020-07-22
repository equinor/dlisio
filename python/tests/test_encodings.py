"""
Testing 'encoding' feature in various levels of representation
(user-facade functionality and underlying logical format)
"""

import pytest
import os

import dlisio


def test_string_encoding_warns(fpath):
    prev_encodings = dlisio.get_encodings()
    try:
        dlisio.set_encodings([])
        with pytest.warns(UnicodeWarning):
            with dlisio.load(fpath) as (f, *_):
                channel = f.object('CHANNEL', 'CHANN1', 10, 0)
                assert channel.units == b'custom unit\xb0'
    finally:
        dlisio.set_encodings(prev_encodings)

def test_string_latin1_encoding_works(fpath):
    prev_encodings = dlisio.get_encodings()
    try:
        dlisio.set_encodings(['latin1'])
        with dlisio.load(fpath) as (f, *_):
            channel = f.object('CHANNEL', 'CHANN1', 10, 0)
            assert channel.units == "custom unit°"
    finally:
        dlisio.set_encodings(prev_encodings)


@pytest.mark.future_test_attributes
def test_broken_utf8_value(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'broken_utf8_value.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/broken-utf8-value.dlis.part',
    ]
    merge_files_oneLR(path, content)

    prev_encodings = dlisio.get_encodings()
    dlisio.set_encodings([])
    with pytest.warns(UnicodeWarning):
        with dlisio.load(path) as (f, *_):
            obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT')
            _ = obj['DEFAULT_ATTRIBUTE']
    try:
        dlisio.set_encodings(['koi8_r'])
        with dlisio.load(path) as (f, *_):
            obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
            assert obj.attic['DEFAULT_ATTRIBUTE'] == ['ВАЖНЫЙ-ПАРАМЕТР']
            assert obj.stash['DEFAULT_ATTRIBUTE'] == ['ВАЖНЫЙ-ПАРАМЕТР']
            #assert units == "2 локтя на долю"
    finally:
        dlisio.set_encodings(prev_encodings)

def test_broken_utf8_obname_value(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'broken_utf8_obname_value.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/broken-utf8-obname-value.dlis.part',
    ]
    merge_files_oneLR(path, content)

    prev_encodings = dlisio.get_encodings()
    dlisio.set_encodings([])

    try:
        f, = dlisio.load(path)
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obname = obj['DEFAULT_ATTRIBUTE'][0]

        with pytest.warns(UnicodeWarning):
            _ = obname.id

        dlisio.set_encodings(['koi8_r'])
        assert obname.id == 'КОТ'
    finally:
        dlisio.set_encodings(prev_encodings)
        f.close()

def test_broken_utf8_object_name(tmpdir, merge_files_oneLR):
    #some actual files have obname which fails with utf-8 codec
    path = os.path.join(str(tmpdir), 'broken_utf8_object_name.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/broken-utf8-object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    prev_encodings = dlisio.get_encodings()
    dlisio.set_encodings([])

    try:
        f, = dlisio.load(path)
        with pytest.warns(UnicodeWarning):
            _ = f.match('.*', 'VERY_MUCH_TESTY_SET')

        dlisio.set_encodings(['koi8_r'])

        objs = f.match('.*', 'VERY_MUCH_TESTY_SET')
        [obj] = [x for x in objs]
        assert obj.name == 'КАДР'
    finally:
        dlisio.set_encodings(prev_encodings)
        f.close()

def test_broken_utf8_label(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'broken_utf8_label.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/broken-utf8-label.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    prev_encodings = dlisio.get_encodings()
    dlisio.set_encodings([])

    try:
        f, = dlisio.load(path)
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)

        with pytest.warns(UnicodeWarning):
            _  = obj.attic.keys()

        dlisio.set_encodings(['koi8_r'])
        assert 'ДОХЛЫЙ-ПАРАМЕТР' in obj.attic.keys()
    finally:
        f.close()
        dlisio.set_encodings(prev_encodings)

@pytest.mark.future_test_set_names
def test_broken_utf8_set(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'broken_utf8_set.dlis')
    content = [
        'data/chap3/sul.dlis.part',
        'data/chap3/set/broken-utf8-set.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    prev_encodings = dlisio.get_encodings()
    dlisio.set_encodings([])

    try:
        f, = dlisio.load(path)
        with pytest.warns(UnicodeWarning):
            _ = f.metadata.types

        dlisio.set_encodings(['koi8_r'])
        assert 'СЕТ_КИРИЛЛИЦЕЙ' in f.metadata.types
        #assert set_name == 'МЕНЯ.ЗОВУТ.СЕТ'
    finally:
        dlisio.set_encodings(prev_encodings)
        f.close()


