from .basicobject import BasicObject
from .valuetypes import scalar, vector, reverse
from .linkage import obname
from .utils import sampling, zonify

import numpy as np

class Parameter(BasicObject):
    """Parameter

    A parameter object describes a parameter used in the acquisition and
    processing of data.  The parameter value(s) may be scalars or an array. In
    the later case, the structure of the array is defined in the dimension
    attribute. The zone attribute specifies which zone(s) the parameter is
    defined. If there are no zone(s) the parameter is defined everywhere.

    See also
    --------

    BasicObject : The basic object that Parameter is derived from

    Notes
    -----

    The Parameter object reflects the logical record type PARAMETER, described
    in rp66. PARAMETER objects are defined in Appendix A.2 - Logical Record
    Types, described in detail in Chapter 5.8.2 - Static and Frame Data,
    PARAMETER objects.
    """
    attributes = {
        'LONG-NAME' : scalar('long_name'),
        'DIMENSION' : reverse('dimension'),
        'AXIS'      : reverse('axis'),
        'ZONES'     : vector('zones'),
    }

    linkage = {
        'long_name' : obname("LONG-NAME"),
        'axis'      : obname("AXIS"),
        'zones'     : obname("ZONE")
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'PARAMETER')
        #: Descriptive name of the channel.
        self.long_name = None

        #: Dimensions of the parameter values
        self.dimension = []

        #: Coordinate axes of the parameter values
        self.axis      = []

        #: Mutually disjoint intervals where the parameter values is constant
        self.zones     = []

    @property
    def values(self):
        """ Parameter values uses a dict interface

        Parameter value(s) may be scalar or array's. The size/dimensionallity
        of each value is defined in the dimensions attribute. The values are
        only defined in certain zones. If no zones are defined, the value is
        said to be unzoned, i.e. it is defined everywere.

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
