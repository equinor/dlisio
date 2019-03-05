from .basic_object import basic_object


class Tool(basic_object):
    """
    The tool object reflects the logical record type TOOL (listed in Appendix
    A.2 - Logical Record Types, described in Chapter 5.8.4 - Static and Frame
    Data, TOOL objects)
    """
    def __init__(self, obj):
        super().__init__(obj, "tool")
        self.description    = None
        self.trademark_name = None
        self.generic_name   = None
        self.status         = None
        self.parts          = []
        self.channels       = []
        self.parameters     = []

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "DESCRIPTION"    : self.description    = attr.value[0]
            if attr.label == "TRADEMARK-NAME" : self.trademark_name = attr.value[0]
            if attr.label == "GENERIC-NAME"   : self.generic_name   = attr.value[0]
            if attr.label == "STATUS"         : self.status         = attr.value[0]
            if attr.label == "PARTS"          : self.parts          = attr.value
            if attr.label == "CHANNELS"       : self.channels       = attr.value
            if attr.label == "PARAMETERS"     : self.parameters     = attr.value

        self.stripspaces()

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
