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
        'TRADEMARK-NAME'  : scalar('trademark_name'),
        'STATUS'          : boolean('status'),
        'TYPE'            : scalar('generic_type'),
        'SERIAL-NUMBER'   : scalar('serial_number'),
        'LOCATION'        : scalar('location'),
        'HEIGHT'          : scalar('height'),
        'LENGTH'          : scalar('length'),
        'MINIMUM-DIAMETER': scalar('diameter_min'),
        'MAXIMUM-DIAMETER': scalar('diameter_max'),
        'VOLUME'          : scalar('volume'),
        'WEIGHT'          : scalar('weight'),
        'HOLE-SIZE'       : scalar('hole_size'),
        'PRESSURE'        : scalar('pressure'),
        'TEMPERATURE'     : scalar('temperature'),
        'VERTICAL-DEPTH'  : scalar('vertical_depth'),
        'RADIAL-DRIFT'    : scalar('radial_drift'),
        'ANGULAR-DRIFT'   : scalar('angular_drift')
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'EQUIPMENT')

        self.trademark_name = None
        self.status         = None
        self.generic_type   = None
        self.serial_number  = None
        self.location       = None
        self.height         = None
        self.length         = None
        self.diameter_min   = None
        self.diameter_max   = None
        self.volume         = None
        self.weight         = None
        self.hole_size      = None
        self.pressure       = None
        self.temperature    = None
        self.vertical_depth = None
        self.radial_drift   = None
        self.angular_drift  = None

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
