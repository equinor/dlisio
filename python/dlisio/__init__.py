from collections import defaultdict, OrderedDict
from io import StringIO
import logging
import re

from . import core
from . import plumbing

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

class dlis(object):
    """Logical file

    A logical file is a collection of objects - in lack of a better word,
    that are logically connected in some way. Think of a logical file as a pool
    of objects. Some examples of objects are Channel, Frame, Fileheader, Tool.
    They are all accessible through their own attribute.

    :py:func:`object()` and :py:func:`match()` let you access specific objects
    or search for objects matching a regular expression. Unknown objects such
    as vendor-specific objects are accessible through the 'unknown'-attribute.

    Uniquely identifying an object within a logical file can be a bit
    cumbersome, and confusing.  It requires no less than 4 attributes!  Namely,
    the object's type, name, origin and copynumber.  The standard allows for
    two objects of the same type to have the same name, as long as either their
    origin or copynumber differ. E.g. there may exist two channels with the
    same name/mnemonic.

    Attributes
    ----------

    attic : dict
        Primitive dict-like representations of the objects. These objects are
        the output of the parsing routine of the core library. They are the
        foundation of which the more rich python objects are created from.
        They are considered to be an internal data structure, the typical user
        does not need to care about these.

    problematic : list
        Duplicated objects. If dlisio is not able to uniquely identify an object
        based on the standards definition, the object is flagged as
        problematic. Mainly indended for debugging files.

    indexedobject : dict
        A full inventory of all objects in the logical file, indexed by type.
        Note that there are more handy ways of accessing objects than through
        this dictionary.
    """
    types = {
        'AXIS'                   : plumbing.Axis,
        'FILE-HEADER'            : plumbing.Fileheader,
        'ORIGIN'                 : plumbing.Origin,
        'LONG-NAME'              : plumbing.Longname,
        'FRAME'                  : plumbing.Frame,
        'CHANNEL'                : plumbing.Channel,
        'ZONE'                   : plumbing.Zone,
        'TOOL'                   : plumbing.Tool,
        'PARAMETER'              : plumbing.Parameter,
        'EQUIPMENT'              : plumbing.Equipment,
        'CALIBRATION-MEASUREMENT': plumbing.Measurement,
        'CALIBRATION-COEFFICIENT': plumbing.Coefficient,
        'CALIBRATION'            : plumbing.Calibration,
        'COMPUTATION'            : plumbing.Computation,
        'SPLICE'                 : plumbing.Splice,
        'WELL-REFERENCE'         : plumbing.Wellref,
        'GROUP'                  : plumbing.Group,
        'PROCESS'                : plumbing.Process,
        'PATH'                   : plumbing.Path,
        'MESSAGE'                : plumbing.Message,
        'COMMENT'                : plumbing.Comment,
    }

    """dict: Parsing guide for native dlis object-types. The typical user can
    safely ignore this attribute. It is mainly intended for internal use and
    advanced customization of dlisio's parsing routine.

    Maps the native dlis object-type to python class. E.g. all dlis objects
    with type AXIS will be constructed into Axis objects. It is possible to
    both remove and add new object-types before loading or reloading a file.
    New objects will behave the same way as the defaulted object-types.

    If an object-type is not in types, it will be default parsed as an unknown
    object and accessible through the dlis.unknowns property.

    Examples
    --------

    Create a new object-type

    >>> from dlisio.plumbing.basicobject import BasicObject
    >>> from dlisio.plumbing.valuetypes import scalar, vector
    >>> from dlisio.plumbing.linkage import obname
    >>> class Channel440(BasicObject):
    ...   attributes = {
    ...     'LONG-NAME' : scalar('longname'),
    ...     'SAMPLES'   : vector('samples')
    ...   }
    ...   linkage= { 'longname' : obname('LONG-NAME') }
    ...   def __init__(self, obj = None, name = None):
    ...     super().__init_(obj, name = name, type = '440-CHANNEL')
    ...     self.longname = None
    ...     self.samples  = []

    Add the new object-type and load the file

    >>> dlisio.dlis.types['440-CHANNEL'] = Channel440
    >>> f = dlisio.load('filename')

    Remove object-type CHANNEL. CHANNEL objects will no longer
    have a specialized parsing routine and will be parsed as Unknown objects

    >>> del dlisio.dlis.types['CHANNEL']
    >>> f = dlisio.load('filename')

    See also
    --------

    plumbing.BasicObject.attributes : Attributes of an object can be customized
      in a similar manner as types.
    plumbing.BasicObject.linkage    :  Linkage tells dlisio how it should try
       to link the content of attributes to other objects.
    """

    def __init__(self, stream, explicits, attic, implicits, sul_offset = 80):
        self.file = stream
        self.explicit_indices = explicits
        self.attic = attic
        self.sul_offset = sul_offset
        self.fdata_index = implicits

        self.indexedobjects = defaultdict(dict)
        self.problematic = []

        self.load()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Close the file handle

        It is not necessary to call this method if you're using the `with`
        statement, which will close the file for you. Calling methods on a
        previously-closed file will raise `IOError`.
        """
        self.file.close()

    def __repr__(self):
        try:
            desc = self.fileheader.id
        except IndexError:
            desc = 'Unknown'
        return 'dlis({})'.format(desc)

    class IndexedObjectDescriptor:
        """ Return all objects of this type"""
        def __init__(self, t):
            self.t = t

        def __get__(self, instance, owner):
            return instance.indexedobjects[self.t].values()

    @property
    def fileheader(self):
        """ Return the Fileheader

        Returns
        -------
        fileheader : Fileheader

        """
        values = list(self.indexedobjects['FILE-HEADER'].values())

        if len(values) != 1:
            msg = "Expected exactly one fileheader. Was: {}"
            logging.warning(msg.format(values))
            if len(values) == 0:
                return None
        else:
            return values[0]

    axes         = IndexedObjectDescriptor("AXIS")
    calibrations = IndexedObjectDescriptor("CALIBRATION")
    channels     = IndexedObjectDescriptor("CHANNEL")
    coefficients = IndexedObjectDescriptor("CALIBRATION-COEFFICIENT")
    comments     = IndexedObjectDescriptor("COMMENT")
    computations = IndexedObjectDescriptor("COMPUTATION")
    equipments   = IndexedObjectDescriptor("EQUIPMENT")
    frames       = IndexedObjectDescriptor("FRAME")
    groups       = IndexedObjectDescriptor("GROUP")
    longnames    = IndexedObjectDescriptor("LONG-NAME")
    measurements = IndexedObjectDescriptor("CALIBRATION-MEASUREMENT")
    messages     = IndexedObjectDescriptor("MESSAGE")
    origins      = IndexedObjectDescriptor("ORIGIN")
    parameters   = IndexedObjectDescriptor("PARAMETER")
    paths        = IndexedObjectDescriptor("PATH")
    processes    = IndexedObjectDescriptor("PROCESS")
    splices      = IndexedObjectDescriptor("SPLICE")
    tools        = IndexedObjectDescriptor("TOOL")
    wellrefs     = IndexedObjectDescriptor("WELL-REFERENCE")
    zones        = IndexedObjectDescriptor("ZONE")

    @property
    def unknowns(self):
        """ Return all objects that are unknown to dlisio. I.e. vendor-specific
        objects. """
        return (obj
            for typename, object_set in self.indexedobjects.items()
            for obj in object_set.values()
            if typename not in self.types
        )


    def match(self, pattern, type="CHANNEL"):
        """ Filter channels by mnemonics

        Returns all objects of given type with mnemonics matching a regex [1].
        By default only matches pattern against Channel objects.
        Use the type parameter to match against other object types.
        Note that type support regex as well.
        Pattern and type are not case-sensitive, i.e. match("TDEP") and
        match("tdep") yield the same result.

        [1] https://docs.python.org/3.7/library/re.html

        Parameters
        ----------

        pattern : str
            Regex to match object mnemonics against.

        type : str
            Extend the targeted object-set to include all objects that
            have a type which matches the supplied type.
            type may be a regex.
            To see available types, refer to dlis.types.keys()

        Yields
        -------

        objects : generator of objects

        Notes
        -----

        Some common regex characters:

        ====== =======================
        Regex  Description
        ====== =======================
        '.'    Any character
        '^'    Starts with
        '$'    Ends with
        '*'    Zero or more occurrences
        '+'    One or more occurrences
        '|'    Either or
        '[]'   Set of characters
        ====== =======================

        **Please bear in mind that any special character you include
        will have special meaning as per regex**

        Examples
        --------

        Return all channels which have mnemonics matching 'AIBK':

        >>> channels = f.match('AIBK')

        Return all objects which have mnemonics matching the regex
        'AIBK', targeting all object-types starting with 'CHANNEL':

        >>> channels = f.match('AIBK', type='^CHANNEL')

        Return all CHANNEL objects where the mnemonic matches 'AI':

        >>> channels = f.match('AI.*')

        Return all CUSTOM-FRAME objects where the mnemonic includes 'PR':

        >>> frames = f.match('.*RP.*', 'custom-frame')

        Remember, that special characters always have their regex meaning:

        >>> for o in f.match("CHANNEL.23"):
        ...     print(o)
        Channel(CHANNEL.23)
        Channel(CHANNEL123)

        """
        def compileregex(pattern):
            try:
                return re.compile(pattern, re.IGNORECASE)
            except:
                msg = 'Invalid regex: {}'.format(pattern)
                raise ValueError(msg)

        objs = {}
        ctype = compileregex(type)
        for key, value in self.indexedobjects.items():
            if not re.match(ctype, key): continue
            objs.update(value)

        cpattern = compileregex(pattern)
        for obj in objs.values():
            if not re.match(cpattern, obj.name): continue
            yield obj

    def object(self, type, name, origin=None, copynr=None):
        """
        Direct access to a single object.
        dlis-objects are uniquely identifiable by the combination of
        type, name, origin and copynumber of the object. However, in most cases
        type and name are sufficient to identify a specific object.
        If origin and/or copynr is omitted in the function call, and there are
        multiple objects matching the type and name, a ValueError is raised.

        Parameters
        ----------
        type: str
            type as specified in RP66
        name: str
            name
        origin: number, optional
            number specifying which origin object the current object belongs to
        copynr: number, optional
            number specifying the copynumber of current object

        Returns
        -------
        obj: searched object

        Examples
        --------

        >>> ch = f.object("CHANNEL", "MKAP", 2, 0)
        >>> print(ch.name)
        MKAP

        """
        if origin is None or copynr is None:
            obj = list(self.match('^'+name+'$', type))
            if len(obj) == 1:
                return obj[0]
            elif len(obj) == 0:
                msg = "No objects with name {} and type {} are found"
                raise ValueError(msg.format(name, type))
            elif len(obj) > 1:
                msg = "There are multiple {}s named {}. Found: {}"
                desc = ""
                for o in obj:
                    desc += ("(origin={}, copy={}), "
                             .format(o.origin, o.copynumber))
                raise ValueError(msg.format(type, name, desc))
        else:
            fingerprint = core.fingerprint(type, name, origin, copynr)
            try:
                return self.indexedobjects[type][fingerprint]
            except KeyError:
                msg = "Object {}.{}.{} of type {} is not found"
                raise ValueError(msg.format(name, origin, copynr, type))

    def describe(self, width=80, indent=''):
        """Printable summary of the logical file

        Parameters
        ----------

        width : int
            maximum width of each line.

        indent : str
            string that will be prepended to each line.

        Returns
        -------

        summary : Summary
            A printable summary of the logical file
        """
        buf = StringIO()
        plumbing.describe_header(buf, 'Logical File', width, indent)

        d = OrderedDict()
        d['Description']  = repr(self)
        d['Frames']       = len(self.frames)
        d['Channels']     = len(self.channels)

        objects = {}
        for v in self.indexedobjects.values():
            objects.update(v)

        d['Object count'] = len(objects)
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

    def load(self, sets=None):
        """ Load and enrich raw objects into the object pool

        This method converts the raw object sets into first-class dlisio python
        objects, and puts them in the objects, indexedobjects and problematic
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
                    obj = self.types[os.type].create(o, name = name, file = self)
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

        self.indexedobjects = indexedobjects
        self.problematic = problematic
        return self

    def storage_label(self):
        """Return the storage label of the physical file

        Notes
        -----

        This method is mainly intended for internal use.
        """
        blob = self.file.get(bytearray(80), self.sul_offset, 80)
        return core.storage_label(blob)

    def raw_objectsets(self):
        """ Return the objects as represented on disk

        Parses attic and returns objects. If attic is empty, will extract
        data from disk.

        Notes
        -----

        These objects are primitive versions of the Python Classes
        that dlisio uses to create a rich interface for the different object
        types. If they are of interest, the preferred way of accessing them is
        through the attic attribute of this class, or the attic attribute of
        the rich objects.
        """
        if self.attic is None:
            self.attic = self.file.extract(self.explicit_indices)

        return core.parse_objects(self.attic)

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

    Note that the parentheses are needed when unpacking directly in the with-
    statement.  The asterisk allows an arbitrary number of extra logical files
    to be stored in tail. Use len(tail) to check how many extra logical files
    there are.

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
