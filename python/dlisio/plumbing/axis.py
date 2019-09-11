from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .utils import describe_dict

from collections import OrderedDict


class Axis(BasicObject):
    """Axis

    The Axis object describes the coordinate axis of an array, e.g. the sample
    array of channels. One axis object describes only one coordinate axis. I.e
    a three dimensional array is described by three Axis objects.

    Attributes
    ----------

    axis_id : str
        Axis identifier

    coordinates : list
        Explicit coordinate value along the axis

    spacing
        Constant, signed spacing along the axis between successive coordinates

    See also
    --------

    BasicObject : The basic object that Axis is derived from

    Notes
    -----

    The Axis object reflects the logical record type AXIS, defined in rp66.
    AXIS objects are listed in Appendix A.2 - Logical Record Types, and
    described in detail in Chapter 5.3.1 - Static and Frame Data, Axis Objects.
    """
    attributes = {
        'AXIS-ID'     : scalar('axis_id'),
        'COORDINATES' : vector('coordinates'),
        'SPACING'     : scalar('spacing'),
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'AXIS')
        self.axis_id     = None
        self.coordinates = []
        self.spacing     = None

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Description'] = self.axis_id
        d['Spacing']     = self.spacing
        d['Coordinates'] = self.coordinates

        describe_dict(buf, d, width, indent, exclude)
