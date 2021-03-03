"""
Testing the way we present data contained in Parameter (values),
Computation (values) and Measurement (samples, max_deviation,
std_deviation, reference, plus_tolerance, minus_tolerance) objects.
Presentation of this data depends on data dimensions and zones, and
the datatype must be inferred from values passed from lower levels of
processing.
"""

import pytest
from datetime import datetime
import os

from dlisio import dlis
from dlisio.dlis.utils import *

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

def assemble_set(settype):
    """
    This setup is the same for all Computation and Parameter test files and can
    be viewed as tests prerequisite.
    Copying it in every test gives more noise than clarity, hence extracted.
    """

    sets = {
        'PARAMETER' :   'data/chap4-7/eflr/ndattrs/set/parameter.dlis.part',
        'COMPUTATION' : 'data/chap4-7/eflr/ndattrs/set/computation.dlis.part',
    }

    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        sets[settype],
        'data/chap4-7/eflr/ndattrs/template/values.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/dimension.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/zones.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
    ]
    return content

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_empty(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-empty.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-OBNAME.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        assert np.array_equal(obj.values, np.empty(0))
        assert obj.dimension == []
        assert obj.axis      == []
        assert obj.zones     == []

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_empty_dimension_provided(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-empty-dimension-provided.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-OBNAME.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        assert np.array_equal(obj.values, np.empty(0))
        assert obj.dimension == [1]
        assert obj.axis      == []
        assert obj.zones     == []

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_simple(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-simple.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-OBNAME.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        assert obj.values[0] == 2

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_infer_simple(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-infer-simple.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-OBNAME.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        assert obj.values[0] == 2

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_one_sample(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-one-sample.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/1-2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-OBNAME.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        assert list(obj.values[0]) == [1, 2]

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_wrong_dimensions(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-wrong-dimensions.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4-5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-OBNAME.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        msg = 'cannot reshape array of size 5 into shape [2]'
        with pytest.raises(ValueError) as error:
            _ = obj.values
        assert str(error.value) == msg
        assert np.array_equal(obj.attic['VALUES'].value,
                              np.array([1, 2, 3, 4, 5]))

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_wrong_dimensions_wrong_zones(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-wrong-dimensions-wrong-zones.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4-5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/zones-4.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        msg = 'cannot reshape array of size 5 into shape [2]'
        with pytest.raises(ValueError) as error:
            _ = obj.values
        assert str(error.value) == msg
        assert np.array_equal(obj.attic['VALUES'].value,
                              np.array([1, 2, 3, 4, 5]))

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_infer_dimensions_from_zones(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-infer-dimensions-from-zones.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4-5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/zones-5.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        # Should be able to infer correct dimension from zones
        assert np.array_equal(obj.values, np.array([1, 2, 3, 4, 5]))

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_no_dimensions_wrong_zones(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-no-dimensions-wrong-zones.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/1.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/zones-4.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        # Should use dimension over zones
        assert np.array_equal(obj.values, np.array([1]))

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_right_dimensions_wrong_zones(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-right-dimensions-wrong-zones.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/zones-5.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        # Should use dimension over zones
        assert np.array_equal(obj.values, np.array([[1, 2], [3, 4]]))

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_right_dimensions_right_zones(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-right-dimensions-right-zones.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/zones-2.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)

        assert np.array_equal(obj.values, np.array([[1, 2], [3, 4]]))

@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_values_multidim_values(tmpdir, merge_files_oneLR, settype):
    path = os.path.join(str(tmpdir), 'values-multidim-values.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4-5-6-7-8-9-10-11-12.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2-3.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-OBNAME.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)

        assert list(obj.values[0][1]) == [3, 4]
        assert list(obj.values[1][2]) == [11, 12]
        assert obj.dimension == [3, 2]

@pytest.mark.parametrize('value, valuefilename', [
    ([1, 2], '1-2.dlis.part'),
    ([0.5, 1.5], '0.5-1.5.dlis.part'),
    ([False, True], 'False-True.dlis.part'),
    (['val1', 'val2'], 'string-val1,val2.dlis.part'),
    ([(0.5, 1.5), (2.5, 3.5)], 'validated-(0.5-1.5),(2.5-3.5).dlis.part'),
    ([complex(0.5, 1.5), complex(2.5, 3.5)],
         'complex-(0.5-1.5),(2.5-3.5).dlis.part'),
    ([datetime(2001, 1, 1), datetime(2002, 2, 2)],
         '2001-Jan-1,2002-Feb-2.dlis.part')
])
@pytest.mark.parametrize('settype', ["PARAMETER", "COMPUTATION"])
def test_parameter_computation_repcode(tmpdir, merge_files_oneLR, settype,
                                       value, valuefilename):
    path = os.path.join(str(tmpdir), 'pc-repcode.dlis')
    content = [
        *assemble_set(settype),
        'data/chap4-7/eflr/ndattrs/objattr/' + valuefilename,
        'data/chap4-7/eflr/ndattrs/objattr/2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-OBNAME.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        obj  = f.object(settype, 'OBJECT', 10, 0)
        assert np.array_equal(obj.values[0], value)

def test_measurement_empty(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'measurement-empty.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/ndattrs/set/calibration-measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/reference.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/dimension.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        m  = f.object('CALIBRATION-MEASUREMENT', 'OBJECT', 10, 0)

        assert m.samples.size       == 0
        assert m.reference.size     == 0
        assert m.std_deviation.size == 0
        assert m.dimension          == []
        assert m.axis               == []

def test_measurement_dimension(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'measurement-dimension.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/ndattrs/set/calibration-measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/dimension.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/empty-INT.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2-3.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        m  = f.object('CALIBRATION-MEASUREMENT', 'OBJECT', 10, 0)

        assert m.samples.size   == 0
        assert m.reference.size == 0
        assert m.dimension      == [3, 2]
        assert m.axis           == []

def test_measurement_wrong_dimension(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'measurement-wrong-dimension.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/ndattrs/set/calibration-measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/dimension.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2-3.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        m  = f.object('CALIBRATION-MEASUREMENT', 'OBJECT', 10, 0)

        msg = 'cannot reshape array of size 3 into shape [3, 2]'
        with pytest.raises(ValueError) as error:
            _ = m.samples

        assert str(error.value) == msg
        assert m.attic['MEASUREMENT'].value == [1, 2, 3]
        assert m.dimension == [3, 2]

def test_measurement_many_samples(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'measurement-many-samples.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/ndattrs/set/calibration-measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/maximum-deviation.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/standard-deviation.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/reference.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/plus-tolerance.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/minus-tolerance.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/dimension.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4-5-6-7-8-9-10-11-12.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/0.5-1.5-2.5-3.5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/0.5-1.5-2.5-3.5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/0.5-1.5-2.5-3.5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/4.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        m  = f.object('CALIBRATION-MEASUREMENT', 'OBJECT', 10, 0)

        assert np.array_equal(m.samples[0], np.array([1, 2, 3, 4]))
        assert np.array_equal(m.samples[1], np.array([5, 6, 7, 8]))
        assert np.array_equal(m.samples[2], np.array([9, 10, 11, 12]))

        assert np.array_equal(m.max_deviation,   np.array([1, 2, 3, 4]))
        assert np.array_equal(m.std_deviation,   np.array([0.5, 1.5, 2.5, 3.5]))
        assert np.array_equal(m.reference,       np.array([1, 2, 3, 4]))
        assert np.array_equal(m.plus_tolerance,  np.array([0.5, 1.5, 2.5, 3.5]))
        assert np.array_equal(m.minus_tolerance, np.array([0.5, 1.5, 2.5, 3.5]))

def test_measurement_non_corresponding_values(tmpdir, merge_files_oneLR):
    path = os.path.join(str(tmpdir), 'measurement-non-corresponding-values.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/ndattrs/set/calibration-measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/maximum-deviation.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/standard-deviation.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/reference.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/plus-tolerance.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/minus-tolerance.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/dimension.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4-5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2-3.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/0.5-1.5-2.5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/4.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        m  = f.object('CALIBRATION-MEASUREMENT', 'OBJECT', 10, 0)

        msg = 'cannot reshape array of size {} into shape 4'
        with pytest.raises(ValueError) as error:
            _ = m.samples
            assert error.value == msg.format(5)

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
            assert error.value == msg.format(1)

        with pytest.raises(ValueError) as error:
            _ = m.minus_tolerance
            assert error.value == msg.format(3)

def test_measurement_more_than_one_sample(tmpdir, merge_files_oneLR, assert_log):
    path = os.path.join(str(tmpdir), 'measurement-more-than-one-sample.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/ndattrs/set/calibration-measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/maximum-deviation.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/standard-deviation.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/reference.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/plus-tolerance.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/minus-tolerance.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/dimension.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4-5-6-7-8-9-10-11-12.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/0.5-1.5-2.5-3.5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/0.5-1.5-2.5-3.5.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/1-2-3-4-5-6-7-8-9-10-11-12.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/2.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        m  = f.object('CALIBRATION-MEASUREMENT', 'OBJECT', 10, 0)

        assert np.array_equal(m.samples[2], np.array([5, 6]))

        msg = 'found {} samples, should be 1'
        _ = m.max_deviation
        assert_log(msg.format(2))

        _ = m.std_deviation
        assert_log(msg.format(2))

        _ = m.reference
        assert_log(msg.format(2))

        _ = m.plus_tolerance
        assert_log(msg.format(2))

        _ = m.minus_tolerance
        assert_log(msg.format(6))

@pytest.mark.parametrize('reference, samples, reffilename, samplesfilename', [
    (1, [1, 2],
         "1.dlis.part", "1-2.dlis.part"),
    (0.5, [0.5, 1.5],
         "0.5.dlis.part", "0.5-1.5.dlis.part"),
    (False, [False, True],
         "False.dlis.part", "False-True.dlis.part"),
    ('val1', ['val1', 'val2'],
         "string-val1.dlis.part", "string-val1,val2.dlis.part"),
    ((0.5, 1.5), [(0.5, 1.5), (2.5, 3.5)],
         "validated-(0.5-1.5).dlis.part",
         "validated-(0.5-1.5),(2.5-3.5).dlis.part"),
    (complex(0.5, 1.5), [complex(0.5, 1.5), complex(2.5, 3.5)],
         "complex-(0.5-1.5).dlis.part", "complex-(0.5-1.5),(2.5-3.5).dlis.part"),
    (datetime(2001, 1, 1), [datetime(2001, 1, 1), datetime(2002, 2, 2)],
         "2001-Jan-1.dlis.part", "2001-Jan-1,2002-Feb-2.dlis.part")
])
def test_measurement_repcode(tmpdir, merge_files_oneLR, reference, reffilename,
                             samples, samplesfilename):
    path = os.path.join(str(tmpdir), 'measurement-repcode.dlis')
    content = [
        'data/chap4-7/eflr/envelope.dlis.part',
        'data/chap4-7/eflr/ndattrs/set/calibration-measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/measurement.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/reference.dlis.part',
        'data/chap4-7/eflr/ndattrs/template/dimension.dlis.part',
        'data/chap4-7/eflr/ndattrs/object.dlis.part',
        'data/chap4-7/eflr/ndattrs/objattr/' + samplesfilename,
        'data/chap4-7/eflr/ndattrs/objattr/' + reffilename,
        'data/chap4-7/eflr/ndattrs/objattr/1.dlis.part',
    ]
    merge_files_oneLR(path, content)

    with dlis.load(path) as (f, *_):
        m  = f.object('CALIBRATION-MEASUREMENT', 'OBJECT', 10, 0)

        assert np.array_equal(reference, m.reference)
        sampled = [samples[0], samples[1]]
        assert np.array_equal(np.array(sampled), m.samples)
