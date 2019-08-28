from .basicobject import BasicObject
from .valuetypes import scalar, vector, boolean
from .linkage import obname
from .utils import *

from collections import OrderedDict

class Tool(BasicObject):
    """
    A tool is an ensembly of equiptment that as a whole provide measurements or
    services. The list of equiptment that makes up the tool can be found in
    *tool.parts*. Tools objects also keep a list of all channels that where produced by
    the tool in *tool.channels*.

    Attributes
    ----------

    description : str
        Textual description of the tool

    trademark_name : str
        The producer's name for the tool

    generic_name : str
        The name generally used by the industry to describe such a tool

    status : bool
        If the tool is enabled to provide information to the acquisition system

    parts : list(Equipment)
        Equipments that makes up the tool

    channels : list(Channel)
        Channels that are produced by this tool

    parameters : list(Parameter)
        Parameters that directly affect or reflect the operation of the tool

    See also
    --------

    BasicObject : The basic object that Tool is derived from

    Notes
    -----

    The tool object reflects the logical record type TOOL defined in rp66. TOOL
    objects are listed in Appendix A.2 - Logical Record Types, described in
    detail in Chapter 5.8.4 - Static and Frame Data, TOOL objects.
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
        self.description     = None
        self.trademark_name  = None
        self.generic_name    = None
        self.status          = None
        self.parts           = []
        self.channels        = []
        self.parameters      = []

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Description']    = self.description
        d['Trademark name'] = self.trademark_name
        d['Generic name']   = self.generic_name
        d['Status']         = self.status

        describe_dict(buf, d, width, indent, exclude)

        channels = replist(self.channels, 'name')
        parameters = replist(self.parameters, 'name')
        parts = replist(self.parts, 'name')

        d = OrderedDict()
        d['Channels']   = channels
        d['Parameters'] = parameters
        d['Parts']      = parts

        describe_dict(buf, d, width, indent, exclude)
