import logging
import re

from collections import defaultdict, OrderedDict
from io import StringIO

from . import core
from . import plumbing

class physicalfile(tuple):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        for f in self:
            f.close()

    def __repr__(self):
        return 'physicalfile(logical files: {})'.format(len(self))

    def describe(self, width=80, indent=''):
        buf = StringIO()
        plumbing.describe_header(buf, 'Physical File', width, indent)

        d = {'Number of Logical Files' : len(self)}
        plumbing.describe_dict(buf, d, width, indent)

        for f in self:
            d = OrderedDict()
            d['Description'] = repr(f)
            d['Frames']   = len(f.frames)
            d['Channels'] = len(f.channels)
            plumbing.describe_dict(buf, d, width, indent)

        return plumbing.Summary(info=buf.getvalue())


class logicalfile(object):
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

    """dict: Dispatch-table for turning :py:class:`dlisio.core.basic_objects`
    into type-specific python objects like Channel and Frame.  This is mainly
    intended for internal use so the typical user can safely ignore this
    attribute.

    Object-types not present in the table are considered as unknowns. They can
    still be reached through :py:func:`object` and :py:func:`match` but lack
    the syntactic sugar added by the type-specific classes.

    It is possible to monkey-patch the dispatch-table with your own custom
    classes. However this is considered to be a fairly advanced usage and it's
    then the users responsibility of ensuring correctness for the custom class.
    """

    def __init__(self, stream, object_pool, fdata_index, sul=None):
        self.file = stream
        self.object_pool = object_pool
        self.sul = sul
        self.fdata_index = fdata_index

        if 'UPDATE' in self.object_pool.types:
            msg = ('{} contains UPDATE-object(s) which changes other '
                   'objects. dlisio lacks support for UPDATEs, hence the '
                   'data in this logical file might be wrongly presented.')

            logging.warning(msg.format(self))

    def __getitem__(self, type):
        """Return all objects of a given type

        Parameters
        ----------
        type : str
            object type, e.g. CHANNEL

        Returns
        -------

        objects : dict
            all objects of type 'type'
        """
        objs = self.object_pool.get(type, plumbing.exact_matcher())
        return { x.fingerprint : x for x in self.promote(objs) }

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
        return 'logicalfile({})'.format(desc)

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
        objects : defaultdict(dict)
            A defaultdict index by object-type

        """
        unknowns = defaultdict(dict)
        for t in set(self.object_pool.types):
            if t in self.types: continue
            unknowns[t] = self[t]

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

        # Use python's re with case-insensitivity as matcher when searching for
        # object_pool objects in dl::pool
        matcher = plumbing.regex_matcher(re.IGNORECASE);
        matches = self.object_pool.get(type, pattern, matcher)
        return self.promote(matches)

    def find(self, objecttype, objectname=None, matcher=None):
        """Find objects in the logical file

        Find searches and returns all objects matching objecttype, and if
        specified, objectname. By default find uses python's re module with
        case-insensitivity when searching for objects matching objecttype and
        objectname. See examples for how to use.

        Parameters
        ----------

        objectype : str
            type of objects to be looked for

        objectname : str, optional
            name / mnemonic of objects to be looked for

        matcher : Any matcher derived from dlisio.core.matcher, optional
                  matcher object to be used when comparing objecttype,
                  objectname to file content. Default is
                  :py:func:`dlisio.regex_matcher(re.IGNORECASE)`.

        Returns
        -------

        objects : list
            A list of all objects in the logicalfile that matches objecttype
            (and objectname)

        See also
        --------

        plumbing.exact_matcher : string comparison using str.__eq__
        plumbing.regex_matcher : string comparison using python's re module

        Examples
        --------

        Query for all Channels where the name / mnemonic contains 'GR':

        >>> f.find('CHANNEL', '.*GR.*')
        [Channel(GR), Channel(GR1)]

        Query for all Channel-like objects. I.e. both regular Channels and
        vendor-specific ones:

        >>> f.find('.*CHANNEL')
        [Channel(TDEP), Channel(GR), Channel(GR1), 440channel(GR2)]

        The two queries above can be combined:

        >>> f.find('.*CHANNEL', '.*GR.*')
        [Channel(GR), Channel(GR1), 440channel(GR2)]

        Omitting the objectname yields *all* objects matching objecttype:

        >>> f.find('FRAME')
        [Frame(60B), Frame(20B), Frame(10B)]

        If your query does not include a regular expression and you care about
        performance, tell find to use the default exact matcher. For large
        files there is a significant difference between comparing strings with
        self.exact and compiling- and comparing regex expressions with
        self.regex.

        >>> f.find('FRAME', matcher=dlisio.plumbing.exact_matcher())
        [Frame(60B), Frame(20B), Frame(10B)]
        """
        if not matcher:
            matcher = plumbing.regex_matcher(re.IGNORECASE)

        if not objectname:
            attics = self.object_pool.get(objecttype, matcher)
        else:
            attics = self.object_pool.get(objecttype, objectname, matcher)

        return self.promote(attics)

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
        matches = self.object_pool.get(type, name, plumbing.exact_matcher())
        matches = self.promote(matches)

        if origin is not None:
            matches = [o for o in matches if o.origin == origin]

        if copynr is not None:
            matches = [o for o in matches if o.copynumber == copynr]

        if len(matches) == 1: return matches[0]

        if len(matches) == 0:
            if origin is not None and copynr is not None:
                msg = "Object {}.{}.{} of type {} is not found"
                raise ValueError(msg.format(name, origin, copynr, type))
            else:
                msg = "No objects with name {} and type {} are found"
                raise ValueError(msg.format(name, type))

        # We found multiple matching objects. If they are all equal, return one
        # of them and be done with it
        if all(x.attic == matches[0].attic for x in matches):
            return matches[0]

        msg = "There are multiple {}s named {}. Found: {}"
        desc = ""
        for o in matches:
            desc += ("(origin={}, copy={}), "
                        .format(o.origin, o.copynumber))
        raise ValueError(msg.format(type, name, desc))


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
        for objtype in self.object_pool.types:
            if objtype in self.types: known[objtype]   = len(self[objtype])
            else:                     unknown[objtype] = len(self[objtype])

        if known:
            plumbing.describe_header(buf, 'Known objects', width, indent, lvl=2)
            plumbing.describe_dict(buf, known, width, indent)

        if unknown:
            plumbing.describe_header(buf, 'Unknown objects', width, indent, lvl=2)
            plumbing.describe_dict(buf, unknown, width, indent)

        return plumbing.Summary(info=buf.getvalue())

    def load(self):
        """ Force load all objects - mainly indended for debugging"""
        _ = [self[x] for x in self.object_pool.types]

    def promote(self, objects):
        """Enrich instances of the generic core.basicobject into type-specific
        objects like Channel, Frame, etc... """
        objs = []
        for o in objects:
            try:
                obj = self.types[o.type](o, lf=self)
            except KeyError:
                obj = plumbing.Unknown(o, lf=self)
            objs.append(obj)
        return objs

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
