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
    def __init__(self, obj = None):
        super().__init__(obj, "CALIBRATION")
        self._method               = None
        self._calibrated_channel   = []
        self._uncalibrated_channel = []
        self._coefficients         = []
        self._parameters           = []

        self.parameters_refs       = []
        self.calibrated_refs       = []
        self.uncalibrated_refs     = []

    @staticmethod
    def load(obj):
        self = Calibration(obj)
        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "METHOD":
                self._method = attr.value[0]
            if attr.label == "CALIBRATED-CHANNELS":
                self.calibrated_refs = attr.value
            if attr.label == "UNCALIBRATED-CHANNELS":
                self.uncalibrated_refs = attr.value
            if attr.label == "COEFFICIENTS":
                self._coefficients = attr.value
            if attr.label == "PARAMETERS":
                self.parameters_refs = attr.value

        self.stripspaces()
        return self

    @property
    def method(self):
        """Method

        The computational method used to calibrate the Channel object(s)
        defined in *Calibration.calibrated_channel*.

        Returns
        -------

        method : str
        """
        return self._method

    @property
    def calibrated_channel(self):
        """Calibrated channel(s)

        List of channels that have been calibrated by the method and
        coefficients described in this calibration object.

        Returns
        -------

        calibrated_channel : list of dlisio.Channel
        """
        return self._calibrated_channel

    @property
    def uncalibrated_channel(self):
        """Uncalibrated channel(s)

        List of uncalibrated channels that along with the method and
        coefficients makes up the calibrated channels. I.e. the channels as
        they where before calibration.

        Returns
        -------

        uncalibrated_channel : list of dlisio.Channel
        """
        return self._uncalibrated_channel

    @property
    def coefficients(self):
        """Coefficients

        List of coefficient objects that contains coefficients, tolerances and
        references that have been used in the calibration of the channels
        listen in *Calibration.calibrated_channels*.

        Returns
        -------

        coefficients : list of dlisio.core.obname
            each element is a reference to an coefficient object
        """
        return self._coefficients

    @property
    def parameters(self):
        """Parameters

        List of parameter objects that contains both numerical and textual
        information assosiated with the calibration process.

        Returns
        -------

        parameters : list of dlisio.Parameter
        """
        return self._parameters

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

        parameters = sets['PARAMETER']
        params = []
        for ref in self.parameters_refs:
            fp = ref.fingerprint('PARAMETER')
            try:
                params.append(parameters[fp])
            except KeyError:
                msg = 'missing parameter {} referenced from calibration {}'
                logging.warning(msg.format(ref, self.name))

        self._calibrated_channel = calibs
        self._uncalibrated_channel = uncalibs
        self._parameters = params
