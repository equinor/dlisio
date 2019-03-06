from .basic_object import basic_object


class Channel(basic_object):
    """
    The Channel object reflects the logical record type CHANNEL (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.5.1 - Static and
    Frame Data, CHANNEL objects).
    """
    def __init__(self, obj):
        super().__init__(obj, "channel")
        self._long_name     = None
        self._reprc         = None
        self._units         = None
        self._properties    = []
        self._dimension     = []
        self._axis          = []
        self._element_limit = []
        self._source        = None

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "LONG-NAME"          : self._long_name     = attr.value[0]
            if attr.label == "REPRESENTATION-CODE": self._reprc         = attr.value[0]
            if attr.label == "UNITS"              : self._units         = attr.value[0]
            if attr.label == "PROPERTIES"         : self._properties    = attr.value
            if attr.label == "DIMENSION"          : self._dimension     = attr.value
            if attr.label == "AXIS"               : self._axis          = attr.value
            if attr.label == "ELEMENT-LIMIT"      : self._element_limit = attr.value
            if attr.label == "SOURCE"             : self._source        = attr.value[0]

        self.stripspaces()

    @property
    def long_name(self):
        return self._long_name

    @property
    def reprc(self):
        return self._reprc

    @property
    def units(self):
        return self._units

    @property
    def properties(self):
        return self._properties

    @property
    def dimension(self):
        return self._dimension

    @property
    def axis(self):
        return self._axis

    @property
    def element_limit(self):
        return self._element_limit

    @property
    def source(self):
        return self._source

    def hassource(self, obj):
        """
        Check if obj is the source of channel

        Parameters
        ----------
        obj : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        issource : bool
            True if obj is the source of channel, else False

        """
        return self.contains(self.source, obj)
