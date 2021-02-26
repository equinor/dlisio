from .basicobject import BasicObject
from .valuetypes import scalar, vector, reverse
from .linkage import objref, obname
from .dimensional import validshape, sampling
from .describe import (
    describe_header,
    describe_attributes,
    describe_sampled_attrs,
    remove_empties,
)

from collections import OrderedDict
import logging
import numpy as np


class Measurement(BasicObject):
    """
    Records of measurements, references, and tolerances used to compute
    calibration coefficients.

    Attributes
    ----------

    phase : str
        In what phase of the overall job sequence the measurement as acquired

    source
        Source the measurement

    mtype : str
        Type of measurement

    dimension : list(int)
        Structure of the sample array

    axis : list(Axis)
        Coordinate axis of the sample array

    samplecount : int
        Number of samples used to compute the max/std_deviation

    begin_time
        Time of the sample acquisition. |crtime|

    duration
        Time duration of the sample acquisition

    standard
        Measurable quantity of the calibration standard used to produce the
        sample

    See also
    --------

    BasicObject : The basic object that Measurement derived from

    Notes
    -----

    The Measurement object reflects the logical record type
    CALIBRATION-MEASUREMENT, defined in rp66. CHANNEL records are listed in
    Appendix A.2 - Logical Record Types and described in detail in Chapter
    5.8.7.1 - Static and Frame Data, CALIBRATION-MEASUREMENT objects.
    """
    attributes = {
        'PHASE'             : scalar,
        'MEASUREMENT-SOURCE': scalar,
        'TYPE'              : scalar,
        'DIMENSION'         : reverse,
        'AXIS'              : reverse,
        'MEASUREMENT'       : vector,
        'SAMPLE-COUNT'      : scalar,
        'MAXIMUM-DEVIATION' : vector,
        'STANDARD-DEVIATION': vector,
        'BEGIN-TIME'        : scalar,
        'DURATION'          : scalar,
        'REFERENCE'         : vector,
        'STANDARD'          : vector,
        'PLUS-TOLERANCE'    : vector,
        'MINUS-TOLERANCE'   : vector,
    }

    linkage = {
        'AXIS'               : obname('AXIS'),
        'MEASUREMENT-SOURCE' : objref
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def phase(self):
        return self['PHASE']

    @property
    def source(self):
        return self['MEASUREMENT-SOURCE']

    @property
    def mtype(self):
        return self['TYPE']

    @property
    def dimension(self):
        return self['DIMENSION']

    @property
    def axis(self):
        return self['AXIS']

    @property
    def samplecount(self):
        return self['SAMPLE-COUNT']

    @property
    def begin_time(self):
        return self['BEGIN-TIME']

    @property
    def duration(self):
        return self['DURATION']

    @property
    def standard(self):
        return self['STANDARD']

    @property
    def samples(self):
        """ Measurment samples

        The type of measurment is described by the type attribute. Each sample
        may be either a scalar or ndarray
        """
        try:
            samples = self.attic['MEASUREMENT'].value
        except KeyError:
            return np.empty(0)

        shape = validshape(samples, self.dimension)
        return sampling(samples, shape)


    @property
    def max_deviation(self):
        """Maximum deviation

        Only applicable when the sample attribute contains mean values. In that
        case, this is maximum deviation from the mean of any value used to
        compute the mean.

        Each sample may be a scalar of ndarray, but should have the same
        structure as the samples in the sample attribute.
        """
        try:
            dev = self.attic['MAXIMUM-DEVIATION'].value
        except KeyError:
            return np.empty(0)

        shape = validshape(dev, self.dimension)
        return sampling(dev, shape, single=True)

    @property
    def std_deviation(self):
        """Standard deviation

        Only applicable when the sample attribute contains mean values. In that
        case, this is the standard deviation of the samples used to compute the
        mean.

        Each sample may be a scalar of ndarray, but should have the same
        structure as the samples in the sample attribute.
        """
        try:
            dev = self.attic['STANDARD-DEVIATION'].value
        except KeyError:
            return np.empty(0)

        shape = validshape(dev, self.dimension)
        return sampling(dev, shape, single=True)

    @property
    def reference(self):
        """The nominal value of each sample in the samples attribute

        Each sample may be a scalar of ndarray, but should have the same
        structure as the samples in the sample attribute.
        """
        try:
            ref = self.attic['REFERENCE'].value
        except KeyError:
            return np.empty(0)

        shape = validshape(ref, self.dimension)
        return sampling(ref, shape, single=True)

    @property
    def plus_tolerance(self):
        """The maximum value that any sample (in samples) can exceed the
        reference and still be 'within tolerance'. Should be all non-negative
        numbers. If this attribute is empty, the plus tolerance is implicity
        infinite.

        Each sample may be a scalar of ndarray, but should have the same
        structure as the samples in the sample attribute.
        """
        try:
            tolerance = self.attic['PLUS-TOLERANCE'].value
        except KeyError:
            return np.empty(0)

        shape = validshape(tolerance, self.dimension)
        return sampling(tolerance, shape, single=True)

    @property
    def minus_tolerance(self):
        """The maximum value that any sample (in samples) can fall below the
        reference and still be 'within tolerance'. Should be all non-negative
        numbers. If this attribute is empty, the minus tolerance is implicity
        infinite.

        Each sample may be a scalar of ndarray, but should have the same
        structure as the samples in the sample attribute.
        """
        try:
            tolerance   = self.attic['MINUS-TOLERANCE'].value
        except KeyError:
            return np.empty(0)

        shape = validshape(tolerance, self.dimension)
        return sampling(tolerance, shape, single=True)

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Type of measurement']       = 'TYPE'
        d['Calibration standard']      = 'STANDARD'
        d['Phase in job sequence']     = 'PHASE'
        # TODO: translate begin-times which are presented as numbers to dates
        d['Start time of acquisition'] = 'BEGIN-TIME'
        d['Duration time']             = 'DURATION'
        d['Data source']               = 'MEASUREMENT-SOURCE'

        describe_header(buf, 'Metadata', width, indent, lvl=2)
        describe_attributes(buf, d, self, width, indent, exclude)

        d = OrderedDict()
        d['Dimensions']  = 'DIMENSION'
        d['Axis labels'] = 'AXIS'
        try:
            samplecount = len(self.samples)
        except ValueError:
            samplecount = 0
        d['Number of values'] = samplecount
        samples = 'Samples used to compute std/max-dev'
        d[samples] = 'SAMPLE-COUNT'

        if exclude['empty']: d = remove_empties(d)
        if d: describe_header(buf, 'Samples', width, indent, lvl=2)
        describe_attributes(buf, d, self, width, indent, exclude)

        d = OrderedDict()
        d['Reference']       = 'REFERENCE'
        d['Minus Tolerance'] = 'MINUS-TOLERANCE'
        d['Plus Tolerance']  = 'PLUS-TOLERANCE'
        d['Std deviation']   = 'STANDARD-DEVIATION'
        d['Max deviation']   = 'MAXIMUM-DEVIATION'

        describe_sampled_attrs(
                buf,
                self.attic,
                self.dimension,
                'MEASUREMENT',
                d,
                width,
                indent,
                exclude
        )
