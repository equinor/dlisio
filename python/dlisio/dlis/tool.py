from collections import OrderedDict

from .basicobject import BasicObject
from . import utils

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

        RP66V1 name: *DESCRIPTION*

    trademark_name : str
        The producer's name for the tool

        RP66V1 name: *TRADEMARK-NAME*

    generic_name : str
        The name generally used by the industry to describe such a tool

        RP66V1 name: *GENERIC-NAME*

    status : bool
        If the tool is enabled to provide information to the acquisition system

        RP66V1 name: *STATUS*

    parts : list(Equipment)
        Equipments that makes up the tool

        RP66V1 name: *PARTS*

    channels : list(Channel)
        Channels that are produced by this tool

        RP66V1 name: *CHANNELS*

    parameters : list(Parameter)
        Parameters that directly affect or reflect the operation of the tool

        RP66V1 name: *PARAMETERS*

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
        'DESCRIPTION'    : utils.scalar,
        'TRADEMARK-NAME' : utils.scalar,
        'GENERIC-NAME'   : utils.scalar,
        'STATUS'         : utils.boolean,
        'PARTS'          : utils.vector,
        'CHANNELS'       : utils.vector,
        'PARAMETERS'     : utils.vector,
    }

    linkage = {
        'PARTS'      : utils.obname('EQUIPMENT'),
        'CHANNELS'   : utils.obname('CHANNEL'),
        'PARAMETERS' : utils.obname('PARAMETER'),
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

        utils.describe_dict(buf, d, width, indent, exclude)

        channels = utils.replist(self.channels, 'name')
        parameters = utils.replist(self.parameters, 'name')
        parts = utils.replist(self.parts, 'name')

        d = OrderedDict()
        d['Channels']   = channels
        d['Parameters'] = parameters
        d['Parts']      = parts

        utils.describe_dict(buf, d, width, indent, exclude)
