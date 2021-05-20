from collections import OrderedDict

from .basicobject import BasicObject
from . import utils

class Calibration(BasicObject):
    """
    Calibration objects are a collection of measurements and coefficients that
    defines the calibration process of channel objects.

    Attributes
    ----------

    method : str
        Computational method used to calibrate the channels

        RP66V1 name: *METHOD*

    calibrated : list(Channel)
        Calibrated channels

        RP66V1 name: *CALIBRATED-CHANNELS*

    uncalibrated : list(Channel)
        Uncalibrated channels. I.e. the channels as they where before
        calibration

        RP66V1 name: *UNCALIBRATED-CHANNELS*

    coefficients : list(Coefficient)
        Coefficients

        RP66V1 name: *COEFFICIENTS*

    measurements : list(Measurement)
        Measurements

        RP66V1 name: *MEASUREMENTS*

    parameters : list(Parameter)
        Parameters containing numerical and textual information assosiated
        with the calibration process.

        RP66V1 name: *PARAMETERS*

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
        'METHOD'               : utils.scalar,
        'CALIBRATED-CHANNELS'  : utils.vector,
        'UNCALIBRATED-CHANNELS': utils.vector,
        'COEFFICIENTS'         : utils.vector,
        'MEASUREMENTS'         : utils.vector,
        'PARAMETERS'           : utils.vector,
    }

    linkage = {
        'CALIBRATED-CHANNELS'   : utils.obname('CHANNEL'),
        'UNCALIBRATED-CHANNELS' : utils.obname('CHANNEL'),
        'COEFFICIENTS'          : utils.obname('CALIBRATION-COEFFICIENT'),
        'MEASUREMENTS'          : utils.obname('CALIBRATION-MEASUREMENT'),
        'PARAMETERS'            : utils.obname('PARAMETER')
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
        d['Calibrated channels']   = utils.replist(self.calibrated  , 'name')
        d['Uncalibrated channels'] = utils.replist(self.uncalibrated, 'name')
        d['Coefficients']          = utils.replist(self.coefficients, 'name')
        d['Measurements']          = utils.replist(self.measurements, 'name')
        d['Parameters']            = utils.replist(self.parameters  , 'name')

        utils.describe_dict(buf, d, width, indent, exclude)
