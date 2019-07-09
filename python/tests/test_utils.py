import numpy as np
import pytest
from datetime import datetime

import dlisio
from dlisio.plumbing import sampling

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

def test_sampling_no_dims():
    dimensions = []

    # posible to infer dimensions
    raw = [3.14]
    samples = sampling(raw, dimensions)
    assert samples[0] == 3.14

    # not posible to infer dimensions
    raw = [3.14, 2]
    with pytest.raises(ValueError):
        _ = sampling(raw, dimensions)

    # possible if count is correctly specified
    samples = sampling(raw, dimensions, count=2)
    assert samples[0] == 3.14
    assert samples[1] == 2
    assert len(samples) == 2

    with pytest.raises(ValueError):
        _ = sampling(raw, dimensions, count=3)

def test_sampling_inconsistent_dims():
    # In data has too few elements
    raw        = [1]
    dimensions = [2]

    with pytest.raises(ValueError):
        _ = sampling(raw, dimensions)

    # In data has too many elements
    raw        = [1, 2, 3]
    dimensions = [2]

    with pytest.raises(ValueError):
        _ = sampling(raw, dimensions)

def test_zonelabels():
    from dlisio.plumbing import zonelabels

    zone_a = dlisio.plumbing.Zone(name='ZONE-A')
    zone_a.copynumber = 10
    zone_a.origin = 0

    zone_a1 = dlisio.plumbing.Zone(name='ZONE-A')
    zone_a1.copynumber = 10
    zone_a1.origin = 1

    zone_b = dlisio.plumbing.Zone(name='ZONE-B')

    zones = [zone_a, zone_b]
    labels = zonelabels(zones, 'DEFAULT')
    assert list(labels) == ['ZONE-A', 'ZONE-B']

    zones = [zone_a, None, zone_b]
    labels = zonelabels(zones, 'DEFAULT')
    assert list(labels)  == ['ZONE-A', 'DEFAULT1', 'ZONE-B']

    zones = [zone_a, None, zone_b, None]
    labels = zonelabels(zones, 'DEFAULT')
    assert list(labels) == ['ZONE-A', 'DEFAULT1', 'ZONE-B', 'DEFAULT3']

    zones = [zone_a, zone_a1, zone_b]
    labels = zonelabels(zones, 'DEFAULT')
    assert list(labels) == ['ZONE-A.0.10', 'ZONE-A.1.10', 'ZONE-B']

    zones = [zone_a, zone_a, zone_b]
    labels = zonelabels(zones, 'DEFAULT')
    assert list(labels) == ['ZONE-A.0.10', 'ZONE-A.0.10', 'ZONE-B']

    zones = [zone_a, zone_a, zone_a]
    labels = zonelabels(zones, 'DEFAULT')
    assert list(labels) == ['ZONE-A.0.10', 'ZONE-A.0.10', 'ZONE-A.0.10']

def test_parameter_empty():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [], 'DIMENSION' : [], 'AXIS' : [], 'ZONES' : []}

    param.load()
    assert list(param.values['RAW']) == []
    assert param.dimension == []
    assert param.axis      == []
    assert param.zones     == []

def test_parameter_dimension():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [], 'DIMENSION' : [1], 'AXIS' : [], 'ZONES' : []}

    param.load()
    assert list(param.values['RAW']) == []
    assert param.dimension == [1]
    assert param.axis      == []
    assert param.zones     == []

def test_parameter_values():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2],
                   'DIMENSION' : [2], 'AXIS' : [], 'ZONES' : []}

    param.load()
    assert list(param.values['DLISIO-UNZONED']) == [1, 2]

def test_parameter_zones_values():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'

    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2, 3, 4],
                   'DIMENSION' : [2], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.zones = [zone_a, zone_b]

    assert list(param.values['ZONE-A']) == [1, 2]
    assert list(param.values['ZONE-B']) == [3, 4]

def test_parameter_copied_zones_values():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2, 3],
                   'DIMENSION' : [1], 'AXIS' : [], 'ZONES' : []}

    param.load()

    zone_a = dlisio.plumbing.Zone()
    zone_a.name       = 'ZONE-A'
    zone_a.origin     = 10
    zone_a.copynumber = 0

    zone_a2 = dlisio.plumbing.Zone()
    zone_a2.name       = 'ZONE-A'
    zone_a2.origin     = 10
    zone_a2.copynumber = 1

    zone_a_other = dlisio.plumbing.Zone()
    zone_a_other.name       = 'ZONE-A'
    zone_a_other.origin     = 34
    zone_a_other.copynumber = 0

    param.zones = [zone_a, zone_a2, zone_a_other]
    assert param.values['ZONE-A.10.0'] == 1
    assert param.values['ZONE-A.10.1'] == 2
    assert param.values['ZONE-A.34.0'] == 3

def test_parameter_wrong_zones_values():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'

    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2, 3, 4, 5],
                   'DIMENSION' : [2], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.zones = [zone_a, zone_b]

    assert list(param.values['RAW']) == [1, 2, 3, 4, 5]

def test_parameter_wrong_zones_one_value():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'

    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [2], 'DIMENSION' : [1], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.zones = [zone_a, zone_b]

    assert param.values['DLISIO-UNDEF-0'] == 2

def test_parameter_dimension1_value1():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [14],
                   'DIMENSION' : [1], 'AXIS' : [], 'ZONES' : []}

    param.load()
    assert param.values['DLISIO-UNZONED'] == 14

def test_parameter_dimension_values():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2],
                   'DIMENSION' : [2], 'AXIS' : [], 'ZONES' : []}

    param.load()
    assert np.array_equal(param.values['DLISIO-UNZONED'], [1, 2])

def test_parameter_wrong_dimension_values():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [3],
                   'DIMENSION' : [2], 'AXIS' : [], 'ZONES' : []}

    param.load()
    assert list(param.values['RAW']) == [3]

def test_parameter_wrong_dimension_wrong_zones_values():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'

    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2, 3],
                   'DIMENSION' : [1], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.zones = [zone_a, zone_b]

    assert param.values['DLISIO-UNDEF-0'] == 1
    assert param.values['DLISIO-UNDEF-1'] == 2
    assert param.values['DLISIO-UNDEF-2'] == 3

def test_parameter_dimension_zones_values():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'

    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                   'DIMENSION' : [2, 3], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.zones = [zone_a, zone_b]

    assert list(param.values['ZONE-A'][1]) == [3, 4]
    assert list(param.values['ZONE-B'][2]) == [11, 12]
    assert param.dimension                 == [3, 2]

def test_computation_dimension_zones_values():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'
    zone_c = dlisio.plumbing.Zone()
    zone_c.name = 'ZONE-C'

    comput = dlisio.plumbing.Computation()
    comput.attic = {'VALUES' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    'DIMENSION' : [4, 1], 'AXIS' : [], 'ZONES' : []}

    comput.load()
    comput.zones = [zone_a, zone_b, zone_c]
    print(comput.values)
    assert list(comput.values['ZONE-A'][0]) == [1, 2, 3, 4]
    assert list(comput.values['ZONE-B'][0]) == [5, 6, 7, 8]
    assert list(comput.values['ZONE-C'][0]) == [9, 10, 11, 12]
    assert comput.dimension              == [1, 4]

def test_computation_unlinked_zones_values():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_c = dlisio.plumbing.Zone()
    zone_c.name = 'ZONE-C'

    comput = dlisio.plumbing.Computation()
    comput.attic = {'VALUES' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    'DIMENSION' : [4], 'AXIS' : [], 'ZONES' : []}

    comput.load()
    comput.zones = [zone_a, None, zone_c]

    assert list(comput.values['ZONE-A']) == [1, 2, 3, 4]
    assert list(comput.values['DLISIO-UNDEF-1']) == [5, 6, 7, 8]
    assert list(comput.values['ZONE-C']) == [9, 10, 11, 12]

@pytest.mark.parametrize('value', [
    (7),
    (1.3),
    (False),
    ('val1'),
    (complex(22.6, 2.1)),
    (datetime(2003, 12, 3, 14, 15, 57))
])
def test_parameter_computation_repcode(value):
    param = dlisio.plumbing.Parameter()
    param.attic = {'DIMENSION' : [1], 'AXIS' : [], 'ZONES' : []}

    param.attic['VALUES'] = [value]
    param.load()
    assert param.values['DLISIO-UNZONED'] == value

    comput = dlisio.plumbing.Computation()
    comput.attic = {'DIMENSION' : [1], 'AXIS' : [], 'ZONES' : []}
    comput.attic['VALUES'] = [value]
    comput.load()
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    comput.zones = [zone_a]
    assert comput.values[zone_a.name] == value

def test_measurement_empty():
    m = dlisio.plumbing.Measurement()
    m.attic = {'MEASUREMENT' : [], 'REFERENCE' : [],
               'DIMENSION' : [], 'AXIS' : []}

    m.load()
    assert m.samples.size       == 0
    assert m.reference.size     == 0
    assert m.std_deviation.size == 0
    assert m.dimension          == []
    assert m.axis               == []

def test_measurement_dimension():
    m = dlisio.plumbing.Measurement()
    m.attic = {'MEASUREMENT' : [], 'DIMENSION' : [3, 5], 'AXIS' : []}

    m.load()
    assert m.samples.size   == 0
    assert m.reference.size == 0
    assert m.dimension      == [5, 3]
    assert m.axis           == []

def test_measurement_wrong_dimension_samples():
    m = dlisio.plumbing.Measurement()
    m.attic = {'MEASUREMENT' : [1, 2, 3], 'DIMENSION' : [3, 5], 'AXIS' : []}

    m.load()
    assert list(m.samples) == [1, 2, 3]
    assert m.dimension     == [5, 3]

def test_measurement_many_samples():
    m = dlisio.plumbing.Measurement()
    m.attic = {'MEASUREMENT'       : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
               'MAXIMUM-DEVIATION' : [2, 3, 2, 1],
               'REFERENCE'         : [3, 6, 9, 12],
               'PLUS-TOLERANCE'    : [0.4, 0.2, 0.1, 0.3],
               'MINUS-TOLERANCE'   : [0.5, 0.1, 0, 1],
               'DIMENSION'         : [4],
               'AXIS'              : []}

    m.load()

    assert list(m.samples[0])        == [1, 2, 3, 4]
    assert list(m.samples[1])        == [5, 6, 7, 8]
    assert list(m.samples[2])        == [9, 10, 11, 12]

    assert list(m.max_deviation[0])   == [2, 3, 2, 1]
    assert list(m.reference[0])       == [3, 6, 9, 12]
    assert list(m.plus_tolerance[0])  == [0.4, 0.2, 0.1, 0.3]
    assert list(m.minus_tolerance[0]) == [0.5, 0.1, 0, 1]

def test_measurement_non_corresponding_values():
    m = dlisio.plumbing.Measurement()
    m.attic = {
        'MEASUREMENT'       : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        'MAXIMUM-DEVIATION' : [2, 3, 2],
        'REFERENCE'         : [3, 6],
        'PLUS-TOLERANCE'    : [0.4, 0.2, 0.1, 0.3, 0.5],
        'MINUS-TOLERANCE'   : [0.5, 0.1, 0],
        'DIMENSION'         : [4]
    }

    m.load()

    assert list(m.samples)  == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    assert list(m.max_deviation)     == [2, 3, 2]
    assert list(m.reference)       == [3, 6]
    assert list(m.plus_tolerance)  == [0.4, 0.2, 0.1, 0.3, 0.5]
    assert list(m.minus_tolerance) == [0.5, 0.1, 0]

@pytest.mark.parametrize('reference, samples', [
    ([1, 2], [3, 4, 5, 6]),
    ([1.1, 2.2], [3.3, 4.4, 5.5, 6.6]),
    ([True, False], [True, False, True, False]),
    (['val1', 'val2'], ['val3', 'val4', 'val5', 'val6']),
    ([complex(1, 1), complex(2, 2)],
     [complex(3, 3), complex(4, 4), complex(5, 5), complex(6, 6)]),
    ([datetime(1991, 1, 1), datetime(1992, 2, 2)],
     [datetime(1993, 3, 3), datetime(1994, 4, 4),
      datetime(1995, 5, 5), datetime(1996, 6, 6)])
])
def test_measurement_repcode(reference, samples):
    m = dlisio.plumbing.Measurement()
    m.attic = {'DIMENSION' : [2], 'AXIS' : []}

    m.attic['MEASUREMENT'] = samples
    m.attic['REFERENCE'] = reference
    m.load()

    assert np.array_equal(np.array(reference), m.reference[0])
    sampled = [samples[0:2], samples[2:4]]
    assert np.array_equal(np.array(sampled), m.samples)
