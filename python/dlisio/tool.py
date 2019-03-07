from .basicobject import BasicObject


class Tool(BasicObject):
    """
    The tool object reflects the logical record type TOOL (listed in Appendix
    A.2 - Logical Record Types, described in Chapter 5.8.4 - Static and Frame
    Data, TOOL objects)
    """
    def __init__(self, obj):
        super().__init__(obj, "tool")
        self._description    = None
        self._trademark_name = None
        self._generic_name   = None
        self._status         = None
        self._parts          = []
        self._channels       = []
        self._parameters     = []

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "DESCRIPTION"    : self._description    = attr.value[0]
            if attr.label == "TRADEMARK-NAME" : self._trademark_name = attr.value[0]
            if attr.label == "GENERIC-NAME"   : self._generic_name   = attr.value[0]
            if attr.label == "STATUS"         : self._status         = attr.value[0]
            if attr.label == "PARTS"          : self._parts          = attr.value
            if attr.label == "CHANNELS"       : self._channels       = attr.value
            if attr.label == "PARAMETERS"     : self._parameters     = attr.value

        self.stripspaces()

    @property
    def description(self):
        return self._description

    @property
    def trademark_name(self):
        return self._trademark_name

    @property
    def generic_name(self):
        return self._generic_name

    @property
    def status(self):
        return self._status

    @property
    def parts(self):
        return self._parts

    @property
    def channels(self):
        return self._channels

    @property
    def parameters(self):
        return self._parameters

    def haschannel(self, channel):
        """
        Return True if channels is in tool.channels,
        else return False

        Parameters
        ----------
        channel : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        haschannel : bool
            True if Tool has the channel obj, else False

        """
        return self.contains(self.channels, channel)

    def hasparameter(self, param):
        """
        Return True if param is in tool.parameters,
        else return False

        Parameters
        ----------
        param : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        hasparam : bool
            True if Tool has the parameter obj, else False

        """
        return self.contains(self.parameters, param)
