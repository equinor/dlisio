import numpy as np
import pytest
from datetime import datetime

import dlisio
from dlisio.plumbing import *
from io import StringIO

def test_sampling_scalar_dims():
    raw = [1, 2, 3, 4, 5, 6]
    dimensions = [1]

    samples = sampling(raw, dimensions)

    assert samples[0]   == 1
    assert np.array_equal(samples[1:5], np.array([2, 3, 4, 5]))
    assert samples[-1]  == 6

def test_sampling_array_dims():
    raw = [1, 2, 3, 4, 5, 6]

    dimensions = [3]
    samples = sampling(raw, dimensions)
    assert np.array_equal(samples[0], np.array(raw[0:3]))
    assert np.array_equal(samples[1], np.array(raw[3:6]))

    dimensions = [6]
    samples = sampling(raw, dimensions)
    assert np.array_equal(samples[0], np.array(raw))

    dimensions = [2,3]
    samples = sampling(raw, dimensions)
    assert np.array_equal(samples[0][0], np.array(raw[0:3]))
    assert np.array_equal(samples[0][1], np.array(raw[3:6]))

    dimensions = [3, 2]
    samples = sampling(raw, dimensions)
    assert np.array_equal(samples[0][0], np.array(raw[0:2]))
    assert np.array_equal(samples[0][1], np.array(raw[2:4]))
    assert np.array_equal(samples[0][2], np.array(raw[4:6]))

def test_sampling_single(assert_log):
    raw = [1, 2]
    dimensions = [2]

    sample = sampling(raw, dimensions, single=True)
    assert np.array_equal(sample, np.array([1, 2]))

    dimensions = [1]

    sample = sampling(raw, dimensions, single=True)
    assert sample == 1
    assert_log('found 2 samples, should be 1')

def test_validshape_no_dims():
    dimensions = []

    # posible to infer dimensions
    raw = [3.14]
    shape = validshape(raw, dimensions)
    assert shape  == [1]

    # not posible to infer dimensions
    raw = [3.14, 2]
    with pytest.raises(ValueError):
        _ = validshape(raw, dimensions)

    # possible if count is correctly specified
    shape = validshape(raw, dimensions, samplecount=2)
    assert shape == [1]

    with pytest.raises(ValueError):
        _ = validshape(raw, dimensions, samplecount=3)

def test_validshape_inconsistent_dims():
    # In data has too few elements
    raw        = [1, 2]
    dimensions = [3]

    with pytest.raises(ValueError):
        _ = validshape(raw, dimensions)

    # In data has too many elements
    raw        = [1, 2, 3]
    dimensions = [2]

    with pytest.raises(ValueError):
        _ = validshape(raw, dimensions)

def test_issequence():
    assert not issequence('seq')
    assert not issequence("seq")
    assert not issequence("""seq""")
    assert not issequence(bytes(1))

    assert issequence([1])
    assert issequence(np.array([1]))

def test_remove_empties():
    d = OrderedDict()
    d['a'] = 0
    d['b'] = 1
    d['c'] = None
    d['d'] = np.empty(0)
    d['e'] = []
    d['f'] = 'str'
    d['g'] = ''
    d['h'] = ""

    ref = OrderedDict()
    ref['a'] = 0
    ref['b'] = 1
    ref['f'] = 'str'

    clean = remove_empties(d)
    assert clean == ref

def test_replist():
    ch1 = Channel(name='TIME')
    ch1.origin = 1
    ch1.copynumber = 0

    ch2 = Channel(name='TDEP')
    ch2.origin = 1
    ch2.copynumber = 1

    channels = [ch1, ch2, None]
    names    = replist(channels, 'name')
    typename = replist(channels, 'typename')
    default  = replist(channels, 'not-a-valid-option')

    assert names    == ['TIME', 'TDEP', 'None']
    assert typename == ['Channel(TIME)', 'Channel(TDEP)', 'None']
    assert default  == ['Channel(TIME, 1, 0)', 'Channel(TDEP, 1, 1)', 'None']

    # Elements that are not a subclass of BasicObjects
    elems = [None , 1, 'str', 2.0]
    reprs = replist(elems, '')
    assert reprs == [str(x) for x in elems]

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

def test_sampled_attrs():
    attic = {
        'CORRECT' : [1, 2],
        'WRONG'   : [5, 6, 7],
        'VALUES'  : [0.5, 0.6, 0.7, 0.8]
    }
    dims = [2]

    exclude = parseoptions('e')
    buf = StringIO()

    d = OrderedDict()
    d['correct'] = 'CORRECT'
    d['wrong'] = 'WRONG'
    d['drop'] = 'NOT-IN-ATTIC'

    describe_sampled_attrs(
            buf,
            attic,
            dims,
            'VALUES',
            d,
            80,
            ' ',
            exclude
    )

    ref = (' Value(s) : [[0.5 0.6]\n'
           '             [0.7 0.8]]\n'
           ' correct  : 1 2\n'
           '\n'
           ' Invalid dimensions\n'
           ' --\n'
           ' wrong : 5 6 7\n\n'
    )

    assert str(buf.getvalue()) == ref

def test_sampled_attrs_wrong_value():
    attic = {'VALUES' : [0.5, 0.6, 0.7]}
    dims = [2]

    exclude = parseoptions('e')
    buf = StringIO()

    describe_sampled_attrs(
            buf,
            attic,
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
           ' Value(s) : 0.5 0.6 0.7\n\n'
    )

    assert str(buf.getvalue()) == ref

def test_describe_description():
    ln = Longname()
    ln.quantity       = 'diameter and stuff'
    ln.source_part_nr = 10

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

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_empty(obj):
    obj.attic = {'VALUES' : [], 'DIMENSION' : [], 'ZONES' : []}

    obj.load()
    assert np.array_equal(obj.values, np.empty(0))
    assert obj.dimension == []
    assert obj.axis      == []
    assert obj.zones     == []

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_dimension(obj):
    obj.attic = {'VALUES' : [], 'DIMENSION' : [1], 'ZONES' : []}

    obj.load()
    assert np.array_equal(obj.values, np.empty(0))
    assert obj.dimension == [1]
    assert obj.axis      == []
    assert obj.zones     == []

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_simple(obj):
    obj.attic = {'VALUES' : [14], 'DIMENSION' : [1], 'ZONES' : []}

    obj.load()
    assert obj.values[0] == 14

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_infer_simple(obj):
    obj.attic = {'VALUES' : [14], 'DIMENSION' : [], 'ZONES' : []}

    obj.load()
    assert obj.values[0] == 14

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_one_sample(obj):
    obj.attic = {'VALUES' : [1, 2], 'DIMENSION' : [2], 'ZONES' : []}

    obj.load()
    assert list(obj.values[0]) == [1, 2]

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_wrong_dimensions(obj):
    obj.attic = {'VALUES' : [1, 2, 3, 4, 5], 'DIMENSION' : [2], 'ZONES' : []}

    obj.load()
    msg  = 'cannot reshape array of size 5 into shape [2]'
    with pytest.raises(ValueError) as error:
        _ = obj.values
    assert str(error.value) == msg
    assert np.array_equal(obj.attic['VALUES'], np.array([1, 2, 3, 4, 5]))

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_wrong_dimensions_wrong_zones(obj):
    obj.attic = {'VALUES' : [1, 2, 3, 4, 5], 'DIMENSION' : [2], 'ZONES' : []}

    obj.load()
    obj.zones = [None for _ in range(4)]

    msg  = 'cannot reshape array of size 5 into shape [2]'
    with pytest.raises(ValueError) as error:
        _ = obj.values
    assert str(error.value) == msg
    assert np.array_equal(obj.attic['VALUES'], np.array([1, 2, 3, 4, 5]))

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_infer_dimensions_from_zones(obj):
    obj.attic = {'VALUES' : [1, 2, 3, 4, 5], 'DIMENSION' : [], 'ZONES' : []}

    obj.load()

    # Should be able to infer correct dimension from zones
    obj.zones = [None for _ in range(5)]
    assert np.array_equal(obj.values, np.array([1, 2, 3, 4, 5]))
    assert np.array_equal(obj.attic['VALUES'], np.array([1, 2, 3, 4, 5]))

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_no_dimensions_wrong_zones(obj):
    obj.attic = {'VALUES' : [1], 'DIMENSION' : [], 'ZONES' : []}

    obj.load()

    # Should use dimension over zones
    obj.zones = [None for _ in range(2)]
    assert np.array_equal(obj.values, np.array([1]))
    assert np.array_equal(obj.attic['VALUES'], np.array([1]))

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_right_dimensions_wrong_zones(obj):
    obj.attic = {'VALUES' : [1, 2, 3, 4], 'DIMENSION' : [2], 'ZONES' : []}

    obj.load()

    # Should use dimension over zones
    obj.zones = [None for _ in range(5)]
    assert np.array_equal(obj.values, np.array([[1, 2 ], [3, 4]]))
    assert np.array_equal(obj.attic['VALUES'], np.array([1, 2, 3, 4]))

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_right_dimensions_right_zones(obj):
    obj.attic = {'VALUES' : [1, 2, 3, 4], 'DIMENSION' : [2], 'ZONES' : []}

    obj.load()
    obj.zones = [None for _ in range(2)]

    assert np.array_equal(obj.values, np.array([[1, 2 ], [3, 4]]))
    assert np.array_equal(obj.attic['VALUES'], np.array([1, 2, 3, 4]))

@pytest.mark.parametrize('obj', [Parameter(), Computation()])
def test_values_multidim_values(obj):
    obj.attic = {'VALUES' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                   'DIMENSION' : [2, 3], 'ZONES' : []}

    obj.load()

    assert list(obj.values[0][1]) == [3, 4]
    assert list(obj.values[1][2]) == [11, 12]
    assert obj.dimension          == [3, 2]

@pytest.mark.parametrize('value', [
    (7),
    (1.3),
    (False),
    ('val1'),
    ((3.2, 6.2)),
    (complex(22.6, 2.1)),
    (datetime(2003, 12, 3, 14, 15, 57))
])
def test_parameter_computation_repcode(value):
    param = Parameter()
    param.attic = {'DIMENSION' : [], 'ZONES' : []}

    param.attic['VALUES'] = [value]
    param.load()

    assert np.array_equal(param.values[0], value)

    comput = Computation()
    comput.attic = {'DIMENSION' : [], 'ZONES' : []}
    comput.attic['VALUES'] = [value]
    comput.load()
    assert np.array_equal(comput.values[0], value)

def test_measurement_empty():
    m = Measurement()
    m.attic = {'MEASUREMENT' : [], 'REFERENCE' : [], 'DIMENSION' : []}

    m.load()
    assert m.samples.size       == 0
    assert m.reference.size     == 0
    assert m.std_deviation.size == 0
    assert m.dimension          == []
    assert m.axis               == []

def test_measurement_dimension():
    m = Measurement()
    m.attic = {'MEASUREMENT' : [], 'DIMENSION' : [3, 5]}

    m.load()
    assert m.samples.size   == 0
    assert m.reference.size == 0
    assert m.dimension      == [5, 3]
    assert m.axis           == []

def test_measurement_wrong_dimension_samples():
    m = Measurement()
    m.attic = {'MEASUREMENT' : [1, 2, 3], 'DIMENSION' : [3, 5]}

    m.load()

    msg = 'cannot reshape array of size 3 into shape [5, 3]'
    with pytest.raises(ValueError) as error:
        _ = m.samples

    assert str(error.value) == msg
    assert m.attic['MEASUREMENT'] == [1, 2, 3]
    assert m.dimension == [5, 3]

def test_measurement_many_samples():
    m = Measurement()
    m.attic = {
        'MEASUREMENT'       : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'MAXIMUM-DEVIATION' : [2, 3, 2, 1],
        'STANDARD-DEVIATION': [3, 2, 5, 6],
        'REFERENCE'         : [3, 6, 9, 12],
        'PLUS-TOLERANCE'    : [0.4, 0.2, 0.1, 0.3],
        'MINUS-TOLERANCE'   : [0.5, 0.1, 0, 1],
        'DIMENSION'         : [4]
    }

    m.load()

    assert np.array_equal(m.samples[0], np.array([1, 2, 3, 4]))
    assert np.array_equal(m.samples[1], np.array([5, 6, 7, 8]))
    assert np.array_equal(m.samples[2], np.array([9, 10, 11, 12]))

    assert np.array_equal(m.max_deviation  , np.array([2, 3, 2, 1]))
    assert np.array_equal(m.std_deviation  , np.array([3, 2, 5, 6]))
    assert np.array_equal(m.reference      , np.array([3, 6, 9, 12]))
    assert np.array_equal(m.plus_tolerance , np.array([0.4, 0.2, 0.1, 0.3]))
    assert np.array_equal(m.minus_tolerance, np.array([0.5, 0.1, 0, 1]))

def test_measurement_non_corresponding_values():
    m = Measurement()
    m.attic = {
        'MEASUREMENT'       : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        'MAXIMUM-DEVIATION' : [2, 3, 2],
        'STANDARD-DEVIATION': [3, 2],
        'REFERENCE'         : [3, 6],
        'PLUS-TOLERANCE'    : [0.4, 0.2, 0.1, 0.3, 0.5],
        'MINUS-TOLERANCE'   : [0.5, 0.1, 0],
        'DIMENSION'         : [4]
    }

    m.load()

    msg = 'cannot reshape array of size {} into shape 4'
    with pytest.raises(ValueError) as error:
        _ = m.samples
        assert error.value == msg.format(11)

    with pytest.raises(ValueError) as error:
        _ = m.max_deviation
        assert error.value == msg.format(3)

    with pytest.raises(ValueError) as error:
        _ = m.std_deviation
        assert error.value == msg.format(2)

    with pytest.raises(ValueError) as error:
        _ = m.reference
        assert error.value == msg.format(2)

    with pytest.raises(ValueError) as error:
        _ = m.plus_tolerance
        assert error.value == msg.format(5)

    with pytest.raises(ValueError) as error:
        _ = m.minus_tolerance
        assert error.value == msg.format(3)

def test_measurement_more_than_one_sample(assert_log):
    m = Measurement()
    m.attic = {
        'MEASUREMENT'       : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'MAXIMUM-DEVIATION' : [2, 3, 1, 3],
        'STANDARD-DEVIATION': [3, 2, 1, 3, 4, 5],
        'REFERENCE'         : [3, 6, 3, 4, 5, 1, 9, 6],
        'PLUS-TOLERANCE'    : [4, 2, 1, 3, 5, 6, 5, 7, 2, 1],
        'MINUS-TOLERANCE'   : [5, 2, 3, 6, 2, 2, 2, 4, 6, 7, 9, 1],
        'DIMENSION'         : [2]
    }

    m.load()

    assert np.array_equal(m.samples[2], np.array([5, 6]))

    msg = 'found {} samples, should be 1'
    _ = m.max_deviation
    assert_log(msg.format(2))

    _ = m.std_deviation
    assert_log(msg.format(3))

    _ = m.reference
    assert_log(msg.format(4))

    _ = m.plus_tolerance
    assert_log(msg.format(5))

    _ = m.minus_tolerance
    assert_log(msg.format(6))

@pytest.mark.parametrize('reference, samples', [
    ([1, 2], [3, 4, 5, 6]),
    ([1.1, 2.2], [3.3, 4.4, 5.5, 6.6]),
    ([True, False], [True, False, True, False]),
    (['val1', 'val2'], ['val3', 'val4', 'val5', 'val6']),
    ([(1, 1), (2, 2)], [(3, 3), (4, 4), (5, 5), (6, 6)]),
    ([complex(1, 1), complex(2, 2)],
     [complex(3, 3), complex(4, 4), complex(5, 5), complex(6, 6)]),
    ([datetime(1991, 1, 1), datetime(1992, 2, 2)],
     [datetime(1993, 3, 3), datetime(1994, 4, 4),
      datetime(1995, 5, 5), datetime(1996, 6, 6)])
])
def test_measurement_repcode(reference, samples):
    m = Measurement()
    m.attic = {'DIMENSION' : [2]}

    m.attic['MEASUREMENT'] = samples
    m.attic['REFERENCE'] = reference
    m.load()

    assert np.array_equal(np.array(reference), m.reference)
    sampled = [samples[0:2], samples[2:4]]
    assert np.array_equal(np.array(sampled), m.samples)
