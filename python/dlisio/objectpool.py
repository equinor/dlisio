from collections import defaultdict

from . import core
from .fileheader import Fileheader
from .origin import Origin
from .frame import Frame
from .channel import Channel
from .tool import Tool
from .parameter import Parameter
from .calibration import Calibration
from .unknown import Unknown

class Objectpool():
    """ The Objectpool implements a pool of all metadata objects.

    Notes
    -----

    For now dlisio only support read operarations, hence any
    user-modification of these objects is NOT reflected on-disk
    """
    def __init__(self, objects):
        self.objects = []
        self.index = 0

        cache = defaultdict(dict)

        for os in objects:
            for obj in os.objects:
                 if   os.type == "FILE-HEADER" : obj = Fileheader.load(obj)
                 elif os.type == "ORIGIN"      : obj = Origin.load(obj)
                 elif os.type == "FRAME"       : obj = Frame.load(obj)
                 elif os.type == "CHANNEL"     : obj = Channel.load(obj)
                 elif os.type == "TOOL"        : obj = Tool.load(obj)
                 elif os.type == "PARAMETER"   : obj = Parameter.load(obj)
                 elif os.type == "CALIBRATION" : obj = Calibration.load(obj)
                 else: obj = Unknown.load(obj, type = os.type)

                 name = obj.name
                 iden = (name.id, name.origin, name.copynumber)
                 cache[obj.type][iden] = obj
                 cache[obj.fingerprint] = obj
                 self.objects.append(obj)

        for obj in self.objects:
            obj.link(cache)

    def __len__(self):
        """x.__len__() <==> len(x)"""
        return len(self.objects)

    def __repr__(self):
        return "Objectpool(objects =  {})".format(len(self))

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
    def fileheader(self):
        """Fileheader objects"""
        return (o for o in self.objects if o.type == "FILE-HEADER")

    @property
    def origin(self):
        """Origin objects"""
        return (o for o in self.objects if o.type == "ORIGIN")

    @property
    def channels(self):
        """Channel objects"""
        return (o for o in self.objects if o.type == "CHANNEL")

    @property
    def frames(self):
        """Frame objects"""
        return (o for o in self.objects if o.type == "FRAME")

    @property
    def tools(self):
        """Tool objects"""
        return (o for o in self.objects if o.type == "TOOL")

    @property
    def parameters(self):
        """Parameter objects"""
        return (o for o in self.objects if o.type == "PARAMETER")

    @property
    def calibrations(self):
        """Calibration objects"""
        return (o for o in self.objects if o.type == "CALIBRATION")

    @property
    def unknowns(self):
        """Frame objects"""
        return (o for o in self.objects if isinstance(o, Unknown))
