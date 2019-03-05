from .basic_object import basic_object


class Calibration(basic_object):
    """
    The Calibration reflects the logical record type CALIBRATION (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.8.7.3 - Static and
    Frame Data, CALIBRATION objects)

    The calibrated_channels and uncalibrated_channels attributes are lists of
    refrences to Channel objects.
    """
    def __init__(self, obj):
        super().__init__(obj, "calibration")
        self.method               = None
        self.calibrated_channel   = []
        self.uncalibrated_channel = []
        self.coefficients         = []
        self.parameters           = []

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "METHOD":
                self.method = attr.value[0]
            if attr.label == "CALIBRATED-CHANNELS":
                self.calibrated_channel = attr.value
            if attr.label == "UNCALIBRATED-CHANNELS":
                self.uncalibrated_channel = attr.value
            if attr.label == "COEFFICIENTS":
                self.coefficients = attr.value
            if attr.label == "PARAMETERS":
                self.parameters = attr.value

        self.stripspaces()

    def hasuncalibrated_channel(self, channel):
        """
        Return True if channels is in Calibration.uncal_ch,
        else return False

        Parameters
        ----------
        channel : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        hasuncalchannel : bool
            True if Calibration has the channel obj in uncal_ch, else False

        """
        return self.contains(self.uncalibrated_channel, channel)

    def hascalibrated_channel(self, channel):
        """
        Return True if channels is in Calibration.cal_ch,
        else return False

        Parameters
        ----------
        channel : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        hasuncalchannel : bool
            True if Calibration has the channel obj in self.cal_ch, else False

        """
        return self.contains(self.calibrated_channel, channel)

    def hasparameter(self, param):
        """
        Return True if parameter is in calibration.parameter,
        else return False

        Parameters
        ----------
        param : dlis.core.obname, tuple(str, int, int)

        Returns
        -------
        hasparameter : bool
            True if Calibration has the param obj, else False

        """
        return self.contains(self.parameters, param)
