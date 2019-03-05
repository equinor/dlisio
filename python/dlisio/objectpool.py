from . import core
from .frame import Frame
from .channel import Channel
from .tool import Tool
from .parameter import Parameter
from .calibration import Calibration
from .unknown import Unknown


class Objectpool():
    """ The Objectpool implements a pool of all metadata objects.

    Linking objects:
    Some objects have attributes that reference other object of different
    classes e.g. frames have a channels attribute. The on-disk representation
    of these attributes are meerly list of unique object names. dlisio resolves
    these object names an creates refrences to the python objects. However,
    dlisio assumes that there exist an object with that unique name on file.
    If not, that entry is silently dropped from the refrencing object
    attribute.

    Note that the attic attribute contains all object attributes as represented
    on disk. Dropped entries can be identified by simply comparing the the
    attribute from the python object with the corresponding attribute in attic

    Also note that for now dlisio only support read operarations, hence any
    user-modification of these objects is NOT reflected on-disk
    """
    def __init__(self, objects):
        self.objects = []
        self.index = 0

        for os in objects:
            for obj in os.objects:
                 if   os.type == "FRAME"       : obj = Frame(obj)
                 elif os.type == "CHANNEL"     : obj = Channel(obj)
                 elif os.type == "TOOL"        : obj = Tool(obj)
                 elif os.type == "PARAMETER"   : obj = Parameter(obj)
                 elif os.type == "CALIBRATION" : obj = Calibration(obj)
                 else: obj = Unknown(obj)
                 self.objects.append(obj)

        for obj in self.objects:
            self.link(obj)

    def __len__(self):
        """x.__len__() <==> len(x)"""
        return len(self.objects)

    def __repr__(self):
        return "Objectpool(objects =  {})".format(len(self))

    def link(self, obj):
        if obj.type == "channel":
            if obj.source is not None:
                for o in self.objects:
                    if o.name == obj.source.name: obj.source = o

        if obj.type == "frame":
            obj.channels = [o for o in self.channels if obj.haschannel(o.name)]

        if obj.type == "tool":
            obj.channels = [o for o in self.channels if obj.haschannel(o.name)]
            obj.parameters = [o for o in self.parameters if obj.hasparameter(o.name)]

        if obj.type == "calibration":
            obj.uncal_ch = [o for o in self.channels if obj.hasuncalibrated_channel(o.name)]
            obj.cal_ch = [o for o in self.channels if obj.hascalibrated_channel(o.name)]
            obj.parameters = [o for o in self.parameters if obj.hasparameter(o.name)]

    def getobject(self, name, type):
        """ return object corresponding to the unique identifier given by name + type

        Parameters
        ----------
        name : tuple(str, int, int) or dlisio.core.obname
        type : str

        Returns
        -------
        obj : object

        Examples
        --------

        >>> name = ("TDEP", 2, 2)
        >>> obj = objects[name, "channel"]
        """

        n = (None, None, None)
        if isinstance(name, tuple):
            n = name

        if isinstance(name, core.obname):
            n = (name.id, name.origin, name.copynumber)

        for o in self.objects:
            if o.type != type            : continue
            if o.name.id != n[0]         : continue
            if o.name.origin != n[1]     : continue
            if o.name.copynumber != n[2] : continue
            return o

    @property
    def allobjects(self):
        """
        Returns a generator of all objects on file
        """
        return (o for o in self.objects)

    @property
    def channels(self):
        """Channel objects"""
        return (o for o in self.objects if o.type == "channel")

    @property
    def frames(self):
        """Frame objects"""
        return (o for o in self.objects if o.type == "frame")

    @property
    def tools(self):
        """Tool objects"""
        return (o for o in self.objects if o.type == "tool")

    @property
    def parameters(self):
        """Parameter objects"""
        return (o for o in self.objects if o.type == "parameter")

    @property
    def calibrations(self):
        """Calibration objects"""
        return (o for o in self.objects if o.type == "calibration")

    @property
    def unknowns(self):
        """Frame objects"""
        return (o for o in self.objects if o.type == "unknown")
