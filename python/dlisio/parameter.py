from .basic_object import basic_object


class Parameter(basic_object):
    """
    The Parameter object reflects the logical record type PARAMETER (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.8.2 - Static
    and Frame Data, PARAMETER objects)
    """
    def __init__(self, obj):
        super().__init__(obj, "parameter")
        self.long_name   = None
        self.dimension   = None
        self.axis        = None
        self.zones       = None
        self.values      = None

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "LONG-NAME" : self.long_name = attr.value[0]
            if attr.label == "DIMENSION" : self.dimension = attr.value
            if attr.label == "AXIS"      : self.axis      = attr.value
            if attr.label == "ZONES"     : self.zones     = attr.value

        self.stripspaces()
