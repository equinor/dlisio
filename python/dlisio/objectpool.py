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

def fingerprint(obj, type = None):
    if type is None:
        type = obj.type.upper()

    try:
        name = obj.name
    except AttributeError:
        name = obj

    return (type, name.id, name.origin, name.copynumber)

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

        cache = defaultdict(list)

        for os in objects:
            for obj in os.objects:
                 if   os.type == "FILE-HEADER" : obj = Fileheader(obj)
                 elif os.type == "ORIGIN"      : obj = Origin(obj)
                 elif os.type == "FRAME"       : obj = Frame(obj)
                 elif os.type == "CHANNEL"     : obj = Channel(obj)
                 elif os.type == "TOOL"        : obj = Tool(obj)
                 elif os.type == "PARAMETER"   : obj = Parameter(obj)
                 elif os.type == "CALIBRATION" : obj = Calibration(obj)
                 else: obj = Unknown(obj)

                 cache[fingerprint(obj)] = obj
                 cache[obj.type].append(obj)
                 self.objects.append(obj)

        for obj in self.objects:
            self.link(obj, cache)

    def __len__(self):
        """x.__len__() <==> len(x)"""
        return len(self.objects)

    def __repr__(self):
        return "Objectpool(objects =  {})".format(len(self))

    def link(self, obj, cache):
        if obj.type == "channel":
            if obj.source is not None:
                obj._source = cache[fingerprint(obj.source)]

        if obj.type == "frame":
            obj._channels = [
                cache[fingerprint(channel, type = 'CHANNEL')]
                for channel in obj._channels
            ]

        if obj.type == "tool":
            obj._channels = [
                cache[fingerprint(channel, type = 'CHANNEL')]
                for channel in obj._channels
            ]

            obj._parameters = [
                cache[fingerprint(channel, type = 'PARAMETER')]
                for channel in obj._parameters
            ]

        if obj.type == "calibration":
            obj._uncalibrated_channel = [
                cache[fingerprint(channel, type = 'CHANNEL')]
                for channel in obj._uncalibrated_channel
            ]

            obj._calibrated_channel = [
                cache[fingerprint(channel, type = 'CHANNEL')]
                for channel in obj._calibrated_channel
            ]

            obj._parameters = [
                cache[fingerprint(channel, type = 'PARAMETER')]
                for channel in obj._parameters
            ]

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
        return (o for o in self.objects if o.type == "fileheader")

    @property
    def origin(self):
        """Origin objects"""
        return (o for o in self.objects if o.type == "origin")

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
