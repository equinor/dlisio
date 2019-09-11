from .basicobject import BasicObject
from .valuetypes import scalar
from .utils import describe_dict

from collections import OrderedDict


class Zone(BasicObject):
    """
    A Zone objects specifies a single interval in depth or time. Other objects
    use zones to define spesific regions in wells or time intervals where the
    object data is valid.

    Attributes
    ----------
    description : str
        Description of the zone
    domain : str
        Type of interval, e.g. borhole-depth, time or vertical-depth
    maximum
        Latest time or deepest point, not inclusive
    minimum
        Earliest time or shallowest point, inclusive

    See also
    --------

    BasicObject : The basic object that Zone is derived from

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
        self.description = None
        self.domain      = None
        self.maximum     = None
        self.minimum     = None

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Description'] = self.description
        d['Domain']      = self.domain
        d['Interval']    = '[{}, {})'.format(self.minimum, self.maximum)

        describe_dict(buf, d, width, indent, exclude)
