from .basicobject import BasicObject
from .valuetypes import scalar, vector


class Axis(BasicObject):
    """Axis

    The Axis object describes the coordinate axis of an array, e.g. the sample
    array of channels. One axis object describes only one coordinate axis. I.e
    a three dimensional array is described by three Axis objects.

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
        #: Axis identifier
        self.axis_id     = None

        #: Explicit coordinate value along the axis
        self.coordinates = []

        #: Constant, signed spacing along the axis between successive
        #: coordinates
        self.spacing     = None
