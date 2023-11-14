import re

import logging
log = logging.getLogger(__name__)

from collections import defaultdict, OrderedDict
from io import StringIO

from .axis import Axis
from .fileheader import Fileheader
from .longname import Longname
from .origin import Origin
from .frame import Frame, mkunique
from .channel import Channel
from .tool import Tool
from .zone import Zone
from .parameter import Parameter
from .calibration import Calibration
from .comment import Comment
from .equipment import Equipment
from .measurement import Measurement
from .message import Message
from .computation import Computation
from .coefficient import Coefficient
from .splice import Splice
from .wellref import Wellref
from .group import Group
from .path import Path
from .process import Process
from .unknown import Unknown
from .noformat import Noformat

from .. import core
from . import utils

""" dlis and exact matchers are frequently used by most methods on
LogicalFile. To avoid the overhead of initializing a new instance of these for
every method-call they are cached as globals here.

Although possible, these globals are not intended to be changed by the end user directly.
"""
regex = utils.regex_matcher(re.IGNORECASE)
exact = utils.exact_matcher()

class PhysicalFile(tuple):
    """ A Physical File

    A physical DLIS file, i.e. a regular file on disk, is segmented into
    multiple Logical Files (LF). Think of a DLIS file as a folder-structure.
    The DLIS-file itself is the folder, and the Logical Files are the actual
    files::

        your_file.dlis
        |
        |-> Logical File 0
        |-> Logical File 1
        |-> Logical File 2
        ...
        |-> Logical File n


    Each LF is a logical grouping of log data and metadata related to the
    acquisition of those logs. The LF's are independent of each other and can
    be thought of as separate files.

    This class is essentially a tuple of all the Logical Files in a regular
    file, and is what's being returned by :func:`dlisio.dlis.load`. The LFs can be
    unpacked following standard Python tuple unpacking rules.

    Notes
    -----

    The DLIS-specification, rp66v1, opens up for a Logical File to span
    multiple physical files. dlisio does not currently have cross-file support.
    We have yet to see any files in the wild using this feature. Note that
    dlisio will still be able to open such files, but any internal
    cross-referencing will be lost.

    See Also
    --------

    dlisio.dlis.load : Open and Index a DLIS-file
    dlisio.dlis.LogicalFile : Interface for working with a single Logical File
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """ Close the file handles of all Logical Files """
        for f in self:
            f.close()

    def __repr__(self):
        return 'PhysicalFile(logical files: {})'.format(len(self))

    def describe(self, width=80, indent=''):
        """ Describe

        Returns a human-readable and printable summary of the current Physical
        File.
        """
        buf = StringIO()
        utils.describe_header(buf, 'Physical File', width, indent)

        d = {'Number of Logical Files' : len(self)}
        utils.describe_dict(buf, d, width, indent)

        for f in self:
            d = OrderedDict()
            d['Description'] = repr(f)
            d['Frames']   = len(f.frames)
            d['Channels'] = len(f.channels)
            utils.describe_dict(buf, d, width, indent)

        return utils.Summary(info=buf.getvalue())


class ObjectStore():
    """ Metadata handler for LogicalFile

    This class stores all the object sets from the LogicalFile and promotes
    them to proper Python objects (e.g. Channel()) when the store is queried.
    It uses dl::pool as a backend for fetching the raw c++ objects.

    By default, the promoted Python objects are cached to avoid a lot off
    unnecessary re-creations. This can be toggled on/off.

    Use :func:`find` to fetch objects.

    Note that for simplicity the store will read and cache _all_ objects of the
    queried type. This is not applicable when caching is off.

    The cache-layout is deliberately chosen to ensure fast lookup for common
    queries, while also allowing duplicated objects (identical type, name,
    origin and copynumber). The layout is a nested dict, where the objects are
    indexed first by type, then by name. E.g:

      store = {
          'FRAME' : {
              'FRAME60' : [Frame('FRAME60'), Frame('FRAME60')],
              'FRAME20' : [Frame('FRAME20')]
          },
          'CHANNEL' : {
              'TDEP' : [Channel('TDEP')]
              'GR'   : [Channel('GR')]
          }
      }
    """
    def __init__(self, logical_file, object_sets):
        self.pool         = object_sets
        self.logical_file = logical_file

        #: Turn on/off caching. If set to False, nothing is ever cached in
        #: :attr:`store`, and objects will be re-created from
        #: :attr:`object_sets` on each query.
        self.caching = True
        self.cache   = {}

    def types(self):
        return set(self.pool.types)

    def __getitem__(self, object_type):
        """ Return all objects of type object_type

        This method should be considered internal to this class and all queries
        from the outside should go through either :func:`get` or :func:`find`.

        Notes
        -----

        This is the _only_ method that should attempt to cache python objects.

        Returns
        -------

        objects : defaultdict(list)
            A defaultdict where objects are indexed by their name

        Examples
        --------

        Get all channels:
        >>> cache['CHANNEL']
        { 'TDEP' : [Channel('TDEP'), Channel('TDEP')], 'GR' : [Channel('GR')] }

        Get all TDEP channels:

        >>> cache['CHANNEL']['TDEP']
        [Channel('TDEP'), Channel('TDEP')]
        """
        if object_type in self.cache:
            return self.cache[object_type]

        attics = self.pool.get(
                object_type,
                exact,
                self.logical_file.error_handler
        )

        objects = defaultdict(list)
        for obj in self.promote(attics):
            objects[obj.name].append(obj)

        if self.caching:
            self.cache[object_type] = objects

        return objects

    def clear_cache(self):
        """Clear all cached objects """
        self.cache = {}

    def find(self, object_type, object_name=None, matcher=None):
        """ Returns matching objects

        find will first look for objects in the cache (if on). If there is no
        objects to be found in the cache the method will continue to look in
        the C++ pool. If found and caching is on, the result will be cached
        before returned.
        """
        if matcher is None: matcher = exact

        if not self.caching:
            if not object_name:
                attics = self.pool.get(
                    object_type,
                    matcher,
                    self.logical_file.error_handler
                )
            else:
                attics = self.pool.get(
                    object_type,
                    object_name,
                    matcher,
                    self.logical_file.error_handler
                )

            return self.promote(attics)

        # This is an optimalization for direct cache lookup.
        if isinstance(matcher, utils.exact_matcher) and object_name is not None:
            return self[object_type][object_name]

        types = [x for x in self.types() if matcher.match(object_type, x)]

        matches = []
        for obj_type in types:
            for name, objs in self[obj_type].items():
                if object_name is None or matcher.match(object_name, name):
                    matches.extend(objs)
        return matches

    def promote(self, attics):
        """Promote dlisio.core.basic_objects to first-class Python objects

        E.g. Channel(), Frame() or Tool()
        """
        objects = []
        for attic in attics:
            try:
                pythontype = self.logical_file.types[attic.type]
                obj = pythontype(attic, lf=self.logical_file)
            except KeyError:
                obj = Unknown(attic, lf=self.logical_file)

            objects.append(obj)

        return objects


class LogicalFile(object):
    """Logical file (LF)

    This class supplies the main interface for working with a single Logical
    File. A Logical File contains log data and metadata related to the
    acquisition of the logs. The metadata is stored as 'objects' - in lack of a
    better word.  There are different object-types for different types of data.
    The logs can be acquired through Frame- and Channel-objects
    (:class:`dlisio.dlis.Frame` and :class:`dlisio.dlis.Channel`).
    There is also an abundance of object-types for storing other metadata: Tool,
    Parameter, Measurement and Calibration to name a few.

    :py:func:`object()` and :py:func:`find()` let you access specific objects
    or search for objects matching a regular expression. Unknown objects such
    as vendor-specific objects are accessible through the 'unknown'-attribute.

    Uniquely identifying an object within a logical file can be a bit
    cumbersome, and confusing.  It requires no less than 4 attributes!  Namely,
    the object's type, name, origin and copynumber.  The standard allows for
    two objects of the same type to have the same name, as long as either their
    origin or copynumber differ. E.g. there may exist two channels with the
    same name/mnemonic.

    **Metadata caching**

    All metadata (e.g. Frame, Channel, Parameter) are cached by default. This
    avoids re-creation of the same objects.

    Note that changes to settings such as :func:`dlisio.common.set_encodings`
    or :attr:`LogicalFile.error_handler` *after* loading the file will not
    propagate to already-cached objects. It's therefore advisable that such
    settings are set before loading the file. Alternatively, you can manually
    toggle on and off caching to clear it with :func:`cache_metadata`.
    """
    types = {
        'AXIS'                   : Axis,
        'FILE-HEADER'            : Fileheader,
        'ORIGIN'                 : Origin,
        'LONG-NAME'              : Longname,
        'FRAME'                  : Frame,
        'CHANNEL'                : Channel,
        'ZONE'                   : Zone,
        'TOOL'                   : Tool,
        'PARAMETER'              : Parameter,
        'EQUIPMENT'              : Equipment,
        'CALIBRATION-MEASUREMENT': Measurement,
        'CALIBRATION-COEFFICIENT': Coefficient,
        'CALIBRATION'            : Calibration,
        'COMPUTATION'            : Computation,
        'SPLICE'                 : Splice,
        'WELL-REFERENCE'         : Wellref,
        'GROUP'                  : Group,
        'PROCESS'                : Process,
        'PATH'                   : Path,
        'MESSAGE'                : Message,
        'COMMENT'                : Comment,
        'NO-FORMAT'              : Noformat,
    }

    """dict: Dispatch-table for turning :py:class:`dlisio.core.basic_object`
    into type-specific python objects like Channel and Frame.  This is mainly
    intended for internal use so the typical user can safely ignore this
    attribute.

    Object-types not present in the table are considered as unknowns. They can
    still be reached through :py:func:`object` and :py:func:`find` but lack
    the syntactic sugar added by the type-specific classes.

    It is possible to monkey-patch the dispatch-table with your own custom
    classes. However this is considered to be a fairly advanced usage and it's
    then the users responsibility of ensuring correctness for the custom class.
    """

    def __init__(self, stream, object_sets, fdata_index, sul, error_handler):
        self.file = stream
        self.sul  = sul

        self.fdata_index = fdata_index
        self.store       = ObjectStore(self, object_sets)

        self.error_handler = error_handler

        if 'UPDATE' in self.store.types():
            msg = ('{} contains UPDATE-object(s) which changes other '
                   'objects. dlisio lacks support for UPDATEs, hence the '
                   'data in this logical file might be wrongly presented.')

            log.warning(msg.format(self))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Close the file handle

        It is not necessary to call this method if you're using the `with`
        statement, which will close the file for you.
        """
        self.file.close()

    def __repr__(self):
        try:
            desc = self.fileheader.id
        except AttributeError:
            desc = 'Unknown'
        return 'LogicalFile({})'.format(desc)

    def cache_metadata(self, cache):
        """ Toggle caching of metadata objects

        By default, the metadata objects are cached to avoid unnecessary
        re-creation of objects. Like all caching, this trades CPU time for
        memory usage.

        Parameters
        ----------

        cache : bool
            Toggle caching on/off
        """
        self.store.clear_cache()
        self.store.caching = cache

    class IndexedObjectDescriptor:
        """ Return all objects of this type"""
        def __init__(self, t):
            self.t = t

        def __get__(self, instance, owner):
            if instance is None: return None
            return instance.find(self.t, matcher=exact)

    @property
    def fileheader(self):
        """ Return the Fileheader

        Returns
        -------
        fileheader : Fileheader

        """
        values = self.find('FILE-HEADER', matcher=exact)

        if len(values) != 1:
            msg = "Expected exactly one fileheader. Was: {}"
            log.warning(msg.format(values))
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
    noformats    = IndexedObjectDescriptor("NO-FORMAT")

    @property
    def unknowns(self):
        """Return all objects that are unknown to dlisio.

        Unknown objects are object-types that dlisio does not know about. By
        default, any metadata object not defined by rp66v1 [1]. The are all
        parsed as :py:class:`dlisio.dlis.Unknown`, that implements a dict
        interface.

        [1] https://energistics.org/sites/default/files/RP66/V1/Toc/main.html

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
        for t in self.store.types():
            if t in self.types: continue
            objects = self.find(t, matcher=exact)
            unknowns[t] = {x.fingerprint : x for x in objects}

        return unknowns

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
                  :py:attr:`dlisio.dlis.regex`.

        Returns
        -------

        objects : list
            A list of all objects in the logicalfile that matches objecttype
            (and objectname)

        See also
        --------

        dlisio.dlis.utils.exact_matcher : str comparison w/ str.__eq__
        dlisio.dlis.utils.regex_matcher : str comparison w/ python's re module

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

        >>> f.find('FRAME', matcher=dlisio.dlis.exact)
        [Frame(60B), Frame(20B), Frame(10B)]
        """
        if matcher is None: matcher = regex
        return self.store.find(objecttype, objectname, matcher)


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
        matches = self.store.find(type, name, exact)

        if origin is not None:
            matches = [o for o in matches if o.origin == origin]

        if copynr is not None:
            matches = [o for o in matches if o.copynumber == copynr]

        if len(matches) == 1: return matches[0]

        if len(matches) == 0:
            msg = "Object not found: type={}, name={}, origin={}, copynumber={}"
            if origin is None: origin = "'any'"
            if copynr is None: copynr = "'any'"

            raise ValueError(msg.format(type, name, origin, copynr))

        # We found multiple matching objects. If they are all equal, return one
        # of them and be done with it
        if all(x.attic == matches[0].attic for x in matches):
            return matches[0]

        msg = "Multiple {} objects with name {}. Candidates are:"
        candidate = "\norigin={}, copy={},"
        candidates = [candidate.format(x.origin, x.copynumber) for x in matches]

        msg += ''.join(candidates)
        raise ValueError(msg.format(type, name))


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

        summary : dlisio.dlis.utils.Summary
            A printable summary of the logical file
        """
        buf = StringIO()
        utils.describe_header(buf, 'Logical File', width, indent)

        d = OrderedDict()
        d['Description']  = repr(self)
        d['Frames']       = len(self.frames)
        d['Channels']     = len(self.channels)

        utils.describe_dict(buf, d, width, indent)

        known, unknown = {}, {}
        for objtype in self.store.types():
            objs = self.find(objtype, matcher=exact)
            if objtype in self.types: known[objtype]   = len(objs)
            else:                     unknown[objtype] = len(objs)

        if known:
            utils.describe_header(buf, 'Known objects', width, indent, lvl=2)
            utils.describe_dict(buf, known, width, indent)

        if unknown:
            utils.describe_header(buf, 'Unknown objects', width, indent, lvl=2)
            utils.describe_dict(buf, unknown, width, indent)

        return utils.Summary(info=buf.getvalue())

    def load(self):
        """ Force load all objects - mainly indended for debugging"""
        _ = [self.find(x, matcher=exact) for x in self.store.types()]

    def storage_label(self):
        """Return the storage label of the physical file

        Notes
        -----

        This method is mainly intended for internal use.
        """
        if not self.sul:
            log.warning('file has no storage unit label')
            return None
        return core.storage_label(self.sul)
