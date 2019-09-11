from .basicobject import BasicObject
from .valuetypes import scalar, vector, reverse, skip
from .linkage import objref, obname
from .utils import *

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

    samples
    max_deviation
    std_deviation
    reference
    plus_tolerance
    minus_tolerance

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
        'PHASE'             : scalar('phase'),
        'MEASUREMENT-SOURCE': scalar('source'),
        'TYPE'              : scalar('mtype'),
        'DIMENSION'         : reverse('dimension'),
        'AXIS'              : reverse('axis'),
        'MEASUREMENT'       : skip(),
        'SAMPLE-COUNT'      : scalar('samplecount'),
        'MAXIMUM-DEVIATION' : skip(),
        'STANDARD-DEVIATION': skip(),
        'BEGIN-TIME'        : scalar('begin_time'),
        'DURATION'          : scalar('duration'),
        'REFERENCE'         : skip(),
        'STANDARD'          : vector('standard'),
        'PLUS-TOLERANCE'    : skip(),
        'MINUS-TOLERANCE'   : skip(),
    }

    linkage = {
        'axis'   : obname("AXIS"),
        'source' : objref
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = "CALIBRATION-MEASUREMENT")
        self.phase           = None
        self.source          = None
        self.mtype           = None
        self.dimension       = []
        self.axis            = []
        self.samplecount     = None
        self.begin_time      = None
        self.duration        = None
        self.standard        = []

    @property
    def samples(self):
        """ Measurment samples

        The type of measurment is described by the type attribute. Each sample
        may be either a scalar or ndarray
        """
        try:
            samples = self.attic['MEASUREMENT']
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
            dev = self.attic['MAXIMUM-DEVIATION']
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
            dev = self.attic['STANDARD-DEVIATION']
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
            ref = self.attic['REFERENCE']
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
            tolerance = self.attic['PLUS-TOLERANCE']
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
            tolerance   = self.attic['MINUS-TOLERANCE']
        except KeyError:
            return np.empty(0)

        shape = validshape(tolerance, self.dimension)
        return sampling(tolerance, shape, single=True)

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Type of measurement']       = self.mtype
        d['Calibration standard']      = self.standard
        d['Phase in job sequence']     = self.phase
        d['Start time of acquisition'] = self.begin_time
        d['Duration time']             = self.duration
        d['Data source']               = self.source

        describe_header(buf, 'Metadata', width, indent, lvl=2)
        describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Dimensions']       = self.dimension
        d['Axis labels']      = self.axis
        try:
            samplecount = len(self.samples)
        except ValueError:
            samplecount = 0
        d['Number of values'] = samplecount
        samples = 'Samples used to compute std/max-dev'
        d[samples] = self.samplecount

        if exclude['empty']: d = remove_empties(d)
        if d: describe_header(buf, 'Samples', width, indent, lvl=2)
        describe_dict(buf, d, width, indent, exclude)

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
