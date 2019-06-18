from .basicobject import BasicObject
from .valuetypes import scalar, vector, reverse
from .linkage import objref, obname
from .utils import sampling

import numpy as np


class Measurement(BasicObject):
    """
    Records of measurements, references, and tolerances used to compute
    calibration coefficients.

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
          'SAMPLE-COUNT'      : scalar('samplecount'),
          'BEGIN-TIME'        : scalar('begin_time'),
          'DURATION'          : scalar('duration'),
          'STANDARD'          : vector('standard'),
    }

    linkage = {
        'axis'   : obname("AXIS"),
        'source' : objref
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = "CALIBRATION-MEASUREMENT")
        #: In what phase of the overall job sequence the
        #: measurement as aquired
        self.phase           = None

        #: Source the measurement
        self.source          = None

        #: Type of measurement
        self.mtype           = None

        #: Structure of the sample array
        self.dimension       = []

        #: Coordinate axis of the sample array
        self.axis            = []

        #: Number of samples used to compute the max/std_deviation
        self.samplecount     = None

        #: Time of the sample acquisition
        self.begin_time      = None

        #: Time duration of the sample acquisition
        self.duration        = None

        #: Measurable quantity of the calibration standard used to produce the
        #: sample
        self.standard        = []

    @property
    def samples(self):
        """ Measurment samples

        The type of measurment is described by the type attribute. Each sample
        may be either a scalar or ndarray
        """
        try:
            data = self.attic['MEASUREMENT']
        except KeyError:
            return np.empty(0)

        try:
            return sampling(data, self.dimension)
        except ValueError:
            return np.array(data)

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
            data = self.attic['MAXIMUM-DEVIATION']
        except KeyError:
            return np.empty(0)

        try:
            return sampling(data, self.dimension)
        except ValueError:
            return np.array(data)

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
            data = self.attic['STANDARD-DEVIATION']
        except KeyError:
            return np.empty(0)

        try:
            return sampling(data, self.dimension)
        except ValueError:
            return np.array(data)

    @property
    def reference(self):
        """The nominal value of each sample in the samples attribute

        Each sample may be a scalar of ndarray, but should have the same
        structure as the samples in the sample attribute.
        """
        try:
            data = self.attic['REFERENCE']
        except KeyError:
            return np.empty(0)

        try:
            return sampling(data, self.dimension)
        except ValueError:
            return np.array(data)

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
            data = self.attic['PLUS-TOLERANCE']
        except KeyError:
            return np.empty(0)

        try:
            return sampling(data, self.dimension)
        except ValueError:
            return np.array(data)

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
            data = self.attic['MINUS-TOLERANCE']
        except KeyError:
            return np.empty(0)

        try:
            return sampling(data, self.dimension)
        except ValueError:
            return np.array(data)
