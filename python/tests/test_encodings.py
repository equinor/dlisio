"""
Testing 'encoding' feature in various levels of representation
(user-facade functionality and underlying logical format)
"""

import pytest
import os

import dlisio
from dlisio import dlis


def test_string_encoding_warns(fpath):
    prev_encodings = dlisio.common.get_encodings()
    try:
        dlisio.common.set_encodings([])
        with pytest.warns(UnicodeWarning):
            with dlis.load(fpath) as (f, *_):
                channel = f.object('CHANNEL', 'CHANN1', 10, 0)
                assert channel.units == b'custom unit\xb0'
    finally:
        dlisio.common.set_encodings(prev_encodings)

def test_string_latin1_encoding_works(fpath):
    prev_encodings = dlisio.common.get_encodings()
    try:
        dlisio.common.set_encodings(['latin1'])
        with dlis.load(fpath) as (f, *_):
            channel = f.object('CHANNEL', 'CHANN1', 10, 0)
            assert channel.units == "custom unit°"
    finally:
        dlisio.common.set_encodings(prev_encodings)


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

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings([])
    with pytest.warns(UnicodeWarning):
        with dlis.load(path) as (f, *_):
            obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT')
            _ = obj['DEFAULT_ATTRIBUTE']
    try:
        dlisio.common.set_encodings(['koi8_r'])
        with dlis.load(path) as (f, *_):
            obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
            assert obj['DEFAULT_ATTRIBUTE'] == ['ВАЖНЫЙ-ПАРАМЕТР']
            assert obj.stash['DEFAULT_ATTRIBUTE'] == ['ВАЖНЫЙ-ПАРАМЕТР']
            assert obj.attic['DEFAULT_ATTRIBUTE'].units == "2 локтя на долю"
    finally:
        dlisio.common.set_encodings(prev_encodings)

def test_broken_utf8_obname_value(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'broken_utf8_obname_value.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/default.dlis.part',
        'data/chap3/object/object.dlis.part',
        'data/chap3/objattr/broken-utf8-obname-value.dlis.part',
    ]
    merge_files_oneLR(path, content)

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings([])

    try:
        f, = dlis.load(path)
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)
        obname = obj['DEFAULT_ATTRIBUTE'][0]

        with pytest.warns(UnicodeWarning):
            _ = obname.id

        dlisio.common.set_encodings(['koi8_r'])
        assert obname.id == 'КОТ'
    finally:
        dlisio.common.set_encodings(prev_encodings)
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

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings([])

    try:
        f, = dlis.load(path)
        with pytest.warns(UnicodeWarning):
            _ = f.find('VERY_MUCH_TESTY_SET', '.*')

        dlisio.common.set_encodings(['koi8_r'])

        objs = f.find('VERY_MUCH_TESTY_SET', '.*')
        [obj] = [x for x in objs]
        assert obj.name == 'КАДР'
    finally:
        dlisio.common.set_encodings(prev_encodings)
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

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings(['koi8_r'])

    try:
        f, = dlis.load(path)

        # With the correct encoding we should get a nice fingerprint
        obj = f.object('VERY_MUCH_TESTY_SET', 'КАДР')
        assert obj.fingerprint == 'T.VERY_MUCH_TESTY_SET-I.КАДР-O.12-C.0'

        dlisio.common.set_encodings([])

        # Without an matching encoding we should get a warning and
        # a byte object
        expected = b'T.VERY_MUCH_TESTY_SET-I.\xeb\xe1\xe4\xf2-O.12-C.0'

        with pytest.warns(UnicodeWarning):
            fp = obj.fingerprint

        assert fp == expected
    finally:
        dlisio.common.set_encodings(prev_encodings)
        f.close()

def test_broken_utf8_label(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'broken_utf8_label.dlis')
    content = [
        'data/chap3/start.dlis.part',
        'data/chap3/template/broken-utf8-label.dlis.part',
        'data/chap3/object/object.dlis.part',
    ]
    merge_files_oneLR(path, content)

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings([])

    try:
        f, = dlis.load(path)
        obj = f.object('VERY_MUCH_TESTY_SET', 'OBJECT', 1, 1)

        with pytest.warns(UnicodeWarning):
            _  = obj.attic.keys()

        dlisio.common.set_encodings(['koi8_r'])
        assert 'ДОХЛЫЙ-ПАРАМЕТР' in obj.attic.keys()
    finally:
        f.close()
        dlisio.common.set_encodings(prev_encodings)

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

    prev_encodings = dlisio.common.get_encodings()

    try:
        # at the moment load uses object_pool.types, so set encoding after load
        f, = dlis.load(path)
        dlisio.common.set_encodings([])

        with pytest.warns(UnicodeWarning):
            _ = f.object_pool.types

        dlisio.common.set_encodings(['koi8_r'])
        assert 'СЕТ_КИРИЛЛИЦЕЙ' in f.object_pool.types
        #assert set_name == 'МЕНЯ.ЗОВУТ.СЕТ'
    finally:
        dlisio.common.set_encodings(prev_encodings)
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

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings([])

    try:
        f, = dlis.load(path)

        # Can't expect to find an object with an encoded string
        # if the encoding is not given to dlisio
        with pytest.raises(ValueError):
            with pytest.warns(UnicodeWarning):
                _ = f.object('VERY_MUCH_TESTY_SET', 'КАДР')

        # However it can be found by matching the bytes
        with pytest.warns(UnicodeWarning):
            obj = f.object('VERY_MUCH_TESTY_SET', b'\xeb\xe1\xe4\xf2')

        assert obj.name == b'\xeb\xe1\xe4\xf2'

        # When the encoding of the string parameter matches the encoding dlisio
        # uses, we should expect to find the object
        dlisio.common.set_encodings(['koi8_r'])
        obj = f.object('VERY_MUCH_TESTY_SET', 'КАДР')
        assert obj.name == 'КАДР'

    finally:
        dlisio.common.set_encodings(prev_encodings)
        f.close()

def test_non_utf8_frame():
    # findfdata (and hence load) should _not_ fail because of a non-utf8
    # Frame name. Furthermore, it should be possible to extract the curves of
    # said frame, provided that the right encoding is set.
    fpath = 'data/chap4-7/encoded-obname.dlis'

    prev_encodings = dlisio.common.get_encodings()
    dlisio.common.set_encodings(['koi8_r'])

    f, = dlis.load(fpath)
    try:
        fr = f.object('FRAME', 'ENCODED-[Б╣дTУБ1')
        ch = fr.channels[0]
        curves = fr.curves()

        assert curves[fr.index]       == [1]
        assert curves[ch.fingerprint] == [32915]

    finally:
        dlisio.common.set_encodings(prev_encodings)
        f.close()
