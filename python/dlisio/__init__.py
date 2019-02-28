import numpy as np
from . import core
from .objects import Objectpool

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

class dlis(object):
    def __init__(self, stream, explicits, sul_offset = 80):
        self.file = stream
        self.explicit_indices = explicits
        self.object_sets = None
        self._objects = Objectpool(self.objectsets())
        self.sul_offset = sul_offset

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.file.close()

    def storage_label(self):
        blob = self.file.get(bytearray(80), self.sul_offset, 80)
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
    def tools(self):
        """ Read all Tool metadata objects

        Returns
        -------
        tools: generator of Tool objects
        """
        return self._objects.tools

    @property
    def parameters(self):
        """ Read all Parameter metadata objects

        Returns
        -------
        parameters: generator of Parameter objects
        """
        return self._objects.parameters

    @property
    def calibrations(self):
        """ Read all Calibration objects

        Returns
        -------
        calibrations: generator of Calibration objects
        """
        return self._objects.calibrations

    @property
    def unknowns(self):
        return self._objects.unknowns

def open(path):
    """ Open a file

    Open a low-level file handle. This is not intended for end-users - rather,
    it's an escape hatch for very broken files that dlisio cannot handle.

    Parameters
    ----------
    path : str_like

    Returns
    -------
    stream : dlisio.core.stream

    See Also
    --------
    dlisio.load
    """
    return core.stream(str(path))

def load(path):
    """ Load a file

    Parameters
    ----------
    path : str_like

    Returns
    -------
    dlis : dlisio.dlis
    """
    path = str(path)

    mmap = core.mmap_source()
    mmap.map(path)

    sulpos = core.findsul(mmap)
    vrlpos = core.findvrl(mmap, sulpos + 80)

    tells, residuals, explicits = core.findoffsets(mmap, vrlpos)
    explicits = [i for i, explicit in enumerate(explicits) if explicit != 0]

    stream = open(path)

    try:
        stream.reindex(tells, residuals)
        f = dlis(stream, explicits, sul_offset = sulpos)
    except:
        stream.close()
        raise

    return f
