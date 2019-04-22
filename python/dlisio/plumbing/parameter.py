from .basicobject import BasicObject
from .valuetypes import scalar


class Parameter(BasicObject):
    """Parameter

    A parameter object describes a parameter used in the acquisition and
    processing of data.  The parameter value(s) may be scalars or an array. In
    the later case, the structure of the array is defined in the dimension
    attribute. The zone attribute specifies which zone(s) the parameter is
    defined. If there are no zone(s) the parameter is defined everywhere.

    Notes
    -----

    The Parameter object reflects the logical record type PARAMETER, described
    in rp66. PARAMETER objects are defined in Appendix A.2 - Logical Record
    Types, described in detail in Chapter 5.8.2 - Static and Frame Data,
    PARAMETER objects.
    """
    attributes = {
        'LONG-NAME' : scalar('long_name'),
        'DIMENSION' : scalar('dimension'),
        'AXIS'      : scalar('axis'),
        'ZONES'     : scalar('zones'),
        'VALUES'    : scalar('values')
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'PARAMETER')
        #: Descriptive name of the channel.
        self.long_name = None

        #: Dimensions of the parameter values
        self.dimension = None

        #: Coordinate axes of the parameter values
        self.axis      = None

        #: Mutually disjoint intervals where the parameter values is constant
        self.zones     = None

        #: Parameter values
        self.values    = None
