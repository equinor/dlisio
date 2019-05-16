from .basicobject import BasicObject
from .valuetypes import vector, scalar
from .linkage import obname

class Calibration(BasicObject):
    """Calibration

    Calibration objects are a collection of measurements and coefficients that
    defines the calibration process of channel objects.

    Notes
    -----

    The Calibration reflects the logical record type CALIBRATION, defined in
    rp66. CALIBRATION records are listen in Appendix A.2 - Logical Record
    Types and described detail in Chapter 5.8.7.3 - Static and Frame Data,
    CALIBRATION objects.

    See also
    --------

    dlisio.Channel : Channel objects.
    dlisio.Parameter : Parameter objects.
    """
    attributes = {
        'METHOD'               : scalar('method'),
        'CALIBRATED-CHANNELS'  : vector('calibrated'),
        'UNCALIBRATED-CHANNELS': vector('uncalibrated'),
        'COEFFICIENTS'         : vector('coefficients'),
        'MEASUREMENTS'         : vector('measurements'),
        'PARAMETERS'           : vector('parameters')
    }

    linkage = {
        'calibrated'   : obname("CHANNEL"),
        'uncalibrated' : obname("CHANNEL"),
        'coefficients' : obname("CALIBRATION-COEFFICIENT"),
        'measurements' : obname("CALIBRATION-MEASUREMENT"),
        'parameters'   : obname("PARAMETER")
    }

    def __init__(self, obj = None, name = None, type = None):
        super().__init__(obj, name = name, type = 'CALIBRATION')
        #: Computational method used to calibrate the channel
        self.method            = None

        #: Calibrated channels
        self.calibrated        = []

        #: Uncalibrated channels. I.e. the channels as the where before
        #: calibration
        self.uncalibrated      = []

        #: Coefficients
        self.coefficients      = []

        #: Measurements
        self.measurements      = []

        #: Parameters containing numerical and textual information assosiated
        #: with the calibration process.
        self.parameters        = []
