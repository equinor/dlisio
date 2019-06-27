from .dataobject import *
from .valuetypes import scalar, vector
from .linkage import objref, obname

import numpy as np

class Measurement(DataObject):
    """Measurement

    Records of measurements, references, and tolerances used to compute
    calibration coefficients.

    See also
    --------

    DataObject : The data object that Measuremenet is derived from

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
          'DIMENSION'         : vector('dimension'),
          'AXIS'              : vector('axis'),
          'MEASUREMENT'       : vector('samples'),
          'SAMPLE-COUNT'      : scalar('samplecount'),
          'MAXIMUM-DEVIATION' : vector('max_deviation'),
          'STANDARD-DEVIATION': vector('std_deviation'),
          'BEGIN-TIME'        : scalar('begin_time'),
          'DURATION'          : scalar('duration'),
          'REFERENCE'         : vector('reference'),
          'STANDARD'          : vector('standard'),
          'PLUS-TOLERANCE'    : vector('plus_tolerance'),
          'MINUS-TOLERANCE'   : vector('minus_tolerance')
    }

    linkage = {
        'axis'   : obname("AXIS"),
        'source' : objref
    }

    datamap = {
        'samples'         : sampled,
        'max_deviation'   : simple,
        'std_deviation'   : simple,
        'reference'       : simple,
        'plus_tolerance'  : simple,
        'minus_tolerance' : simple,
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

        #: Measurement samples
        self.samples         = np.empty(0)

        #: Number of samples used to compute the max/std_deviation
        self.samplecount     = None

        #: Maximum deviation in the sample array
        self.max_deviation   = np.empty(0)

        #: Standard deviation in the sample array
        self.std_deviation   = np.empty(0)

        #: Time of the sample acquisition
        self.begin_time      = None

        #: Time duration of the sample acquisition
        self.duration        = None

        #: Expected nominal value of a single sample
        self.reference       = np.empty(0)

        #: Measurable quantity of the calibration standard used to produce the
        #: sample
        self.standard        = []

        #: Maximum value that a sample can exceed the reference and still be
        #: "within tolerance"
        self.plus_tolerance  = np.empty(0)

        #: Maximum value that a sample can fall below the reference and still
        #: be "within tolerance"
        self.minus_tolerance = np.empty(0)
