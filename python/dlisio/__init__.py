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
    def __init__(self, stream, explicits, attic, implicits, sul_offset = 80):
        self.file = stream
        self.explicit_indices = explicits
        self.attic = attic
        self.sul_offset = sul_offset
        self.fdata_index = implicits

        self.objects = {}
        self.object_sets = defaultdict(dict)
        self.problematic = []

        self.types = {
            'AXIS'                   : plumbing.Axis.create,
            'FILE-HEADER'            : plumbing.Fileheader.create,
            'ORIGIN'                 : plumbing.Origin.create,
            'LONG-NAME'              : plumbing.Longname.create,
            'FRAME'                  : plumbing.Frame.create,
            'CHANNEL'                : plumbing.Channel.create,
            'ZONE'                   : plumbing.Zone.create,
            'TOOL'                   : plumbing.Tool.create,
            'PARAMETER'              : plumbing.Parameter.create,
            'EQUIPMENT'              : plumbing.Equipment.create,
            'CALIBRATION-MEASUREMENT': plumbing.Measurement.create,
            'CALIBRATION-COEFFICIENT': plumbing.Coefficient.create,
            'CALIBRATION'            : plumbing.Calibration.create,
            'COMPUTATION'            : plumbing.Computation.create,
        }
        self.load()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        print("dlis: closed {}".format(self))
        self.close()

    def close(self):
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
            obj.link(objects)

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
    def axes(self):
        """ Read all Axis objects

        Returns
        -------
        axes: dict_values
        """
        return self.object_sets['AXIS'].values()

    @property
    def longnames(self):
        """ Read all Longname objects

        Returns
        -------
        long-name : dict_values
        """
        return self.object_sets['LONG-NAME'].values()

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
    def zones(self):
        """ Read all Zone objects

        Returns
        -------
        zones: dict_values
        """
        return self.object_sets['ZONE'].values()

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
    def computations(self):
        """ Read all computation objects

        Returns
        -------
        computations : dict_values
        """
        return self.object_sets['COMPUTATION'].values()

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
    """ Loads a file and returns one filehandle pr logical file.

    The dlis standard have a concept of logical files. A logical file is a
    group of related logical records, i.e. curves and metadata and is
    independent from any other logical file. Each physical file (.dlis) can
    contain 1 to n logical files. Layouts of physical- and logical files:

    Physical file::

         --------------------------------------------------------
        | Logical File 1 | Logical File 2 | ... | Logical File n |
         --------------------------------------------------------

    Logical File::

         ---------------------------------------------------------
        | Fileheader |  Origin  |  Frame  |  Channel  | curvedata |
         ---------------------------------------------------------

    This means that dlisio.load() will return 1 to n logical files.

    Parameters
    ----------

    path : str_like

    Examples
    --------

    Read the fileheader of each logical file

    >>> with dlisio.load(filename) as files:
    ...     for f in files:
    ...         header = f.fileheader

    Automatically unpack the first logical file and store the remaining logical
    files in tail

    >>> with dlisio.load(filename) as (f, *tail):
    ...     header = f.fileheader
    ...     for g in tail:
    ...         header = g.fileheader

    Notes
    -----

    1) That the parentezies are needed when unpacking directly in the with
    statment

    2) The asterisk allows an arbitrary number of extra logical files to be
    stored in tail. Use len(tail) to check how many extra logical files there
    is

    Returns
    -------

    dlis : tuple(dlisio.dlis)
    """
    path = str(path)

    mmap = core.mmap_source()
    mmap.map(path)

    sulpos = core.findsul(mmap)
    vrlpos = core.findvrl(mmap, sulpos + 80)

    tells, residuals, explicits = core.findoffsets(mmap, vrlpos)
    exi = [i for i, explicit in enumerate(explicits) if explicit != 0]

    try:
        stream = open(path)
        stream.reindex(tells, residuals)

        records = stream.extract(exi)
        stream.close()
    except:
        stream.close()
        raise

    split_at = find_fileheaders(records, exi)

    batch = []
    for part in partition(records, explicits, tells, residuals, split_at):
        try:
            stream = open(path)
            stream.reindex(part['tells'], part['residuals'])

            implicits = defaultdict(list)
            for key, val in core.findfdata(mmap,
                    part['implicits'], part['tells'], part['residuals']):
                implicits[key].append(val)

            f = dlis(stream, part['explicits'],
                    part['records'], implicits, sul_offset=sulpos)
            batch.append(f)
        except:
            stream.close()
            for stream in batch:
                stream.close()
            raise

    return Batch(batch)

class Batch(tuple):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        for f in self:
            f.close()

def find_fileheaders(records, exi):
    # Logical files start whenever a FILE-HEADER is encountered. When a logical
    # file spans multiple physical files, the FILE-HEADER is not repeated.
    # This means that the first record may not be a FILE-HEADER. In that case
    # dlisio still creates a logical file, but warns that this logical file
    # might be segmented, hence missing data.
    msg =  'First logical file does not contain a fileheader. '
    msg += 'The logical file might be segmented into multiple physical files '
    msg += 'and data can be missing.'

    pivots = []

    # There is only indirectly formated logical records in the physical file.
    # The logical file might be segmented.
    if not records:
        pivots.append(0)

    for i, rec in enumerate(records):
        # The first metadata record is not a file-header. The logical file
        # might be segmented.
        #TODO: This logic will change when support for multiple physical files
        # in a storage set is added
        if i == 0 and rec.type != 0:
            logging.warning(msg)
            pivots.append(exi[i])

        if rec.type == 0:
            pivots.append(exi[i])

    return pivots

def partition(records, explicits, tells, residuals, pivots):
    """
    Splits records, explicits, implicits, tells and residuals into
    partitions (Logical Files) based on the pivots

    Returns
    -------

    partitions : list(dict)
    """

    def split_at(lst, pivot):
        head = lst[:pivot]
        tail = lst[pivot:]
        return head, tail

    partitions = []

    for pivot in reversed(pivots):
        tells    , part_tells = split_at(tells, pivot)
        residuals, part_res   = split_at(residuals, pivot)
        explicits, part_ex    = split_at(explicits, pivot)

        part_ex   = [i for i, x in enumerate(part_ex) if x != 0]
        implicits = [x for x in range(len(part_tells)) if x not in part_ex]

        records, part_recs = split_at(records, -len(part_ex))

        part = {
            'records'   : part_recs,
            'explicits' : part_ex,
            'tells'     : part_tells,
            'residuals' : part_res,
            'implicits' : implicits
        }
        partitions.append(part)

    for par in reversed(partitions):
        yield par
