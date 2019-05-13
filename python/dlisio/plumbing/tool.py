from .basicobject import BasicObject
from .valuetypes import scalar, vector, boolean
from .linkage import obname

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
    attributes = {
        'DESCRIPTION'    : scalar('description'),
        'TRADEMARK-NAME' : scalar('trademark_name'),
        'GENERIC-NAME'   : scalar('generic_name'),
        'STATUS'         : boolean('status'),
        'PARTS'          : vector('parts'),
        'CHANNELS'       : vector('channels'),
        'PARAMETERS'     : vector('parameters')
    }

    linkage = {
        "parts"      : obname("EQUIPMENT"),
        "channels"   : obname("CHANNEL"),
        "parameters" : obname("PARAMETER"),
    }

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
