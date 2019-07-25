from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .linkage import obname


class Process(BasicObject):
    """
    Process objects describes a specific process or computation applied to input
    objects to get output objects.

    Attributes
    ----------

    description : str

    trademark_name  : str
        Trademark name refers to the process and its products.

    version : str
        Software version.

    properties : list of str
        Properties that applies to the output of the process, as a result of
        the process.

    status : str
        Indicated the status of the process. It's typically updated to indicate
        when the process is completed or aborted.

    input_channels : list of Channel
        Channels that are used directly by this Process.

    output_channels : list of Channel
        Channels that are produced directly by this Process.

    input_computation : list of Computation
        Computations that are used directly by this Process.

    output_computation : list of Computation
        Computations that are produced directly by this Process.

    parameters : list of Parameter
        Parameters that are used by the Process or that directly affect the
        operation of the Process.

    comments : list of str
        Comments contains information specific to the particular
        execution of the process.

    Notes
    -----

    The Process object reflects the logical record type Process, defined in
    rp66. PROCESS records are listed in Appendix A.2 - Logical Record Types and
    described in detail in Chapter 5.8.5 - Static and Frame Data, Process
    objects.
    """
    attributes = {
        'DESCRIPTION'         : scalar('description'),
        'TRADEMARK-NAME'      : scalar('trademark_name'),
        'VERSION'             : scalar('version'),
        'PROPERTIES'          : vector('properties'),
        'STATUS'              : scalar('status'),
        'INPUT-CHANNELS'      : vector('input_channels'),
        'OUTPUT-CHANNELS'     : vector('output_channels'),
        'INPUT-COMPUTATIONS'  : vector('input_computations'),
        'OUTPUT-COMPUTATIONS' : vector('output_computations'),
        'PARAMETERS'          : vector('parameters'),
        'COMMENTS'            : vector('comments')
    }

    linkage = {
        'description'         : obname('LONG-NAME'),
        'input_channels'      : obname('CHANNEL'),
        'output_channels'     : obname('CHANNEL'),
        'input_computations'  : obname('COMPUTATION'),
        'output_computations' : obname('COMPUTATION'),
        'parameters'          : obname('PARAMETER')
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'PROCESS')
        self.description         = None
        self.trademark_name      = None
        self.version             = None
        self.properties          = []
        self.status              = None
        self.input_channels      = []
        self.output_channels     = []
        self.input_computations  = []
        self.output_computations = []
        self.parameters          = []
        self.comments            = []
