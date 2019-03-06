from .basic_object import basic_object


class Frame(basic_object):
    """
    The Frame object reflects the logical record type FRAME (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.7.1 - Static and
    Frame Data, FRAME objects)
    """
    def __init__(self, obj):
        super().__init__(obj, "frame")
        self._description = None
        self._channels    = []
        self._index_type  = None
        self._direction   = None
        self._spacing     = None
        self._encrypted   = None
        self._index_min   = None
        self._index_max   = None

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "DESCRIPTION": self._description = attr.value[0]
            if attr.label == "CHANNELS"   : self._channels    = attr.value
            if attr.label == "INDEX-TYPE" : self._index_type  = attr.value[0]
            if attr.label == "DIRECTION"  : self._direction   = attr.value[0]
            if attr.label == "SPACING"    : self._spacing     = attr.value[0]
            if attr.label == "ENCRYPTED"  : self._encrypted   = attr.value[0]
            if attr.label == "INDEX-MIN"  : self._index_min   = attr.value[0]
            if attr.label == "INDEX-MAX"  : self._index_max   = attr.value[0]

        self.stripspaces()

    @property
    def description(self):
        return self._description

    @property
    def channels(self):
        return self._channels

    @property
    def index_type(self):
        return self._index_type

    @property
    def direction(self):
        return self._direction

    @property
    def spacing(self):
        return self._spacing

    @property
    def encrypted(self):
        return self._encrypted

    @property
    def index_min(self):
        return self._index_min

    @property
    def index_max(self):
        return self._index_max

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
