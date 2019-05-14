from collections import defaultdict
import logging
import numpy as np

from . import core
from . import plumbing

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

class dlis(object):
    def __init__(self, stream, explicits, sul_offset = 80):
        self.file = stream
        self.explicit_indices = explicits
        self.attic = None
        self.sul_offset = sul_offset
        self.fdata_index = None

        self.objects = {}
        self.object_sets = defaultdict(dict)
        self.problematic = []

        self.types = {
            'FILE-HEADER'            : plumbing.Fileheader.create,
            'ORIGIN'                 : plumbing.Origin.create,
            'FRAME'                  : plumbing.Frame.create,
            'CHANNEL'                : plumbing.Channel.create,
            'TOOL'                   : plumbing.Tool.create,
            'PARAMETER'              : plumbing.Parameter.create,
            'EQUIPMENT'              : plumbing.Equipment.create,
            'CALIBRATION-MEASUREMENT': plumbing.Measurement.create,
            'CALIBRATION-COEFFICIENT': plumbing.Coefficient.create,
            'CALIBRATION'            : plumbing.Calibration.create,
        }
        self.load()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.file.close()

    def storage_label(self):
        blob = self.file.get(bytearray(80), self.sul_offset, 80)
        return core.storage_label(blob)

    def raw_objectsets(self, reload = False):
        if self.attic is None:
            self.attic = self.file.extract(self.explicit_indices)

        return core.parse_objects(self.attic)

    def load(self, sets=None):
        """ Load and enrich raw objects into the object pool

        This method converts the raw object sets into first-class dlisio python
        objects, and puts them in the the objects, object_sets and problematic
        members.

        Parameters
        ----------
        sets : iterable of object_set

        Notes
        -----
        This is a part of the two-phase initialisation of the pool, and should
        rarely be called as an end user. This is primarily a mechanism for
        testing and prototyping for developers, and the occasional
        live-patching of features so that dlisio is useful, even when something
        in particular is not merged upstream.

        """
        problem = 'multiple distinct objects '
        where = 'in set {} ({}). Duplicate fingerprint = {}'
        action = 'continuing with the last object'
        duplicate = 'duplicate fingerprint {}'

        objects = {}
        object_sets = defaultdict(dict)
        problematic = []

        if sets is None:
            sets = self.raw_objectsets()

        for os in sets:
            # TODO: handle replacement sets
            for name, o in os.objects.items():
                try:
                    obj = self.types[os.type](o, name = name)
                except KeyError:
                    obj = plumbing.Unknown.create(o, name = name, type = os.type)

                fingerprint = obj.fingerprint
                if fingerprint in objects:
                    original = objects[fingerprint]

                    logging.info(duplicate.format(fingerprint))
                    if original.attic != obj.attic:
                        msg = problem + where
                        msg = msg.format(os.type, os.name, fingerprint)
                        logging.error(msg)
                        logging.warning(action)
                        problematic.append((original, obj))

                objects[fingerprint] = obj
                object_sets[obj.type][fingerprint] = obj

        for obj in objects.values():
            obj.link(objects, object_sets)

        self.objects = objects
        self.object_sets = object_sets
        self.problematic = problematic
        return self

    def getobject(self, name, type):
        return self._objects.getobject(name, type)

    def curves(self, fingerprint):
        frame = self.object_sets['FRAME'][fingerprint]
        fmt = frame.fmtstr()
        indices = self.fdata_index[fingerprint]
        a = np.empty(shape = len(indices), dtype = frame.dtype)
        core.read_all_fdata(fmt, self.file, indices, a)
        return a

    @property
    def fileheader(self):
        """ Read all Fileheader objects

        Returns
        -------
        fileheader : dict_values

        """
        return self.object_sets['FILE-HEADER'].values()

    @property
    def origin(self):
        """ Read all Origin objects

        Returns
        -------
        origin : dict_values
        """
        return self.object_sets['ORIGIN'].values()

    @property
    def channels(self):
        """ Read all channel objects

        Returns
        -------
        channel : dict_values

        Examples
        --------
        Print all Channel names

        >>> for channel in f.channels:
        ...     print(channel.name)
        """
        return self.object_sets['CHANNEL'].values()

    @property
    def frames(self):
        """ Read all Frame objects

        Returns
        -------
        frames: dict_values
        """
        return self.object_sets['FRAME'].values()

    @property
    def tools(self):
        """ Read all Tool objects

        Returns
        -------
        tools: dict_values
        """
        return self.object_sets['TOOL'].values()

    @property
    def parameters(self):
        """ Read all Parameter objects

        Returns
        -------
        parameters: dict_values
        """
        return self.object_sets['PARAMETER'].values()

    @property
    def equipments(self):
        """ Read all Equipment objects

        Returns
        -------
        equipments : dict_values
        """
        return self.object_sets['EQUIPMENT'].values()

    @property
    def measurements(self):
        """ Read all Measurement objects

        Returns
        -------
        measurement : dict_values
        """
        return self.object_sets['CALIBRATION-MEASUREMENT'].values()

    @property
    def coefficients(self):
        """ Read all Coefficient objects

        Returns
        -------
        coefficient : dict_values
        """
        return self.object_sets['CALIBRATION-COEFFICIENT'].values()

    @property
    def calibrations(self):
        """ Read all Calibration objects

        Returns
        -------
        calibrations : dict_values
        """
        return self.object_sets['CALIBRATION'].values()

    @property
    def unknowns(self):
        return (obj
            for typename, object_set in self.object_sets.items()
            for obj in object_set.values()
            if typename not in self.types
        )

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
        index = defaultdict(list)
        for key, val in core.findfdata(mmap, candidates, tells, residuals):
            index[key].append(val)

        f.fdata_index = index
    except:
        stream.close()
        raise

    return f
