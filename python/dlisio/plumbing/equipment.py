from .basicobject import BasicObject
from .valuetypes import scalar, boolean
from .utils import describe_dict

from collections import OrderedDict


class Equipment(BasicObject):
    """
    Equipment objects contains information about individual pieces of surface
    and downhole equipment used in the acquistion of the data. Typically, tools
    (specified by the Tool object) is a composition of equipment.

    Attributes
    ----------

    trademark_name : str
        The producer's name for the equipment

    status : bool
        Operational status

    generic_type : str
        Generic type

    serial_number : str
        Serial number

    location : str
        General location of equipment during acqusition

    height
        Heigth

    length
        Length

    diameter_min
        Minimum diameter

    diameter_max
        Maximum diameter

    volume
        Volume

    weight
        Weight

    hole_size
        Hole size

    pressure
        Pressure

    temperature
        Temperature

    vertical_depth
        Vertical depth

    radial_drift
        Radial drift

    angular_drift
        Angular drift

    See also
    --------

    BasicObject : The basic object that Equipment is derived from

    Notes
    -----

    The Equipment object reflects the logical record type EQUIPMENT, defined in
    rp66. EQUIPMENT records are listed in Appendix A.2 - Logical Record Types and
    described in detail in Chapter 5.8.3 - Static and Frame Data, EQUIPMENT
    objects.
    """
    attributes = {
        'TRADEMARK-NAME'  : scalar,
        'STATUS'          : boolean,
        'TYPE'            : scalar,
        'SERIAL-NUMBER'   : scalar,
        'LOCATION'        : scalar,
        'HEIGHT'          : scalar,
        'LENGTH'          : scalar,
        'MINIMUM-DIAMETER': scalar,
        'MAXIMUM-DIAMETER': scalar,
        'VOLUME'          : scalar,
        'WEIGHT'          : scalar,
        'HOLE-SIZE'       : scalar,
        'PRESSURE'        : scalar,
        'TEMPERATURE'     : scalar,
        'VERTICAL-DEPTH'  : scalar,
        'RADIAL-DRIFT'    : scalar,
        'ANGULAR-DRIFT'   : scalar,
    }

    def __init__(self, obj = None, name = None, lf = None):
        super().__init__(obj, name = name, type = 'EQUIPMENT', lf = lf)

    @property
    def trademark_name(self):
        return self['TRADEMARK-NAME']

    @property
    def status(self):
        return self['STATUS']

    @property
    def generic_type(self):
        return self['TYPE']

    @property
    def serial_number(self):
        return self['SERIAL-NUMBER']

    @property
    def location(self):
        return self['LOCATION']

    @property
    def height(self):
        return self['HEIGHT']

    @property
    def length(self):
        return self['LENGTH']

    @property
    def diameter_min(self):
        return self['MINIMUM-DIAMETER']

    @property
    def diameter_max(self):
        return self['MAXIMUM-DIAMETER']

    @property
    def volume(self):
        return self['VOLUME']

    @property
    def weight(self):
        return self['WEIGHT']

    @property
    def hole_size(self):
        return self['HOLE-SIZE']

    @property
    def pressure(self):
        return self['PRESSURE']

    @property
    def temperature(self):
        return self['TEMPERATURE']

    @property
    def vertical_depth(self):
        return self['VERTICAL-DEPTH']

    @property
    def radial_drift(self):
        return self['RADIAL-DRIFT']

    @property
    def angular_drift(self):
        return self['ANGULAR-DRIFT']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Trademark name']     = self.trademark_name
        d['Generic type']       = self.generic_type
        d['Operational status'] = self.status
        d['Serial number']      = self.serial_number
        d['Location']           = self.location
        describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Height, Length']      = [self.height, self.length]
        d['Diameter (min, max)'] = [self.diameter_min, self.diameter_max]
        d['Volume']              = self.volume
        d['Weight']              = self.weight

        describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Minimum borehole size'] = self.hole_size
        d['Max pressure']          = self.pressure
        d['Max temperature']       = self.temperature

        describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Vertical depth'] = self.vertical_depth
        d['Radial drift ']  = self.radial_drift
        d['Angular drift']  = self.angular_drift

        describe_dict(buf, d, width, indent, exclude)
