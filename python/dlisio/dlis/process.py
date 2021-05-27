from collections import OrderedDict

from .basicobject import BasicObject
from . import utils


class Process(BasicObject):
    """
    Process objects describes a specific process or computation applied to input
    objects to get output objects.

    Attributes
    ----------

    description : str

        RP66V1 name: *DESCRIPTION*

    trademark_name  : str
        Trademark name refers to the process and its products.

        RP66V1 name: *TRADEMARK-NAME*

    version : str
        Software version.

        RP66V1 name: *VERSION*

    properties : list(str)
        Properties that applies to the output of the process, as a result of
        the process.

        RP66V1 name: *PROPERTIES*

    status : str
        Indicated the status of the process. It's typically updated to indicate
        when the process is completed or aborted.

        RP66V1 name: *STATUS*

    input_channels : list(Channel)
        Channels that are used directly by this Process.

        RP66V1 name: *INPUT-CHANNELS*

    output_channels : list(Channel)
        Channels that are produced directly by this Process.

        RP66V1 name: *OUTPUT-CHANNELS*

    input_computations : list(Computation)
        Computations that are used directly by this Process.

        RP66V1 name: *INPUT-COMPUTATIONS*

    output_computations : list(Computation)
        Computations that are produced directly by this Process.

        RP66V1 name: *OUTPUT-COMPUTATIONS*

    parameters : list(Parameter)
        Parameters that are used by the Process or that directly affect the
        operation of the Process.

        RP66V1 name: *PARAMETERS*

    comments : list(str)
        Comments contains information specific to the particular
        execution of the process.

        RP66V1 name: *COMMENTS*

    See also
    --------

    BasicObject : The basic object that Parameter is derived from


    Notes
    -----

    The Process object reflects the logical record type Process, defined in
    rp66. PROCESS records are listed in Appendix A.2 - Logical Record Types and
    described in detail in Chapter 5.8.5 - Static and Frame Data, Process
    objects.
    """
    attributes = {
        'DESCRIPTION'         : utils.scalar,
        'TRADEMARK-NAME'      : utils.scalar,
        'VERSION'             : utils.scalar,
        'PROPERTIES'          : utils.vector,
        'STATUS'              : utils.scalar,
        'INPUT-CHANNELS'      : utils.vector,
        'OUTPUT-CHANNELS'     : utils.vector,
        'INPUT-COMPUTATIONS'  : utils.vector,
        'OUTPUT-COMPUTATIONS' : utils.vector,
        'PARAMETERS'          : utils.vector,
        'COMMENTS'            : utils.vector,
    }

    linkage = {
        'DESCRIPTION'         : utils.obname('LONG-NAME'),
        'INPUT-CHANNELS'      : utils.obname('CHANNEL'),
        'OUTPUT-CHANNELS'     : utils.obname('CHANNEL'),
        'INPUT-COMPUTATIONS'  : utils.obname('COMPUTATION'),
        'OUTPUT-COMPUTATIONS' : utils.obname('COMPUTATION'),
        'PARAMETERS'          : utils.obname('PARAMETER')
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
    def version(self):
        return self['VERSION']

    @property
    def properties(self):
        return self['PROPERTIES']

    @property
    def status(self):
        return self['STATUS']

    @property
    def input_channels(self):
        return self['INPUT-CHANNELS']

    @property
    def output_channels(self):
        return self['OUTPUT-CHANNELS']

    @property
    def input_computations(self):
        return self['INPUT-COMPUTATIONS']

    @property
    def output_computations(self):
        return self['OUTPUT-COMPUTATIONS']

    @property
    def parameters(self):
        return self['PARAMETERS']

    @property
    def comments(self):
        return self['COMMENTS']

    def describe_attr(self, buf, width, indent, exclude):
        utils.describe_description(buf, self.description, width, indent, exclude)

        d = OrderedDict()
        d['Trademark name'] = self.trademark_name
        d['Status']         = self.status
        d['Version']        = self.version
        d['Comments']       = self.comments
        utils.describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Properties']  = self.properties
        d['Parameters']  = utils.replist(self.parameters, 'name')
        utils.describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Input Channels']      = utils.replist(self.input_channels, 'name')
        d['Output Channels']     = utils.replist(self.output_channels, 'name')
        d['Input Computations']  = utils.replist(self.input_computations, 'name')
        d['Output computations'] = utils.replist(self.output_computations, 'name')
        utils.describe_dict(buf, d, width, indent, exclude)
