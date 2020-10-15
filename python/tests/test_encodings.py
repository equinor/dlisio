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
            assert obj.attic['DEFAULT_ATTRIBUTE'].values == ['ВАЖНЫЙ-ПАРАМЕТР']
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

def test_broken_utf8_object_fp(tmpdir, merge_files_oneLR):
    # Should be able to create object.fingerprint regardless of
    # encoding
    path = os.path.join(str(tmpdir), 'broken_utf8_object_name.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/broken-utf8-object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    prev_encodings = dlisio.get_encodings()
    dlisio.set_encodings(['koi8_r'])

    try:
        f, = dlisio.load(path)

        # With the correct encoding we should get a nice fingerprint
        obj = f.object('VERY_MUCH_TESTY_SET', 'КАДР')
        assert obj.fingerprint == 'T.VERY_MUCH_TESTY_SET-I.КАДР-O.12-C.0'

        dlisio.set_encodings([])

        # Without an matching encoding we should get a warning and
        # a byte object
        expected = b'T.VERY_MUCH_TESTY_SET-I.\xeb\xe1\xe4\xf2-O.12-C.0'

        with pytest.warns(UnicodeWarning):
            fp = obj.fingerprint

        assert fp == expected
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
            _ = f.object_pool.types

        dlisio.set_encodings(['koi8_r'])
        assert 'СЕТ_КИРИЛЛИЦЕЙ' in f.object_pool.types
        #assert set_name == 'МЕНЯ.ЗОВУТ.СЕТ'
    finally:
        dlisio.set_encodings(prev_encodings)
        f.close()

def test_access_to_object_with_non_utf8_name(tmpdir, merge_files_oneLR):
    # Object with a non-utf8 name can be queried with dlis.object
    # regardless of what encoding is set.

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

        # Can't expect to find an object with an encoded string
        # if the encoding is not given to dlisio
        with pytest.raises(ValueError):
            _ = f.object('VERY_MUCH_TESTY_SET', 'КАДР')

        # However it can be found by matching the bytes
        with pytest.warns(UnicodeWarning):
            obj = f.object('VERY_MUCH_TESTY_SET', b'\xeb\xe1\xe4\xf2')

        assert obj.name == b'\xeb\xe1\xe4\xf2'

        # When the encoding of the string parameter matches the encoding dlisio
        # uses, we should expect to find the object
        dlisio.set_encodings(['koi8_r'])
        obj = f.object('VERY_MUCH_TESTY_SET', 'КАДР')
        assert obj.name == 'КАДР'

    finally:
        dlisio.set_encodings(prev_encodings)
        f.close()

def test_non_utf8_frame():
    # findfdata (and hence load) should _not_ fail because of a non-utf8
    # Frame name. Furthermore, it should be possible to extract the curves of
    # said frame, provided that the right encoding is set.
    fpath = 'data/chap4-7/encoded-obname.dlis'

    prev_encodings = dlisio.get_encodings()
    dlisio.set_encodings(['koi8_r'])

    f, = dlisio.load(fpath)
    try:
        fr = f.object('FRAME', 'ENCODED-[Б╣дTУБ1')
        ch = fr.channels[0]
        curves = fr.curves()

        assert curves[fr.index]       == [1]
        assert curves[ch.fingerprint] == [32915]

    finally:
        dlisio.set_encodings(prev_encodings)
        f.close()
