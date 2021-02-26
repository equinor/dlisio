from .basicobject import BasicObject
from .valuetypes import scalar, vector, boolean
from .linkage import obname
from .describe import describe_dict, replist

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
        'DESCRIPTION'    : scalar,
        'TRADEMARK-NAME' : scalar,
        'GENERIC-NAME'   : scalar,
        'STATUS'         : boolean,
        'PARTS'          : vector,
        'CHANNELS'       : vector,
        'PARAMETERS'     : vector,
    }

    linkage = {
        'PARTS'      : obname('EQUIPMENT'),
        'CHANNELS'   : obname('CHANNEL'),
        'PARAMETERS' : obname('PARAMETER'),
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def description(self):
        return self['DESCRIPTION']

    @property
    def trademark_name(self):
        return self['TRADEMARK-NAME']

    @property
    def generic_name(self):
        return self['GENERIC-NAME']

    @property
    def status(self):
        return self['STATUS']

    @property
    def parts(self):
        return self['PARTS']

    @property
    def channels(self):
        return self['CHANNELS']

    @property
    def parameters(self):
        return self['PARAMETERS']

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
