from .basicobject import BasicObject
from .valuetypes import scalar


class Zone(BasicObject):
    """Zone

    A Zone objects specifies a single interval in depth or time. Other objects
    use zones to define spesific regions in wells or time intervals where the
    object data is valid.

    Notes
    -----

    The Zone object reflects the logical record type ZONE, defined in rp66.
    ZONE objects are listed in Appendix A.2 - Logical Record Types, and
    described in detail in Chapter 5.8.1 - Static and Frame Data, Zone Objects.
    """
    attributes = {
        'DESCRIPTION': scalar('description'),
        'DOMAIN'     : scalar('domain'),
        'MAXIMUM'    : scalar('maximum'),
        'MINIMUM'    : scalar('minimum')
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'ZONE')
        #: Description of the zone
        self.description = None

        #: Type of interval, e.g. borhole-depth, time or vertical-depth
        self.domain      = None

        #: Latest time or deepest point, not inclusive
        self.maximum     = None

        #: Earliest time or shallowest point, inclusive
        self.minimum     = None
