from .basic_object import basic_object


class Frame(basic_object):
    """
    The Frame object reflects the logical record type FRAME (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.7.1 - Static and
    Frame Data, FRAME objects)
    """
    def __init__(self, obj):
        super().__init__(obj, "frame")
        self.description = None
        self.channels    = []
        self.index_type  = None
        self.direction   = None
        self.spacing     = None
        self.encrypted   = None
        self.index_min   = None
        self.index_max   = None

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "DESCRIPTION": self.description = attr.value[0]
            if attr.label == "CHANNELS"   : self.channels    = attr.value
            if attr.label == "INDEX-TYPE" : self.index_type  = attr.value[0]
            if attr.label == "DIRECTION"  : self.direction   = attr.value[0]
            if attr.label == "SPACING"    : self.spacing     = attr.value[0]
            if attr.label == "ENCRYPTED"  : self.encrypted   = attr.value[0]
            if attr.label == "INDEX-MIN"  : self.index_min   = attr.value[0]
            if attr.label == "INDEX-MAX"  : self.index_max   = attr.value[0]

        self.stripspaces()

    def haschannel(self, channel):
        """
        Return True if channels is in frame.channels,
        else return False

        Parameters
        ----------
        channel : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        haschannel : bool
            True if Frame has the channel obj, else False

        """
        return self.contains(self.channels, channel)
