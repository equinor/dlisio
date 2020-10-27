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
        'METHOD'               : scalar,
        'CALIBRATED-CHANNELS'  : vector,
        'UNCALIBRATED-CHANNELS': vector,
        'COEFFICIENTS'         : vector,
        'MEASUREMENTS'         : vector,
        'PARAMETERS'           : vector,
    }

    linkage = {
        'CALIBRATED-CHANNELS'   : obname('CHANNEL'),
        'UNCALIBRATED-CHANNELS' : obname('CHANNEL'),
        'COEFFICIENTS'          : obname('CALIBRATION-COEFFICIENT'),
        'MEASUREMENTS'          : obname('CALIBRATION-MEASUREMENT'),
        'PARAMETERS'            : obname('PARAMETER')
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def method(self):
        return self['METHOD']

    @property
    def calibrated(self):
        return self['CALIBRATED-CHANNELS']

    @property
    def uncalibrated(self):
        return self['UNCALIBRATED-CHANNELS']

    @property
    def coefficients(self):
        return self['COEFFICIENTS']

    @property
    def measurements(self):
        return self['MEASUREMENTS']

    @property
    def parameters(self):
        return self['PARAMETERS']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Computational method']  = self.method
        d['Calibrated channels']   = replist(self.calibrated  , 'name')
        d['Uncalibrated channels'] = replist(self.uncalibrated, 'name')
        d['Coefficients']          = replist(self.coefficients, 'name')
        d['Measurements']          = replist(self.measurements, 'name')
        d['Parameters']            = replist(self.parameters  , 'name')

        describe_dict(buf, d, width, indent, exclude)
