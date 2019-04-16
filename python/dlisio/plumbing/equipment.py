from .basicobject import BasicObject


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
        'TRADEMARK-NAME'  : ('trademark_name', True),
        'STATUS'          : ('status'        , True),
        'TYPE'            : ('generic_type'  , True),
        'SERIAL-NUMBER'   : ('serial_number' , True),
        'LOCATION'        : ('location'      , True),
        'HEIGHT'          : ('height'        , True),
        'LENGTH'          : ('length'        , True),
        'MINIMUM-DIAMETER': ('diameter_min'  , True),
        'MAXIMUM-DIAMETER': ('diameter_max'  , True),
        'VOLUME'          : ('volume'        , True),
        'WEIGHT'          : ('weight'        , True),
        'HOLE-SIZE'       : ('hole_size'     , True),
        'PRESSURE'        : ('pressure'      , True),
        'TEMPERATURE'     : ('temperature'   , True),
        'VERTICAL-DEPTH'  : ('vertical_depth', True),
        'RADIAL-DRIFT'    : ('radial_drift'  , True),
        'AGULAR-DRIFT'    : ('angular_drift' , True)
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
