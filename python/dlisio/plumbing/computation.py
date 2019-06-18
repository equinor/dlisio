from .basicobject import BasicObject
from .valuetypes import scalar, vector, reverse
from .linkage import obname, objref
from .utils import sampling, zonify

import numpy as np


class Computation(BasicObject):
    """
    Results of computations that are more appropriately expressed as static
    information rather than as channels.

    Computation values are indexed by the zone they are defined in. If no zones
    are defined, the computation is *unzoned* and there should only be one
    computation value. Unzoned computation values are defined everywhere. Note
    that each computation value may be scalar or an ndarray.

    The axis attribute, if present, defines axis labels for multidimensional
    samples.

    See also
    --------

    BasicObject : The basic object that Computation is derived from

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
        'DIMENSION' : reverse('dimension'),
        'AXIS'      : reverse('axis'),
        'ZONES'     : vector('zones'),
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

        #: The immediate source of the Computation
        self.source = []

    @property
    def values(self):
        """ Computation values uses a dict interface

        Computation value(s) may be scalar or array's. The values are only
        defined in certain zones. If no zones are defined, the value is said to
        be unzoned, i.e. it is defined everywere.

        Returns
        -------

        values : dict
            indexed by Zone

        Notes
        -----

        If there is no values or DLISIO is unable to structure the samples due
        to insufficient or contradictory information in the object, the
        unstructured array is return as is and can be accessed under the label
        *RAW*. Note that in this case the standard deem the meaning of the
        values to be undefined.

        If Zones are missing, DLISIO uses defaulted zonelabels.

        Examples
        --------

        Values from a spesific zone:

        >>> parameter.values['ZONE-C']
        [10, 20, 30]

        Values from each zone:

        >>>  zone, value in parameter.values.items():
        ...     print(zone, value)
        'ZONE-A' [120, 130, 140]
        'ZONE-B' [160, 170, 180]
        """
        try:
            data = self.attic['VALUES']
        except KeyError:
            return {'RAW' : np.empty(0)}

        try:
            sampled = sampling(data, self.dimension, count=len(self.zones))
        except ValueError:
            return {'RAW' : np.array(data)}

        return zonify(self.zones, sampled)
