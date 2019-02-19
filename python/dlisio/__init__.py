import numpy as np
from . import core
from .objects import Objectpool

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

class dlis(object):
    def __init__(self, stream, explicits):
        self.file = stream
        self.explicit_indices = explicits
        self.object_sets = None
        self._objects = Objectpool(self.objectsets())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.file.close()

    def storage_label(self):
        blob = self.file.get(bytearray(80), 0, 80)
        return core.storage_label(blob)

    def objectsets(self, reload = False):
        if self.object_sets is None:
            self.object_sets = self.file.extract(self.explicit_indices)

        return core.parse_objects(self.object_sets)

    def getobject(self, name, type):
        return self._objects.getobject(name, type)

    @property
    def objects(self):
        return self._objects.allobjects

    @property
    def channels(self):
        """ Read all channel metadata objects

        Returns
        -------
        channels: generator of Channel objects

        Examples
        --------
        Print all Channel names

        >>> for channel in f.channels:
        ...     print(channel.name)

        Filter channels on name.id
        >>> x = [ch for ch in f.channels if ch.name.id == "name"]

        """
        return self._objects.channels

    @property
    def frames(self):
        """ Read all Frame metadata objects

        Returns
        -------
        frames: generator of Frame objects

        Examples
        --------
        Print all Frame names

        >>> for frame in f.frames:
        ...     print(frame.name)

        Check if a channel, ch,  is a part of Frame:
        >>> if frame.haschannel(ch):
        ...     pass

        """
        return self._objects.frames

    @property
    def unknowns(self):
        return self._objects.unknowns

def open(path):
    tells, residuals, explicits = core.findoffsets(path)
    explicits = [i for i, explicit in enumerate(explicits) if explicit != 0]

    stream = core.stream(path)

    try:
        stream.reindex(tells, residuals)
        f = dlis(stream, explicits)
    except:
        stream.close()
        raise

    return f
