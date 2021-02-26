from collections import OrderedDict

from .basicobject import BasicObject
from . import utils


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
        'DESCRIPTION': utils.scalar,
        'DOMAIN'     : utils.scalar,
        'MAXIMUM'    : utils.scalar,
        'MINIMUM'    : utils.scalar,
    }


    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def description(self):
        return self['DESCRIPTION']

    @property
    def domain(self):
        return self['DOMAIN']

    @property
    def maximum(self):
        return self['MAXIMUM']

    @property
    def minimum(self):
        return self['MINIMUM']


    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Description'] = self.description
        d['Domain']      = 'DOMAIN'
        d['Minimum']     = 'MINIMUM'
        d['Maximum']     = 'MAXIMUM'

        utils.describe_attributes(buf, d, self, width, indent, exclude)
