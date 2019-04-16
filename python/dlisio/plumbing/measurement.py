from .basicobject import BasicObject


class Measurement(BasicObject):
    """Measurement

    Records of measurements, references, and tolerances used to compute
    calibration coefficients.

    Notes
    -----

    The Measurement object reflects the logical record type
    CALIBRATION-MEASUREMENT, defined in rp66. CHANNEL records are listed in
    Appendix A.2 - Logical Record Types and described in detail in Chapter
    5.8.7.1 - Static and Frame Data, CALIBRATION-MEASUREMENT objects.
    """
    attributes = {
          'PHASE'             : ('phase'          , True),
          'MEASUREMENT-SOURCE': ('source_ref'     , True),
          'TYPE'              : ('mtype'          , True),
          'DIMENSION'         : ('dimension'      , False),
          'AXIS'              : ('axis'           , False),
          'MEASUREMENT'       : ('samples'        , False),
          'SAMPLE-COUNT'      : ('samplecount'    , True),
          'MAXIMUM-DEVIATION' : ('max_deviation'  , True),
          'STANDARD-DEVIATION': ('std_deviation'  , True),
          'BEGIN-TIME'        : ('begin_time'     , True),
          'DURATION'          : ('duration'       , True),
          'REFERENCE'         : ('reference'      , False),
          'STANDARD'          : ('standard'       , False),
          'PLUS-TOLERANCE'    : ('plus_tolerance' , False),
          'MINUS-TOLERANCE'   : ('minus_tolerance', False)
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
        self.samples         = []

        #: Number of samples used to compute the max/std_deviation
        self.samplecount     = None

        #: Maximum deviation in the sample array
        self.max_deviation   = None

        #: Standard deviation in the sample array
        self.std_deviation   = None

        #: Time of the sample acquisition
        self.begin_time      = None

        #: Time duration of the sample acquisition
        self.duration        = None

        #: Expected nominal value of a single sample
        self.reference       = []

        #: Measurable quantity of the calibration standard used to produce the
        #: sample
        self.standard        = []

        #: Maximum value that a sample can exceed the reference and still be
        #: "within tolerance"
        self.plus_tolerance  = []

        #: Maximum value that a sample can fall below the reference and still
        #: be "within tolerance"
        self.minus_tolerance = []

        #: Reference to the source
        self.source_ref      = None

    def link(self, objects, sets):
        if self.source_ref is None:
            return

        ref = self.source_ref.fingerprint
        try:
            self.source = objects[ref]
        except KeyError:
            problem = 'measurement source referenced, but not found. '
            ids = 'measurement = {}, source = {}'.format(self.fingerprint, ref)

            info = 'not populating source attribute for {}'
            info = info.format(self.fingerprint)

            logging.warning(problem + ids)
            logging.info(info)
