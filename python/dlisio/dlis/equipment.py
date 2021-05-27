from collections import OrderedDict

from .basicobject import BasicObject
from . import utils


class Equipment(BasicObject):
    """
    Equipment objects contains information about individual pieces of surface
    and downhole equipment used in the acquistion of the data. Typically, tools
    (specified by the Tool object) is a composition of equipment.

    Attributes
    ----------

    trademark_name : str
        The producer's name for the equipment

        RP66V1 name: *TRADEMARK-NAME*

    status : bool
        Operational status

        RP66V1 name: *STATUS*

    generic_type : str
        Generic type

        RP66V1 name: *TYPE*

    serial_number : str
        Serial number

        RP66V1 name: *SERIAL-NUMBER*

    location : str
        General location of equipment during acqusition

        RP66V1 name: *LOCATION*

    height
        Heigth

        RP66V1 name: *HEIGHT*

    length
        Length

        RP66V1 name: *LENGTH*

    diameter_min
        Minimum diameter

        RP66V1 name: *MINIMUM-DIAMETER*

    diameter_max
        Maximum diameter

        RP66V1 name: *MAXIMUM-DIAMETER*

    volume
        Volume

        RP66V1 name: *VOLUME*

    weight
        Weight

        RP66V1 name: *WEIGHT*

    hole_size
        Hole size

        RP66V1 name: *HOLE-SIZE*

    pressure
        Pressure

        RP66V1 name: *PRESSURE*

    temperature
        Temperature

        RP66V1 name: *TEMPERATURE*

    vertical_depth
        Vertical depth

        RP66V1 name: *VERTICAL-DEPTH*

    radial_drift
        Radial drift

        RP66V1 name: *RADIAL-DRIFT*

    angular_drift
        Angular drift

        RP66V1 name: *ANGULAR-DRIFT*

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
        'TRADEMARK-NAME'  : utils.scalar,
        'STATUS'          : utils.boolean,
        'TYPE'            : utils.scalar,
        'SERIAL-NUMBER'   : utils.scalar,
        'LOCATION'        : utils.scalar,
        'HEIGHT'          : utils.scalar,
        'LENGTH'          : utils.scalar,
        'MINIMUM-DIAMETER': utils.scalar,
        'MAXIMUM-DIAMETER': utils.scalar,
        'VOLUME'          : utils.scalar,
        'WEIGHT'          : utils.scalar,
        'HOLE-SIZE'       : utils.scalar,
        'PRESSURE'        : utils.scalar,
        'TEMPERATURE'     : utils.scalar,
        'VERTICAL-DEPTH'  : utils.scalar,
        'RADIAL-DRIFT'    : utils.scalar,
        'ANGULAR-DRIFT'   : utils.scalar,
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
        utils.describe_attributes(buf, d, self, width, indent, exclude)

        d = OrderedDict()
        d['Height']         = 'HEIGHT'
        d['Length']         = 'LENGTH'
        d['Diameter (min)'] = 'MINIMUM-DIAMETER'
        d['Diameter (max)'] = 'MAXIMUM-DIAMETER'
        d['Volume']         = 'VOLUME'
        d['Weight']         = 'WEIGHT'

        utils.describe_attributes(buf, d, self, width, indent, exclude)

        d = OrderedDict()
        d['Minimum borehole size'] = 'HOLE-SIZE'
        d['Max pressure']          = 'PRESSURE'
        d['Max temperature']       = 'TEMPERATURE'

        utils.describe_attributes(buf, d, self, width, indent, exclude)

        d = OrderedDict()
        d['Vertical depth'] = 'VERTICAL-DEPTH'
        d['Radial drift ']  = 'RADIAL-DRIFT'
        d['Angular drift']  = 'ANGULAR-DRIFT'

        utils.describe_attributes(buf, d, self, width, indent, exclude)
