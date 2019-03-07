from .basicobject import BasicObject


class Parameter(BasicObject):
    """
    The Parameter object reflects the logical record type PARAMETER (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.8.2 - Static
    and Frame Data, PARAMETER objects)
    """
    def __init__(self, obj):
        super().__init__(obj, "parameter")
        self._long_name = None
        self._dimension = None
        self._axis      = None
        self._zones     = None
        self._values    = None

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "LONG-NAME" : self._long_name = attr.value[0]
            if attr.label == "DIMENSION" : self._dimension = attr.value
            if attr.label == "AXIS"      : self._axis      = attr.value
            if attr.label == "ZONES"     : self._zones     = attr.value

        self.stripspaces()

    @property
    def long_name(self):
        return self._long_name

    @property
    def dimension(self):
        return self._dimension

    @property
    def axis(self):
        return self._axis

    @property
    def zones(self):
        return self._zones

    @property
    def values(self):
        return self._values
