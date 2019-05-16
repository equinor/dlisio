from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .linkage import obname, objref

class Computation(BasicObject):
    """Computation

    Results of computations that are more appropriately expressed as static
    information rather than as channels.

    Notes
    -----

    The Computation object reflects the logical record type COMPUTATION,
    defined in rp66.  COMPUTATION objects are listed in Appendix A.2 - Logical
    Record Types, and described in detail in Chapter 5.8.6 - Static and Frame
    Data, COMPUTATION objects.
    """

    attributes = {
        'LONG-NAME' : scalar('long_name'),
        'PROPERTIES': vector('properties'),
        'DIMENSION' : vector('dimension'),
        'AXIS'      : vector('axis'),
        'ZONES'     : vector('zones'),
        'VALUES'    : vector('values'),
        'SOURCE'    : vector('source')
    }

    linkage = {
        'long-name' : obname('LONG-NAME'),
        'axis'      : obname('AXIS'),
        'zones'     : obname('ZONE'),
        'source'    : objref
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'COMPUTATION')
        #: Descriptive name of the computation
        self.long_name   = None

        #:Property indicators that summarizes the characteristics of the computation
        #: and the processing that has occurred to produce it
        self.properties  = []

        #: Array structure of a single value
        self.dimension   = []

        #: Coordinate axes of the values
        self.axis        = []

        #: Mutually disjoint zones over which the value of the current
        #: computation is constant
        self.zones       = []

        #: Computational values
        self.values      = []

        #: The immediate source of the Computation
        self.source = []
