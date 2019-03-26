from .basicobject import BasicObject


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
    def __init__(self, obj = None):
        super().__init__(obj, "PARAMETER")
        self._long_name = None
        self._dimension = None
        self._axis      = None
        self._zones     = None
        self._values    = None


    @staticmethod
    def load(obj):
        self = Parameter(obj)
        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "LONG-NAME" : self._long_name = attr.value[0]
            if attr.label == "DIMENSION" : self._dimension = attr.value
            if attr.label == "AXIS"      : self._axis      = attr.value
            if attr.label == "ZONES"     : self._zones     = attr.value

        self.stripspaces()
        return self

    @property
    def long_name(self):
        """Long name

        Long descriptive name of the parameter.

        A long_name can be either:
        1. A unstructured desciptive string
        2. An dlis.core.obname referencing a Longname object

        Returns
        -------

        long_name : str or dlisio.core.obname
        """
        return self._long_name

    @property
    def dimension(self):
        """Dimension

        The array structure of each parameter value. Each element in
        *dimension* specifies the number of elements along each dimension of
        the parameter value array's. The dimensionality of the arrays is
        implicitly given by len(dimension). E.g: if **dimension = [10, 50,
        20]** then each element in Parameter.values is a 3-dimensional array of
        size 10x50x20.

        Notes
        -----

        The dimension attribute is defined in rp66, Chapter 4.4.3 - DIMENSION
        Attribute

        Returns
        -------

        dimension : list of int
        """
        return self._dimension

    @property
    def axis(self):
        """Axis

        The axes of the parameter values.

        Notes
        -----

        The axis attribute is defined in rp66, Chapter 4.4.4 - AXIS
        Attribute

        Returns
        -------

        axis : list of dlisio.core.obname
            each element is a reference to an axis object
        """
        return self._axis

    @property
    def zones(self):
        """Zones

        A list of mutually disjoint intervals where the parameter value is
        constant. If present, the parameter is only defined in the zones
        defined by the zone objects. Elsewhere it is undefined. If there is no
        defined zones, the parameter is said to be defined everywhere.

        Returns
        -------

        zones : list of dlisio.core.obname
            each element is a reference to a zone object
        """
        return self._zones

    @property
    def values(self):
        """Values

        List of parameter values as defined by *Parameter.zones* and
        *Parameter.dimension* If there is no defined zones, values should
        contain only one element. Otherwise, values will contain one element
        (parameter value) for each zone defined in *Parameter.zones*.

        The structure of each element is defined by *Parameter.dimension*.

        Returns
        -------

        values : list of undefined type
        """
        return self._values
