from collections import defaultdict, OrderedDict
from io import StringIO
import logging
import numpy as np
import re

from . import core
from . import plumbing

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

class dlis(object):
    types = {
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
        'SPLICE'                 : plumbing.Splice.create,
        'WELL-REFERENCE'         : plumbing.Wellref.create,
        'GROUP'                  : plumbing.Group.create,
        'PROCESS'                : plumbing.Process.create,
        'PATH'                   : plumbing.Path.create,
        'MESSAGE'                : plumbing.Message.create,
        'COMMENT'                : plumbing.Comment.create,
    }

    """dict: Parsing guide for native dlis object-types. Maps the native dlis
    object-type to python object-constructors. E.g. all dlis objects with type
    AXIS will be constructed into Axis objects. It is possible to both remove
    and add new object-types before loading or reloading a file. New objects
    will behave the same way as the defaulted object-types.

    If an object-type is not in types, it will be default parsed as an unknown
    object and accessible through the dlis.unknowns property.

    Examples
    --------

    Create a new object-type

    >>> from dlisio.plumbing.basicobject import BasicObject
    >>> from dlisio.plumbing.valuetypes import scalar, vector
    >>> from dlisio.plumbing.linkage import obname
    >>> class Channel440(BasicObject):
    ... attributes = {
    ...     'LONG-NAME' : scalar('longname'),
    ...     'SAMPLES'   : vector('samples')
    ... }
    ... linkage= { 'longname' : obname('LONG-NAME') }
    ... def __init__(self, obj = None, name = None):
    ...     super().__init_(obj, name = name, type = '440-CHANNEL')
    ...     self.longname = None
    ...     self.samples  = []

    Add the new object-type and load the file

    >>> dlisio.dlis.types['440-CHANNEL'] = Channel440.create
    >>> f = dlisio.load('filename')

    Access all objects off type 440-CHANNEL

    >>> channels440 = f.types['440-CHANNEL']

    Remove object-type CHANNEL. CHANNEL objects will no longer
    have a specialized parsing routine and will be parsed as Unknown objects

    >>> del dlisio.dlis.types['CHANNEL']
    >>> f = dlisio.load('filename')

    See also
    --------

    plumbing.BasicObject.attributes : attributes
    plumbing.BasicObject.linkage    : linkage
    """
    def __init__(self, stream, explicits, attic, implicits, sul_offset = 80):
        self.file = stream
        self.explicit_indices = explicits
        self.attic = attic
        self.sul_offset = sul_offset
        self.fdata_index = implicits

        self.objects = {}
        self.indexedobjects = defaultdict(dict)
        self.problematic = []

        self.load()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.file.close()

    def __repr__(self):
        try:
            fh = list(self.fileheader)[0]
            desc = fh.id
        except IndexError:
            desc = 'Unknown'
        return 'dlis({})'.format(desc)

    def describe(self, width=80, indent=''):
        buf = StringIO()
        plumbing.describe_header(buf, 'Logical File', width, indent)

        d = OrderedDict()
        d['Description']  = repr(self)
        d['Frames']       = len(self.frames)
        d['Channels']     = len(self.channels)
        d['Object count'] = len(self.objects)
        plumbing.describe_dict(buf, d, width, indent)

        known, unknown = {}, {}
        for objtype, val in self.indexedobjects.items():
            if objtype in self.types:
                known[objtype] = len(val)
            else:
                unknown[objtype] = len(val)

        if known:
            plumbing.describe_header(buf, 'Known objects', width, indent, lvl=2)
            plumbing.describe_dict(buf, known, width, indent)

        if unknown:
            plumbing.describe_header(buf, 'Unknown objects', width, indent, lvl=2)
            plumbing.describe_dict(buf, unknown, width, indent)

        return plumbing.Summary(info=buf.getvalue())

    def storage_label(self):
        blob = self.file.get(bytearray(80), self.sul_offset, 80)
        return core.storage_label(blob)

    def raw_objectsets(self, reload = False):
        if self.attic is None:
            self.attic = self.file.extract(self.explicit_indices)

        return core.parse_objects(self.attic)

    def match(self, pattern, type=None):
        """ Filter channels by mnemonics

        Returns all channel with mnemonics matching a regex [1]. By default the
        targeted object-set only includes native rp66 CHANNEL objects. This
        target set can be extended with the type parameter

        [1] https://docs.python.org/3.7/library/re.html


        Parameters
        ----------

        pattern : str
            Regex to match channel mnemonics against

        type : str
            Extend the targeted object-set to include all objects that have a
            type matching the inputed regex. Must be a valid regex

        Returns
        -------

        channels : generator of channels/objects

        Notes
        -----

        Some common regex characters:

        ====== =======================
        Regex  Description
        ====== =======================
        '.'    Any character
        '^'    Starts with
        '$'    Ends with
        '*'    Zero or more occurances
        '+'    One or more occurances
        '|'    Either or
        '[]'   Set of characters
        ====== =======================

        Examples
        -------

        Return all channels which have mnemonics matching 'AIBK':

        >>> channels = f.match('AIBK')

        Return all objects which have mnemonics matching the regex
        'AIBK', targeting all object-types starting with 'CHANNEL':

        >>> channels = f.match('AIBK', type='^CHANNEL')

        Return all CHANNEL objects where the mnemonic matches 'AI':

        >>> channels = f.match('AI.*')

        """
        def compileregex(pattern):
            try:
                return re.compile(pattern)
            except:
                msg = 'Invalid regex: {}'.format(pattern)
                raise ValueError(msg)

        objs = {}
        if type is None:
            objs = self.indexedobjects['CHANNEL']
        else:
            ctype = compileregex(type)
            for key, value in self.indexedobjects.items():
                if not re.match(ctype, key): continue
                objs.update(value)

        cpattern = compileregex(pattern)
        for obj in objs.values():
            if not re.match(cpattern, obj.name): continue
            yield obj

    def load(self, sets=None):
        """ Load and enrich raw objects into the object pool

        This method converts the raw object sets into first-class dlisio python
        objects, and puts them in the the objects, indexedobjects and problematic
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
        indexedobjects = defaultdict(dict)
        problematic = []

        if sets is None:
            sets = self.raw_objectsets()

        for os in sets:
            # TODO: handle replacement sets
            for name, o in os.objects.items():
                try:
                    obj = self.types[os.type](o, name = name, file = self)
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
                indexedobjects[obj.type][fingerprint] = obj

        for obj in objects.values():
            obj.link(objects)

        self.objects = objects
        self.indexedobjects = indexedobjects
        self.problematic = problematic
        return self

    @property
    def fileheader(self):
        """ Read all Fileheader objects

        Returns
        -------
        fileheader : dict_values

        """
        return self.indexedobjects['FILE-HEADER'].values()

    @property
    def origin(self):
        """ Read all Origin objects

        Returns
        -------
        origin : dict_values
        """
        return self.indexedobjects['ORIGIN'].values()

    @property
    def axes(self):
        """ Read all Axis objects

        Returns
        -------
        axes: dict_values
        """
        return self.indexedobjects['AXIS'].values()

    @property
    def longnames(self):
        """ Read all Longname objects

        Returns
        -------
        long-name : dict_values
        """
        return self.indexedobjects['LONG-NAME'].values()

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
        return self.indexedobjects['CHANNEL'].values()

    @property
    def frames(self):
        """ Read all Frame objects

        Returns
        -------
        frames: dict_values
        """
        return self.indexedobjects['FRAME'].values()

    @property
    def tools(self):
        """ Read all Tool objects

        Returns
        -------
        tools: dict_values
        """
        return self.indexedobjects['TOOL'].values()

    @property
    def zones(self):
        """ Read all Zone objects

        Returns
        -------
        zones: dict_values
        """
        return self.indexedobjects['ZONE'].values()

    @property
    def parameters(self):
        """ Read all Parameter objects

        Returns
        -------
        parameters: dict_values
        """
        return self.indexedobjects['PARAMETER'].values()

    @property
    def process(self):
        """ Read all Process objects

        Returns
        -------

        processes : dict_values
        """
        return self.indexedobjects['PROCESS'].values()

    @property
    def group(self):
        """ Read all Group objects

        Returns
        -------

        groups : dict_values
        """
        return self.indexedobjects['GROUP'].values()

    @property
    def wellref(self):
        """ Read all Wellref objects

        Returns
        -------

        wellrefs : dict_values
        """
        return self.indexedobjects['WELL-REFERENCE'].values()

    @property
    def splice(self):
        """ Read all Splice objects

        Returns
        -------

        splice : dict_values
        """
        return self.indexedobjects['SPLICE'].values()

    @property
    def path(self):
        """ Read all Path objects

        Returns
        -------

        path : dict_values
        """
        return self.indexedobjects['PATH'].values()

    @property
    def equipments(self):
        """ Read all Equipment objects

        Returns
        -------
        equipments : dict_values
        """
        return self.indexedobjects['EQUIPMENT'].values()

    @property
    def computations(self):
        """ Read all computation objects

        Returns
        -------
        computations : dict_values
        """
        return self.indexedobjects['COMPUTATION'].values()

    @property
    def measurements(self):
        """ Read all Measurement objects

        Returns
        -------
        measurement : dict_values
        """
        return self.indexedobjects['CALIBRATION-MEASUREMENT'].values()

    @property
    def coefficients(self):
        """ Read all Coefficient objects

        Returns
        -------
        coefficient : dict_values
        """
        return self.indexedobjects['CALIBRATION-COEFFICIENT'].values()

    @property
    def calibrations(self):
        """ Read all Calibration objects

        Returns
        -------
        calibrations : dict_values
        """
        return self.indexedobjects['CALIBRATION'].values()

    @property
    def comments(self):
        """ Read all Comment objects

        Returns
        -------
        comment : dict_values

        """
        return self.indexedobjects['COMMENT'].values()

    @property
    def messages(self):
        """ Read all Message objects

        Returns
        -------
        meassage : dict_values

        """
        return self.indexedobjects['MESSAGE'].values()

    @property
    def unknowns(self):
        return (obj
            for typename, object_set in self.indexedobjects.items()
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

    def __repr__(self):
        return 'Batch(logical files: {})'.format(len(self))

    def describe(self, width=80, indent=''):
        buf = StringIO()
        plumbing.describe_header(buf, 'Batch of Logical Files', width, indent)

        d = {'Number of Logical Files' : len(self)}
        plumbing.describe_dict(buf, d, width, indent)

        for f in self:
            d = OrderedDict()
            d['Description'] = repr(f)
            d['Frames']   = len(f.frames)
            d['Channels'] = len(f.channels)
            plumbing.describe_dict(buf, d, width, indent)

        return plumbing.Summary(info=buf.getvalue())


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
