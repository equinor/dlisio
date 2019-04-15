from .basicobject import BasicObject

import logging

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
        'METHOD'               : ('method'           , False),
        'CALIBRATED-CHANNELS'  : ('calibrated_refs'  , False),
        'UNCALIBRATED-CHANNELS': ('uncalibrated_refs', False),
        'COEFFICIENTS'         : ('coefficients'     , False),
        'MEASUREMENTS'         : ('measurement_refs' , False),
        'PARAMETERS'           : ('parameters_refs'  , False)
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

        #: Reference to the calibrated channels
        self.calibrated_refs   = []

        #: Reference to the uncalibrated channels
        self.uncalibrated_refs = []

        #: Reference to measurements
        self.measurement_refs      = []

        #: References to the parameters
        self.parameters_refs   = []

    def link(self, objects, sets):
        channels = sets['CHANNEL']

        calibs = []
        for ref in self.calibrated_refs:
            fp = ref.fingerprint('CHANNEL')
            try:
                calibs.append(channels[fp])
            except KeyError:
                msg = 'missing channel {} referenced from calibration {}'
                logging.warning(msg.format(ref, self.name))

        uncalibs = []
        for ref in self.uncalibrated_refs:
            fp = ref.fingerprint('CHANNEL')
            try:
                uncalibs.append(channels[fp])
            except KeyError:
                msg = 'missing channel {} referenced from calibration {}'
                logging.warning(msg.format(ref, self.name))

        measurements = sets['CALIBRATION-MEASUREMENT']
        measures = []
        for ref in self.measurement_refs:
            fp = ref.fingerprint('CALIBRATION-MEASUREMENT')
            try:
                measures.append(measurements[fp])
            except KeyError:
                msg = 'missing coefficient {} referenced from calibration {}'
                logging.warning(msg.format(ref, self.name))

        parameters = sets['PARAMETER']
        params = []
        for ref in self.parameters_refs:
            fp = ref.fingerprint('PARAMETER')
            try:
                params.append(parameters[fp])
            except KeyError:
                msg = 'missing parameter {} referenced from calibration {}'
                logging.warning(msg.format(ref, self.name))

        self.calibrated = calibs
        self.uncalibrated = uncalibs
        self.measurements = measures
        self.parameters = params
