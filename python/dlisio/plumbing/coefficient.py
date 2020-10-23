from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .utils import *

from collections import OrderedDict

class Coefficient(BasicObject):
    """
    Records of measurements, references, and tolerances used in the calibration
    of channels.

    Attributes
    ----------

    label : str
        Identify the coefficient-role in the calibration process

    coefficients : list
        Coefficients corresponding to the label

    references : list
        Nominal values for each coefficient

    plus_tolerance : list
        Maximum value that a sample can exceed the reference and still be
        "within tolerance"

    minus_tolerance : list
        Maximum value that a sample can fall below the reference and still
        be "within tolerance"

    See also
    --------

    BasicObject : The basic object that Coefficient is derived from

    Notes
    -----

    The Coefficient object reflects the logical record type
    CALIBRATION-COEFFICIENT, defined in rp66. CALIBRATION-COEFFICIENT records
    are listed in Appendix A.2 - Logical Record Types and described in detail
    in Chapter 5.8.7.2 - Static and Frame Data, CALIBRATION-COEFFICIENT
    objects.
    """
    attributes = {
        "LABEL"           : scalar,
        "COEFFICIENTS"    : vector,
        "REFERENCES"      : vector,
        "PLUS-TOLERANCES" : vector,
        "MINUS-TOLERANCES": vector,
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def label(self):
        return self['LABEL']

    @property
    def coefficients(self):
        return self['COEFFICIENTS']

    @property
    def references(self):
        return self['REFERENCES']

    @property
    def plus_tolerance(self):
        return self['PLUS-TOLERANCES']

    @property
    def minus_tolerance(self):
        return self['MINUS-TOLERANCES']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Coefficient type']   = self.label
        d['Number of value(s)'] = len(self.coefficients)

        describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Reference value(s)'] =  'REFERENCES'
        d['Minus Tolerance(s)'] =  'PLUS-TOLERANCES'
        d['Plus Tolerance(s)']  =  'MINUS-TOLERANCES'

        describe_sampled_attrs(
                buf,
                self.attic,
                [1],
                'COEFFICIENTS',
                d,
                width,
                indent,
                exclude,
                single=False
        )
