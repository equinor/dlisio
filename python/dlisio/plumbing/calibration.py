from .basicobject import BasicObject
from .valuetypes import vector, scalar
from .linkage import obname
from .utils import describe_dict, replist

from collections import OrderedDict

class Calibration(BasicObject):
    """
    Calibration objects are a collection of measurements and coefficients that
    defines the calibration process of channel objects.

    Attributes
    ----------

    method : str
        Computational method used to calibrate the channels

    calibrated : list(Channel)
        Calibrated channels

    uncalibrated : list(Channel)
        Uncalibrated channels. I.e. the channels as they where before
        calibration

    coefficients : list(Coefficient)
        Coefficients

    measurements : list(Measurement)
        Measurements

    parameters : list(Parameter)
        Parameters containing numerical and textual information assosiated
        with the calibration process.

    See also
    --------

    BasicObject : The basic object that Calibration is derived from

    Notes
    -----

    The Calibration reflects the logical record type CALIBRATION, defined in
    rp66. CALIBRATION records are listen in Appendix A.2 - Logical Record
    Types and described detail in Chapter 5.8.7.3 - Static and Frame Data,
    CALIBRATION objects.
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

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'CALIBRATION')
        self.method            = None
        self.calibrated        = []
        self.uncalibrated      = []
        self.coefficients      = []
        self.measurements      = []
        self.parameters        = []

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Computational method']  = self.method
        d['Calibrated channels']   = replist(self.calibrated  , 'name')
        d['Uncalibrated channels'] = replist(self.uncalibrated, 'name')
        d['Coefficients']          = replist(self.coefficients, 'name')
        d['Measurements']          = replist(self.measurements, 'name')
        d['Parameters']            = replist(self.parameters  , 'name')

        describe_dict(buf, d, width, indent, exclude)
