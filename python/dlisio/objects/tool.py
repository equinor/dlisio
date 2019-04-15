import logging

from .basicobject import BasicObject

class Tool(BasicObject):
    """Tool

    A tool is an ensembly of equiptment that as a whole provide measurements or
    services. The list of equiptment that makes up the tool can be found in
    *tool.parts*. Tools objects also keep a list of all channels that where produced by
    the tool in *tool.channels*.

    Notes
    -----

    The tool object reflects the logical record type TOOL defined in rp66. TOOL
    objects are listed in Appendix A.2 - Logical Record Types, described in
    detail in Chapter 5.8.4 - Static and Frame Data, TOOL objects.

    See also
    --------

    dlisio.Channel : Channel objects.
    dlisio.Parameter : Parameter objects.
    """
    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'TOOL')
        #: Textual description of the tool
        self.description     = None

        #: The producer's name for the tool
        self.trademark_name  = None

        #: The name generally used by the industry to describe such a tool
        self.generic_name    = None

        #: If the tool is enabled to provide information to the acquisition
        #: system
        self.status          = None

        #: The equipment that makes up the tool
        self.parts           = []

        #: Channels that are produced by this tool
        self.channels        = []

        #: Parameter that directly affect or reflect the operation of the tool
        self.parameters      = []

        #: References to the channels
        self.channels_refs   = []

        #: References to the parameters
        self.parameters_refs = []

    @staticmethod
    def load(obj, name = None):
        self = Tool(obj, name = name)
        for label, value in obj.items():
            if value is None: continue

            if label == "DESCRIPTION"    : self.description    = value[0]
            if label == "TRADEMARK-NAME" : self.trademark_name = value[0]
            if label == "GENERIC-NAME"   : self.generic_name   = value[0]
            if label == "STATUS"         : self.status         = value[0]
            if label == "PARTS"          : self.parts          = value
            if label == "CHANNELS"       : self.channels_refs   = value
            if label == "PARAMETERS"     : self.parameters_refs = value

        self.stripspaces()
        return self

    def link(self, objects, sets):
        channels = sets['CHANNEL']
        chans = []
        for ref in self.channels_refs:
            fp = ref.fingerprint('CHANNEL')
            try:
                chans.append(channels[fp])
            except KeyError:
                msg = 'missing channel {} referenced from tool {}'
                logging.warning(msg.format(ref, self.name))

        parameters = sets['PARAMETER']
        params = []
        for ref in self.parameters_refs:
            fp = ref.fingerprint('PARAMETER')
            try:
                params.append(parameters[fp])
            except KeyError:
                msg = 'missing parameter {} referenced from tool {}'
                logging.warning(msg.format(ref, self.name))

        self.channels = chans
        self.parameters = params
