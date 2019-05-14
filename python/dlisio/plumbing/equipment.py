from .basicobject import BasicObject
from .valuetypes import scalar, boolean


class Equipment(BasicObject):
    """Equipment

    Equipment objects contains information about individual pieces of surface
    and downhole equipment used in the acquistion of the data. Typically, tools
    (specified by the Tool object) is a composition of equipment.

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

        #: The producer's name for the equipment
        self.trademark_name = None

        #: Operational status
        self.status         = None

        #: Generic type
        self.generic_type   = None

        #: Serial number
        self.serial_number  = None

        #: General location of equipment during acqusition
        self.location       = None

        #: Height
        self.height         = None

        #: Lenght
        self.length         = None

        #: Minimum diameter
        self.diameter_min   = None

        #: Maximum diameter
        self.diameter_max   = None

        #: Volume
        self.volume         = None

        #: Weight
        self.weight         = None

        #: Hole size
        self.hole_size      = None

        #: Pressure
        self.pressure       = None

        #: Temperature
        self.temperature    = None

        #: Vertical depth
        self.vertical_depth = None

        #: Radial drift
        self.radial_drift   = None

        #: Angular drift
        self.angular_drift  = None
