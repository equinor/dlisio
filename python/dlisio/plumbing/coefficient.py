from .basicobject import BasicObject
from .valuetypes import scalar, vector

class Coefficient(BasicObject):
    """Coefficient

    Records of measurements, references, and tolerances used in the calibration
    of channels.

    Notes
    -----

    The Coefficient object reflects the logical record type
    CALIBRATION-COEFFICIENT, defined in rp66. CALIBRATION-COEFFICIENT records
    are listed in Appendix A.2 - Logical Record Types and described in detail
    in Chapter 5.8.7.2 - Static and Frame Data, CALIBRATION-COEFFICIENT
    objects.
    """
    attributes = {
        "LABEL"           : scalar('label'),
        "COEFFICIENTS"    : vector('coefficients'),
        "REFERENCES"      : vector('references'),
        "PLUS-TOLERANCES" : vector('plus_tolerance'),
        "MINUS-TOLERANCES": vector('minus_tolerance')
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = "CALIBRATION-COEFFICIENT")
        #: Identify the coefficient-role in the calibration process
        self.label           = None

        #: Coefficients corresponding to the label
        self.coefficients    = []

        #: Nominal values for each coefficient
        self.references      = []

        #: Maximum value that a sample can exceed the reference and still be
        #: "within tolerance"
        self.plus_tolerance  = []

        #: Maximum value that a sample can fall below the reference and still
        #: be "within tolerance"
        self.minus_tolerance = []
