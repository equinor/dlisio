"""
Testing 'describe' functionality
"""
from io import StringIO
import os
import pytest

from dlisio import dlis
from dlisio.dlis.utils import *

def test_describe(fpath):
    # Because the .describe() i.e. returns long descriptive textual string,
    # they are hard to test. But the very least test that it is callable.

    with dlis.load(fpath) as batch:
        _ = batch.describe()

        for f in batch:
            _ = f.describe()

            for obj in f.find('.*', '.*'):
                _ = obj.describe(indent='   ', width=70, exclude='e')

def test_replist(f):
    frame = f.object('FRAME', 'FRAME1')
    # If dlisio cannot find a particular object, it will return None. Hence
    # it's not uncommon for lists such as frame.channels to include some Nones.
    # The None is added to simulate a missing object.
    channels = frame.channels + [None]

    names    = replist(channels, 'name')
    typename = replist(channels, 'typename')
    default  = replist(channels, 'not-a-valid-option')

    assert names    == ['CHANN1', 'CHANN2', 'None']
    assert typename == ['Channel(CHANN1)', 'Channel(CHANN2)', 'None']
    assert default  == ['Channel(CHANN1, 10, 0)',
                        'Channel(CHANN2, 10, 0)',
                        'None']

    # Elements that are not a subclass of BasicObjects
    elems = [None , 1, 'str', 2.0]
    reprs = replist(elems, '')
    assert reprs == [str(x) for x in elems]


def test_remove_empties():
    d = {
        "good value"   : "val",
        "empty string" : "",
        "string 0"     : "0",
        "int 0"        : 0,
        "float 0"      : 0.0,
        "None"         : None,

        "good list"              : [2],
        "empty list"             : [],
        "list with empty string" : [""],
        "list with 0"            : [0],
        "list with None"         : [None],

        "good numpy array"              : np.array([5.6]),
        "empty numpy array"             : np.empty(0),
        "numpy array with emtpy string" : np.array([""]),
        "numpy array with 0"            : np.array([0]),
        "numpy array with None"         : np.array(None),

        "empty multidimensional array"     : np.array([['', None], [None, '']]),
        "multidimensional array with zero" : np.array([['', None], [0, '']]),
    }

    expected = [
        "good value",
        "string 0",
        "int 0",
        "float 0",

        "good list",
        "list with 0",

        "good numpy array",
        "numpy array with 0",

        "multidimensional array with zero",
    ]

    clean = remove_empties(d)
    assert clean.keys() == set(expected)


def test_sampled_attrs(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'sampled-attrs.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/ndattrs/set/parameter.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/correct.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/wrong.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/values.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/0.5-1.5-2.5-3.5.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object('PARAMETER', 'OBJECT', 10, 0)
        dims = [2]

        exclude = parseoptions('e')
        buf = StringIO()

        d = OrderedDict()
        d['correct'] = 'CORRECT'
        d['wrong'] = 'WRONG'
        d['drop'] = 'NOT-IN-ATTIC'

        describe_sampled_attrs(
                buf,
                obj.attic,
                dims,
                'VALUES',
                d,
                80,
                ' ',
                exclude
        )

        ref = (' Value(s) : [[0.5 1.5]\n'
               '             [2.5 3.5]]\n'
               ' correct  : 1 2\n'
               '\n'
               ' Invalid dimensions\n'
               ' --\n'
               ' wrong : 1 2 3\n\n'
        )

        assert str(buf.getvalue()) == ref

def test_sampled_attrs_wrong_value(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'sampled-attrs-wrong-value.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/ndattrs/set/parameter.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/values.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/0.5-1.5-2.5.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object('PARAMETER', 'OBJECT', 10, 0)
        dims = [2]

        exclude = parseoptions('e')
        buf = StringIO()

        describe_sampled_attrs(
                buf,
                obj.attic,
                dims,
                'VALUES',
                {},
                80,
                ' ',
                exclude
        )

        ref = (
               ' Invalid dimensions\n'
               ' --\n'
               ' Value(s) : 0.5 1.5 2.5\n\n'
        )

        assert str(buf.getvalue()) == ref


def test_describe_attributes(f):
    obj = f.object('LONG-NAME', 'SHORT-LONG-NAME', 10, 0)

    exclude = parseoptions('')
    buf = StringIO()

    d = OrderedDict()
    d['Simple'] = 'QUANTITY'
    d['Default value'] = 'ENTITY'
    d['Leave as is'] = 'NOT-IN-ATTIC'
    d['Not a string'] = 1

    describe_attributes( buf, d, obj, width=40, indent=' ', exclude=exclude)

    ref = (' Simple        : diameter and stuff\n'
           ' Default value : None\n'
           ' Leave as is   : NOT-IN-ATTIC\n'
           ' Not a string  : 1\n\n'
           )

    assert str(buf.getvalue()) == ref

def test_describe_header():
    # top level header, indented with one whitespace
    case1 = (' -------\n'
             ' Channel\n'
             ' -------\n'
    )

    # section header, indented with one withspace
    case2 = (' Index\n'
             ' --\n'
    )

    buf = StringIO()
    describe_header(buf, 'Channel', width=10, indent=' ', lvl=1)
    assert str(buf.getvalue()) == case1

    buf = StringIO()
    describe_header(buf, 'Index', 10, ' ', lvl=2)
    assert str(buf.getvalue()) == case2

def test_describe_description(f):
    ln  = f.object('LONG-NAME', 'SHORT-LONG-NAME', 10, 0)

    # description is a Longname object
    case1 = (' Description\n'
             ' --\n'
             ' Quantity           : diameter\n'
             '                      and stuff\n'
             ' Source part number : 10\n\n'
    )

    buf = StringIO()
    exclude = parseoptions('e')
    describe_description(buf, ln, width=31, indent=' ', exclude=exclude)
    assert str(buf.getvalue()) == case1

    # description is a string
    case2 = (' Description : string\n'
             '               desc\n\n'
    )

    buf = StringIO()
    describe_description(buf, 'string desc', width=21, indent=' ',
            exclude=exclude)
    assert str(buf.getvalue()) == case2

def test_describe_dict():
    d = OrderedDict()
    d['desc']  = 'long description'
    d['list']  = list(range(10))
    d['empty'] = None


    # dict, indented with one whitespace, wrapped at 20 characters
    case1 = (' desc  : long\n'
             '         description\n'
             ' list  : 0 1 2 3 4 5\n'
             '         6 7 8 9\n'
             ' empty : None\n\n'
    )

    buf = StringIO()
    exclude = parseoptions('')
    describe_dict(buf, d, width=20, indent=' ', exclude=exclude)
    assert str(buf.getvalue()) == case1

    # dict, indented with one whitespace, wrapped at 20 characters, where empty
    # values are ommited
    case2 = (' desc : long\n'
             '        description\n'
             ' list : 0 1 2 3 4 5\n'
             '        6 7 8 9\n\n'
    )

    buf = StringIO()
    exclude = parseoptions('e')
    describe_dict(buf, d, width=20, indent=' ', exclude=exclude)
    assert str(buf.getvalue()) == case2

def test_describe_text():
    text = 'Desc : fra cha'

    # text, indented with a single withspace, wrap on 11 characters, and
    # subindented such that the 'key' matches up with the above
    case1 = (' Desc : fra\n'
             '        cha\n'
    )

    buf = StringIO()
    describe_text(buf, text, 11, ' ', subindent=''.ljust(8))
    assert str(buf.getvalue()) == case1

    # text, indented with a single withspace, wrap on 11 characters, and no
    # subindent. I.e subindent=indent
    case2 = (' Desc : fra\n'
            ' cha\n'
    )

    buf = StringIO()
    describe_text(buf, text, 11, ' ')
    assert str(buf.getvalue()) == case2

def test_describe_array():
    # describe_array should not write anything to the buffer when supplying an
    # empty array with writempty=False
    buf = StringIO()
    describe_array(buf, [], width=80, indent='  ', subindent='  ',
            writeempty=False)

    assert buf.getvalue() == StringIO().getvalue()

    # wrap array on 10 characters and indent it by one whitespace.
    # describe_array should align columns when the elements are of unequal
    # length
    case1 = (' 100  2000\n'
             ' 3000 10\n')

    buf = StringIO()
    arr = [100, 2000, 3000, 10]
    describe_array(buf, arr, width=10, indent=' ')
    assert str(buf.getvalue()) == case1

def test_describe_ndarray():
    # ndarray's should be handled by numpy's array2string

    # A array where each sample is a 2x2 ndarray, indented by one whitespace
    case1 = (' [[[ 100 2000]\n'
             '   [3000   10]]\n'
             '\n'
             '  [[  20   30]\n'
             '   [3000  200]]]\n')

    arr = np.array([[[100, 2000], [3000, 10]], [[20, 30], [3000, 200]]])
    buf = StringIO()
    describe_array(buf, arr, width=20, indent=' ')
    assert str(buf.getvalue()) == case1


@pytest.mark.parametrize('exclude, units', [
    (parseoptions('u'), ''),
    (parseoptions(''),  ' [°]'),
])
def test_describe_attribute_units(f, exclude, units):
    eq = f.object('EQUIPMENT', 'EQUIP1', 10, 0)
    d = OrderedDict()
    d['With units'] = 'TEMPERATURE'

    buf = StringIO()
    describe_attributes( buf, d, eq, width=30, indent=' ', exclude=exclude)
    expected = ' With units : 17{}\n\n'.format(units)
    assert str(buf.getvalue()) == expected


@pytest.mark.parametrize('exclude, units', [
    (parseoptions('u'), ''),
    (parseoptions(''),  ' [units]'),
])
def test_describe_sampled_attribute_units(f, exclude, units):
    param = f.object('PARAMETER', 'PARAM2', 10, 0)
    d = OrderedDict()
    d['With units'] = 'VALUES'

    buf = StringIO()
    describe_sampled_attrs(buf, param.attic, param.dimension, 'VALUES',
        {}, 80, ' ', exclude
    )
    expected = ' Value(s) : [[131  69]]{}\n\n'.format(units)
    assert str(buf.getvalue()) == expected
