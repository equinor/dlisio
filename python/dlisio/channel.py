from .basic_object import basic_object


class Channel(basic_object):
    """
    The Channel object reflects the logical record type CHANNEL (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.5.1 - Static and
    Frame Data, CHANNEL objects).
    """
    def __init__(self, obj):
        super().__init__(obj, "channel")
        self.long_name     = None
        self.reprc         = None
        self.units         = None
        self.properties    = []
        self.dimension     = []
        self.axis          = []
        self.element_limit = []
        self.source        = None

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "LONG-NAME"          : self.long_name     = attr.value[0]
            if attr.label == "REPRESENTATION-CODE": self.reprc         = attr.value[0]
            if attr.label == "UNITS"              : self.units         = attr.value[0]
            if attr.label == "PROPERTIES"         : self.properties    = attr.value
            if attr.label == "DIMENSION"          : self.dimension     = attr.value
            if attr.label == "AXIS"               : self.axis          = attr.value
            if attr.label == "ELEMENT-LIMIT"      : self.element_limit = attr.value
            if attr.label == "SOURCE"             : self.source        = attr.value[0]

        self.stripspaces()

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
