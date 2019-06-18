import numpy as np
import dlisio
import pytest
from datetime import datetime

def test_parameter_empty():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [], 'DIMENSION' : [], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.reshape(True)
    assert param.values.size == 0
    assert param.dimension   == []
    assert param.axis        == []
    assert param.zones       == []

def test_parameter_dimension():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [], 'DIMENSION' : [1], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.reshape(True)
    assert param.values.size == 0
    assert param.dimension   == [1]
    assert param.axis        == [None]
    assert param.zones       == []

def test_parameter_values():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2],
                   'DIMENSION' : [], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.reshape(True)
    assert list(param.values["unzoned"]) == [1, 2]
    assert param.dimension               == [2]
    assert param.axis                    == [None]
    assert param.zones                   == []

def test_parameter_zones_values():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'

    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2, 3, 4],
                   'DIMENSION' : [], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.zones = [zone_a, zone_b]
    param.reshape(True)

    assert list(param.values["ZONE-A"]) == [1, 2]
    assert list(param.values["ZONE-B"]) == [3, 4]
    assert param.dimension              == [2]
    assert param.axis                   == [None]
    assert param.zones                  == [zone_a, zone_b]

def test_parameter_copied_zones_values():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2, 3],
                   'DIMENSION' : [], 'AXIS' : [], 'ZONES' : []}

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
    param.reshape(True)

    assert list(param.values["ZONE-A.10.0"]) == [1]
    assert list(param.values["ZONE-A.10.1"]) == [2]
    assert list(param.values["ZONE-A.34.0"]) == [3]

def test_parameter_wrong_zones_values():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'

    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2, 3, 4, 5],
                   'DIMENSION' : [], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.zones = [zone_a, zone_b]
    param.reshape(True)

    assert np.array_equal(param.values, np.empty(0))
    assert param.dimension == []
    assert param.axis      == []
    assert param.zones     == [zone_a, zone_b]

def test_parameter_wrong_zones_one_value():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'

    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [2], 'DIMENSION' : [], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.zones = [zone_a, zone_b]
    param.reshape(True)

    assert np.array_equal(param.values, np.empty(0))
    assert param.dimension == []
    assert param.axis      == []
    assert param.zones     == [zone_a, zone_b]

def test_parameter_dimension1_value1():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [14],
                   'DIMENSION' : [1], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.reshape(True)
    assert np.array_equal(param.values["unzoned"], [14])
    assert param.dimension == [1]
    assert param.axis      == [None]
    assert param.zones     == []

def test_parameter_dimension_values():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2],
                   'DIMENSION' : [2], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.reshape(True)
    assert np.array_equal(param.values["unzoned"], [1, 2])
    assert param.dimension == [2]
    assert param.axis      == [None]
    assert param.zones     == []

def test_parameter_wrong_dimension_values():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [3],
                   'DIMENSION' : [2], 'AXIS' : [], 'ZONES' : []}

    param.load()
    param.reshape(True)
    assert np.array_equal(param.values, np.empty(0))
    assert param.dimension == [2]
    assert param.axis      == [None]
    assert param.zones     == []

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
    param.reshape(True)

    assert np.array_equal(param.values, np.empty(0))
    assert param.dimension == [1]
    assert param.axis      == [None]

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
    param.reshape(True)

    assert list(param.values["ZONE-A"][1]) == [3, 4]
    assert list(param.values["ZONE-B"][2]) == [11, 12]
    assert param.dimension                 == [3, 2]
    assert param.axis                      == [None, None]
    assert param.zones                     == [zone_a, zone_b]

def test_parameter_combine():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    zone_b = dlisio.plumbing.Zone()
    zone_b.name = 'ZONE-B'

    param1= dlisio.plumbing.Parameter()
    param1.attic = {'VALUES' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    'DIMENSION' : [2, 3], 'AXIS' : [], 'ZONES' : []}
    param1.load()
    param1.zones = [zone_a, zone_b]
    param1.reshape(True)

    param2= dlisio.plumbing.Parameter()
    param2.attic = {'VALUES' : [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                    'DIMENSION' : [2, 3], 'AXIS' : [], 'ZONES' : []}
    param2.load()
    param2.zones = [zone_a, zone_b]
    param2.reshape(True)

    params = np.array([param1.values, param2.values])
    assert np.array_equal(params["ZONE-A"][0],
                          np.array([[1, 2], [3, 4], [5, 6]]))
    assert np.array_equal(params["ZONE-B"][1],
                          np.array([[6, 5], [4, 3], [2, 1]]))

def test_parameter_no_load_double_reshape():
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'

    param = dlisio.plumbing.Parameter()
    param.dimension            = [2, 3]
    param.datapoints["values"] = [1, 2, 3, 4, 5, 6]
    param.zones                = [zone_a]

    arr = np.array([[1, 2, 3], [4, 5, 6]])

    param.reshape(False)
    assert param.dimension == [2, 3]
    assert param.axis      == [None, None]
    assert np.array_equal(param.values['ZONE-A'], arr)

    param.reshape(False)
    assert param.dimension == [2, 3]
    assert param.axis      == [None, None]
    assert np.array_equal(param.values['ZONE-A'], arr)

def test_parameter_reshape():
    param = dlisio.plumbing.Parameter()
    param.attic = {'VALUES' : [1, 2, 3, 4, 5, 6],
                   'DIMENSION' : [3, 2], 'AXIS' : [], 'ZONES' : []}

    arr = np.array([[1, 2, 3], [4, 5, 6]])

    param.load()
    param.reshape(True)
    assert param.dimension == [2, 3]
    assert param.axis      == [None, None]
    assert np.array_equal(param.values['unzoned'], arr)

    param.dimension = [1, 6]

    arr = np.array([[1, 2, 3, 4, 5, 6]])

    param.reshape(False)
    assert param.dimension == [1, 6]
    assert np.array_equal(param.values['unzoned'], arr)

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

    comput.reshape(True)
    assert list(comput.values["ZONE-A"][0]) == [1, 2, 3, 4]
    assert list(comput.values["ZONE-B"][0]) == [5, 6, 7, 8]
    assert list(comput.values["ZONE-C"][0]) == [9, 10, 11, 12]
    assert comput.dimension                 == [1, 4]
    assert comput.axis                      == [None, None]
    assert comput.zones                     == [zone_a, zone_b, zone_c]

@pytest.mark.parametrize("value", [
    (7),
    (1.3),
    (False),
    ("val1"),
    ((3.2, 6.2)),
    ((1.6, 6.7, -9.0)),
    (complex(22.6, 2.1)),
    (datetime(2003, 12, 3, 14, 15, 57))
])
def test_parameter_computation_repcode(value):
    param = dlisio.plumbing.Parameter()
    param.attic = {'DIMENSION' : [], 'AXIS' : [], 'ZONES' : []}

    param.attic['VALUES'] = [value]
    param.load()
    param.reshape(True)
    assert np.array_equal(np.array([value]), param.values["unzoned"])

    comput = dlisio.plumbing.Computation()
    comput.attic = {'DIMENSION' : [], 'AXIS' : [], 'ZONES' : []}
    comput.attic['VALUES'] = [value]
    comput.load()
    zone_a = dlisio.plumbing.Zone()
    zone_a.name = 'ZONE-A'
    comput.zones = [zone_a]
    comput.reshape(True)
    assert np.array_equal(np.array([value]), comput.values["ZONE-A"])

def test_measurement_empty():
    m = dlisio.plumbing.Measurement()
    m.attic = {'MEASUREMENT' : [], 'REFERENCE' : [],
               'DIMENSION' : [], 'AXIS' : []}

    m.load()
    m.reshape(True)
    assert m.samples.size       == 0
    assert m.reference.size     == 0
    assert m.std_deviation.size == 0
    assert m.dimension          == []
    assert m.axis               == []

def test_measurement_dimension():
    m = dlisio.plumbing.Measurement()
    m.attic = {'MEASUREMENT' : [], 'DIMENSION' : [3, 5], 'AXIS' : []}

    m.load()
    m.reshape(True)
    assert m.samples.size   == 0
    assert m.reference.size == 0
    assert m.dimension      == [5, 3]
    assert m.axis           == [None, None]

def test_measurement_wrong_dimension_samples():
    m = dlisio.plumbing.Measurement()
    m.attic = {'MEASUREMENT' : [1, 2, 3], 'DIMENSION' : [3, 5], 'AXIS' : []}

    m.load()
    m.reshape(True)
    assert m.samples.size   == 0
    assert m.reference.size == 0
    assert m.dimension      == [5, 3]
    assert m.axis           == [None, None]

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
    m.reshape(True)

    assert list(m.samples[0])      == [1, 2, 3, 4]
    assert list(m.samples[1])      == [5, 6, 7, 8]
    assert list(m.samples[2])      == [9, 10, 11, 12]
    assert list(m.max_deviation)   == [2, 3, 2, 1]
    assert list(m.reference)       == [3, 6, 9, 12]
    assert list(m.plus_tolerance)  == [0.4, 0.2, 0.1, 0.3]
    assert list(m.minus_tolerance) == [0.5, 0.1, 0, 1]
    assert m.dimension             == [4]
    assert m.axis                  == [None]

def test_measurement_non_corresponding_values():
    m = dlisio.plumbing.Measurement()
    m.attic = {'MEASUREMENT'       : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
               'MAXIMUM-DEVIATION' : [2, 3, 2, 1],
               'REFERENCE'         : [3, 6],
               'PLUS-TOLERANCE'    : [0.4, 0.2, 0.1, 0.3],
               'MINUS-TOLERANCE'   : [0.5, 0.1, 0, 1],
               'DIMENSION'         : [],
               'AXIS'              : []}

    m.load()
    m.reshape(True)

    assert list(m.samples)   == []
    assert list(m.reference) == []
    assert m.dimension       == []
    assert m.axis            == []

def test_measurement_reshape():
    m = dlisio.plumbing.Measurement()
    m.attic = {'MEASUREMENT' : [1, 2, 3, 4],
               'DIMENSION' : [], 'AXIS' : []}

    m.load()
    m.reshape(True)

    assert m.dimension        == [1]
    assert m.axis             == [None]
    assert list(m.samples[0]) == [1]
    assert list(m.samples[1]) == [2]
    assert list(m.samples[2]) == [3]
    assert list(m.samples[3]) == [4]

    m.attic['REFERENCE'] = [5]

    m.load()
    m.reshape(True)
    assert m.dimension == [1]
    assert m.axis      == [None]
    assert m.reference == [5]

    m.attic['REFERENCE'] = [5, 6, 7, 8]

    m.load()
    m.reshape(True)
    assert m.dimension == [4]
    assert np.array_equal(m.samples[0], [1, 2, 3, 4])
    assert np.array_equal(m.reference, [5, 6, 7, 8])

    m.attic['DIMENSION'] = [2, 2]
    m.load()
    m.reshape(True)
    assert list(m.samples[0][0]) == [1, 2]
    assert list(m.samples[0][1]) == [3, 4]

    m.dimension = [1, 4]
    m.reshape(False)
    assert list(m.samples[0][0]) == [1, 2, 3, 4]

    del m.attic['REFERENCE']
    del m.datapoints['reference']
    del m.reference

    m.load()
    m.dimension = [2] #owerwriting existing
    m.reshape(False)
    assert list(m.samples[0]) == [1, 2]
    assert list(m.samples[1]) == [3, 4]

@pytest.mark.parametrize("reference, samples", [
    ([1, 2], [3, 4, 5, 6]),
    ([1.1, 2.2], [3.3, 4.4, 5.5, 6.6]),
    ([True, False], [True, False, True, False]),
    (["val1", "val2"], ["val3", "val4", "val5", "val6"]),
    ([(1, 1), (2, 2)], [(3, 3), (4, 4), (5, 5), (6, 6)]),
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
    m.reshape(True)
    assert np.array_equal(np.array(reference), m.reference)
    sampled = [samples[0:2], samples[2:4]]
    assert np.array_equal(np.array(sampled), m.samples)
