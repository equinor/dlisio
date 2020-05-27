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

def get_encodings():
    """Get codepages to use for decoding strings

    Get the currently set codepages used when decoding strings.

    Returns
    -------
    encodings : list

    See also
    --------
    set_encodings
    """
    return core.get_encodings()

def set_encodings(encodings):
    """Set codepages to use for decoding strings

    RP66 specifies that all strings should be in ASCII, meaning 7-bit. Strings
    in ASCII have identical bitwise representation in UTF-8, and python strings
    are in UTF-8. However, a lot of files contain strings that aren't ASCII,
    but encoded in some way - a common is the degree symbol [1]_, but plenty of
    files use other encodings too.

    This function sets the code pages that dlisio will try *in order* when
    decoding strings (IDENT, ASCII, UNITS, and when they appear as members in
    e.g. ATTREF). UTF-8 will always be tried first, and is always correct if
    the file behaves according to spec.

    Available encodings can be found in the Python docs [2]_.

    If none of the encodings succeed, all strings will be returned as a bytes
    object.

    Parameters
    ----------
    encodings : list of str
        Ordered list of encodings to try

    Warns
    -----
    UnicodeWarning
        When no decode was successful, and a bytes object is returned

    Warnings
    --------
    There is no place in the DLIS spec to put or look for encoding information,
    decoding is a wild guess. Plenty of strings are valid in multiple encodings,
    so there's a high chance that decoding with the wrong encoding will give a
    valid string, but not the one the writer intended.

    See also
    --------
    get_encodings : currently set encodings

    Notes
    -----
    Strings are decoded using Python's bytes.decode(errors = 'strict').

    References
    ----------
    .. [1] https://stackoverflow.com/questions/8732025/why-degree-symbol-differs
    .. [2] https://docs.python.org/3/library/codecs.html#standard-encodings

    Examples
    --------
    Decoding of the same string under different encodings

    >>> dlisio.set_encodings([])
    >>> with dlisio.load('file.dlis') as (f, *_):
    ...     print(getchannel(f).units)
    b'custom unit\\xb0'
    >>> dlisio.set_encodings(['latin1'])
    >>> with dlisio.load('file.dlis') as (f, *_):
    ...     print(getchannel(f).units)
    'custom unit°'
    >>> dlisio.set_encodings(['utf-16'])
    >>> with dlisio.load('file.dlis') as (f, *_):
    ...     print(getchannel(f).units)
    '畣瑳浯甠楮끴'
    """
    core.set_encodings(list(encodings))

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
        problematic. Mainly intended for debugging files.

    indexedobject : dict
        A inventory of __loaded__ objects in the logical file, indexed by type.
        Only intended as internal storage. It is not intended to be accessed
        directly.
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

    >>> from dlisio.plumbing import BasicObject
    >>> from dlisio.plumbing import scalar, vector, obname
    >>> class Channel440(BasicObject):
    ...     attributes = {
    ...       'LONG-NAME' : scalar,
    ...       'SAMPLES'   : vector,
    ...     }
    ...     linkage= { 'longname' : obname('LONG-NAME') }
    ...
    ...     def __init__(self, obj = None, name = None):
    ...       super().__init_(obj, name = name, type = '440-CHANNEL')
    ...
    ...     @property
    ...     def longname(self):
    ...         return self['LONG-NAME']
    ...
    ...     @property
    ...     def samples(self):
    ...         return self['SAMPLES']

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

    def __init__(self, stream, explicits, attic, implicits, sul=None):
        self.file = stream
        self.explicit_indices = explicits
        self.attic = attic
        self.sul = sul
        self.fdata_index = implicits

        self.indexedobjects = defaultdict(dict)
        self.problematic = []

        self.record_types = core.parse_set_types(self.attic)

        types = ('FILE-HEADER', 'ORIGIN', 'FRAME', 'CHANNEL')
        recs  = [rec for rec, t in zip(self.attic, self.record_types) if t in types]
        self.load(recs)

        if 'UPDATE' in self.record_types:
            msg = ('{} contains UPDATE-object(s) which changes other '
                   'objects. dlisio lacks support for UPDATEs, hence the '
                   'data in this logical file might be wrongly presented.')

            logging.warning(msg.format(self))

    def __getitem__(self, type):
        """Return all objects of a given type. Parses and caches relevant
        records if objects of the given type is not parsed yet.

        All direct access of objects should be routed through this method, to
        ensure unloaded objects are loaded when asked for.

        Parameters
        ----------
        type : str
            object type, e.g. CHANNEL

        Returns
        -------

        objects : dict
            all objects of type 'type'
        """
        if type in self.indexedobjects:
            return self.indexedobjects[type]

        recs = [rec
            for rec, t
            in zip(self.attic, self.record_types)
            if t == type
        ]

        self.load(recs, reload=False)

        return self.indexedobjects[type]

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
        except AttributeError:
            desc = 'Unknown'
        return 'dlis({})'.format(desc)

    class IndexedObjectDescriptor:
        """ Return all objects of this type"""
        def __init__(self, t):
            self.t = t

        def __get__(self, instance, owner):
            if instance is None: return None
            return instance[self.t].values()

    @property
    def fileheader(self):
        """ Return the Fileheader

        Returns
        -------
        fileheader : Fileheader

        """
        values = list(self['FILE-HEADER'].values())

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
        """Return all objects that are unknown to dlisio.

        Unknown objects are object-types that dlisio does not know about. By
        default, any metadata object not defined by rp66v1 [1]. The are all
        parsed as :py:class:`dlisio.plumbing.Unknown`, that implements a dict
        interface.

        [1] http://w3.energistics.org/rp66/v1/Toc/main.html

        Notes
        -----
        Adding a custom python class for an object-type to dlis.types will
        in-effect remove all objects of that type from unknowns.

        Returns
        -------
        objects : defaultdict(list)
            A defaultdict index by object-type

        """
        recs = [rec for rec, t in zip(self.attic, self.record_types)
            if  t not in self.types
            and not rec.encrypted
            and t not in self.indexedobjects
        ]

        self.load(recs, reload=False)

        unknowns = defaultdict(list)

        for key, value in self.indexedobjects.items():
            if key in self.types: continue
            unknowns[key] = value

        return unknowns

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

        ctype    = compileregex(type)
        cpattern = compileregex(pattern)

        types = [x for x in set(self.record_types) if re.match(ctype, x)]

        for t in types:
            for obj in self[t].values():
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
                return self[type][fingerprint]
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

        plumbing.describe_dict(buf, d, width, indent)

        known, unknown = {}, {}
        for objtype in set(self.record_types):
            if objtype == 'encrypted': continue

            if objtype in self.types: known[objtype]   = len(self[objtype])
            else:                     unknown[objtype] = len(self[objtype])

        if known:
            plumbing.describe_header(buf, 'Known objects', width, indent, lvl=2)
            plumbing.describe_dict(buf, known, width, indent)

        if unknown:
            plumbing.describe_header(buf, 'Unknown objects', width, indent, lvl=2)
            plumbing.describe_dict(buf, unknown, width, indent)

        return plumbing.Summary(info=buf.getvalue())

    def load(self, records=None, reload=True):
        """ Load and enrich raw objects into the object pool

        This method converts the raw object sets into first-class dlisio python
        objects, and puts them in the indexedobjects and problematic members.

        Parameters
        ----------

        records : iterable of records

        reload : bool
            If False, append the new object too the pool of objects. If True,
            overwrite the existing pool with new objects.

        Notes
        -----

        This method is mainly intended for internal use. It serves as a worker
        for other methods that needs to populate the pool with new objects.
        It's the callers responsibility to keep track of the current state of
        the pool, and not load the same objects into the pool several times.

        Examples
        --------

        When opening a file with dlisio.load('path') only a few object-types
        are loaded into the pool. If need be, it is possible to force dlisio to
        load every object in the file into its internal cache:

        >>> with dlisio.load('file') as (f, *tail):
        ...     f.load()

        """
        problem = 'multiple distinct objects '
        where = 'in set {} ({}). Duplicate fingerprint = {}'
        action = 'continuing with the last object'
        duplicate = 'duplicate fingerprint {}'

        if reload:
            indexedobjects = defaultdict(dict)
            problematic    = []

        else:
            indexedobjects = self.indexedobjects
            problematic    = self.problematic

        if records is None: records = self.attic
        sets = core.parse_objects(records)

        for os in sets:
            # TODO: handle replacement sets
            for name, o in os.objects.items():
                try:
                    obj = self.types[os.type](o, name = name, lf = self)
                except KeyError:
                    obj = plumbing.Unknown(
                        o,
                        name = name,
                        type = os.type,
                        lf = self
                    )

                fingerprint = obj.fingerprint
                if fingerprint in indexedobjects[os.type]:
                    original = indexedobjects[os.type][fingerprint]

                    logging.info(duplicate.format(fingerprint))
                    if original.attic != obj.attic:
                        msg = problem + where
                        msg = msg.format(os.type, os.name, fingerprint)
                        logging.error(msg)
                        logging.warning(action)
                        problematic.append((original, obj))

                indexedobjects[obj.type][fingerprint] = obj


        self.indexedobjects = indexedobjects
        self.problematic    = problematic

        if 'FRAME' not in [x.type for x in sets]: return self

        # Frame objects need the additional step of updating its Channels with
        # a reference back to itself. See Frame.link()
        for obj in self.indexedobjects['FRAME'].values():
            obj.link()

        return self

    def storage_label(self):
        """Return the storage label of the physical file

        Notes
        -----

        This method is mainly intended for internal use.
        """
        if not self.sul:
            logging.warning('file has no storage unit label')
            return None
        return core.storage_label(self.sul)


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
    return core.open(str(path))

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
    stream = open(path)

    sulsize = 80
    tifsize = 12

    try:
        offset = core.findsul(stream)
        sul = stream.get(bytearray(sulsize), offset, sulsize)
        offset += sulsize
    except:
        offset = 0
        sul = None

    tapemarks = core.hastapemark(stream)
    offset = core.findvrl(stream, offset)

    def rewind(offset, tif):
        """Rewind offset to make sure not to miss VRL when calling findvrl"""
        offset -= 4
        if tif: offset -= 12
        return offset

    # Layered File Protocol does not currently offer support for re-opening
    # files at the current position, nor is it able to precisly report the
    # underlying tell. Therefore, dlisio has to manually search for the
    # VRL to determine the right offset in which to open the new filehandle
    # at.
    #
    # Logical files are partitioned by core.findoffsets and it's required
    # [1] that new logical files always start on a new Visible Record.
    # Hence, dlisio takes the (approximate) tell at the end of each Logical
    # File and searches for the VRL to get the exact tell.
    #
    # [1] rp66v1, 2.3.6 Record Structure Requirements:
    #     > ... Visible Records cannot intersect more than one Logical File.
    lfs = []
    while True:
        if tapemarks: offset -= tifsize
        stream.seek(offset)
        if tapemarks: stream = core.open_tif(stream)
        stream = core.open_rp66(stream)

        explicits, implicits = core.findoffsets(stream)
        hint = rewind(stream.absolute_tell, tapemarks)

        records = core.extract(stream, explicits)
        fdata_index = defaultdict(list)
        for key, val in core.findfdata(stream, implicits):
            fdata_index[key].append(val)

        lf = dlis(stream, explicits, records, fdata_index, sul)
        lfs.append(lf)

        try:
            stream = core.open(path)
            offset = core.findvrl(stream, hint)
        except RuntimeError:
            if stream.eof(): break
            raise

    return Batch(lfs)

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

