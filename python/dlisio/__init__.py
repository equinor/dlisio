import collections
import numpy as np
from . import core
from .objectpool import Objectpool

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
        self._objects = Objectpool()
        self._objects.load(self.objectsets())
        self.sul_offset = sul_offset
        self.fdata_index = None

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

    def curves(self, fingerprint):
        frame = self._objects.object_sets['FRAME'][fingerprint]
        fmt = frame.fmtstr()
        indices = self.fdata_index[fingerprint]
        a = np.empty(shape = len(indices), dtype = frame.dtype)
        core.read_all_fdata(fmt, self.file, indices, a)
        return a

    @property
    def objects(self):
        return self._objects.allobjects

    @property
    def fileheader(self):
        """ Read all Fileheader objects

        Returns
        -------
        tools: generator of Fileheader objects
        """
        return self._objects.fileheader

    @property
    def origin(self):
        """ Read all Origin objects

        Returns
        -------
        tools: generator of Origin objects
        """
        return self._objects.origin

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

        explicits = set(explicits)
        candidates = [x for x in range(len(tells)) if x not in explicits]

        # TODO: formalise and improve the indexing of FDATA records
        index = collections.defaultdict(list)
        for key, val in core.findfdata(mmap, candidates, tells, residuals):
            index[key].append(val)

        f.fdata_index = index
    except:
        stream.close()
        raise

    return f
