from .basicobject import BasicObject
from .valuetypes import scalar, boolean
from .utils import describe_attributes

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

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

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

        d['Trademark name']     = 'TRADEMARK-NAME'
        d['Generic type']       = 'TYPE'
        d['Operational status'] = 'STATUS'
        d['Serial number']      = 'SERIAL-NUMBER'
        d['Location']           = 'LOCATION'
        describe_attributes(buf, d, self, width, indent, exclude)

        d = OrderedDict()
        d['Height']         = 'HEIGHT'
        d['Length']         = 'LENGTH'
        d['Diameter (min)'] = 'MINIMUM-DIAMETER'
        d['Diameter (max)'] = 'MAXIMUM-DIAMETER'
        d['Volume']         = 'VOLUME'
        d['Weight']         = 'WEIGHT'

        describe_attributes(buf, d, self, width, indent, exclude)

        d = OrderedDict()
        d['Minimum borehole size'] = 'HOLE-SIZE'
        d['Max pressure']          = 'PRESSURE'
        d['Max temperature']       = 'TEMPERATURE'

        describe_attributes(buf, d, self, width, indent, exclude)

        d = OrderedDict()
        d['Vertical depth'] = 'VERTICAL-DEPTH'
        d['Radial drift ']  = 'RADIAL-DRIFT'
        d['Angular drift']  = 'ANGULAR-DRIFT'

        describe_attributes(buf, d, self, width, indent, exclude)
