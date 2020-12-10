from .. import core
from .valuetypes import *
from .linkage import *
from .utils import *

import logging

class BasicObject():
    """A Basic object that all other object-types derive from

    BasicObject is mainly an implementation detail. Its the least common
    denominator of all object-types.

    When working with dlisio you need not care too much about the BasicObject.
    However, keep in mind that all other object-types inherit BasicObject's
    attributes and methods and they can be called directly on the objects.
    Hence it might be a good idea to somewhat familiarize yourself with its
    features.

    When reading the documentation keep in mind that the attributes defined on
    the BasicObject are **not** documented again on the derived object.

    An object is uniquely identifiable within a logical file by the combination
    of its type, name, origin and copynumber. I.e. no two objects can have the
    same type, name, origin AND copynumber. This means that the standard allows
    for e.g. two Channels to have the same name/mnemonic, which can easily
    become a bit confusing.

    Attributes
    ----------

    type : str
        Type of the object, e.g. rp66 object-types as CHANNEL or FRAME

    name : str
        Mnemonic / name

    origin : int
        Defines which origin the object belongs to

    copynumber : int
        There may exist several copies of the same object, the
        copynumber is used to distinguish them

    attic : dict_like
        Attic refers the underlying basic_object, which
        is a dict-representation of the data on disk. The attic can be
        None if this particular instance was not loaded from disk.
    """

    attributes = {}
    """dict: Parsing guide for native dlis objects. The typical user can safely
    ignore this attribute. It is mainly intended for internal use and advanced
    customization of dlisio's parsing routine.

    In short, this dictionary tells dlisio parse each attribute for a given
    object. By default it implements rules defined by the dlis-spec. However it
    can easily be customized if you'd like dlisio to parse your file in a
    different way.

    Examples
    --------

    Lets take a look at Channel.attributes, it looks like this:

    .. code-block:: python

        attributes = {
            'LONG-NAME'          : scalar,
            'REPRESENTATION-CODE': scalar,
            'UNITS'              : scalar,
            'PROPERTIES'         : vector,
            'DIMENSION'          : reverse,
            'AXIS'               : reverse,
            'ELEMENT-LIMIT'      : reverse,
            'SOURCE'             : scalar,
        }

    The keys are from the dlis-spec, i.e. this is how the attributes of a
    CHANNEL-object are named in the file. The values tells dlisio how to
    interpret these keys. In the dlis-spec it's defined that 'UNITS' only
    contains a single value. This is communicated to dlisio with the
    'scalar'-keyword. I.e. Channels __getitem__ will return a single value:

    >>> channel['UNITS']
    'm/s'

    The __getitem__ is not intended for direct use. However it is called
    internally from all properties of the Channel-object. I.e. you observe the
    same here:

    >>> channel.units
    'm/s'

    The following example might be a bit absurd, but keep in mind that this
    approach can be applied to _any_ attribute of _any_ object-type, even Unknown
    object-types.

    But now let's say that you are in possession of a file that you know is
    structured differently from what the standard specifies. It contains some
    weird Channel's where there are multiple units per Channel. Simply update
    the attribute-dict before loading the file and dlisio will parse 'UNITS' as
    a list:

    >>> from dlisio.plumbing import vector
    >>> Channel.attributes['UNITS'] = vector
    >>> with dlisio.load('file.dlis') as (f, *_):
    ...     ch = f.object('CHANNEL', 'TDEP')
    ...     ch.units
    ['m/s', 'rad/s']

    The same can be achieved for a _specific_ object. Forcing a copy of the
    attribute-dict for a given object before altering it makes sure your
    changes only apply _that_ object

    >>> ch = f.object('CHANNEL', 'TDEP')
    >>> ch.attributes = dict(ch.attributes)
    >>> Channel.attributes['UNITS'] = vector
    >>> ch.units
    ['m/s', 'rad/s']

    References
    ----------

    [1] http://w3.energistics.org/RP66/V1/Toc/main.html
    """

    linkage    = {}
    """dict: Defines which attributes contain references to other objects.  The
    typical user can safely ignore this attribute. It is mainly intended for
    internal use and advanced customization of dlisio's parsing routine.

    Object-to-object references often contains implicit information. E.g.
    Frame.channels implicitly reference Channel object, so the type 'CHANNEL' is
    not specified in the file. Hence dlisio needs to be told about this.

    Like for attributes, this behavior is customizable.

    Examples
    --------

    Change how dlisio parses Channel.source:

    >>> from dlisio.plumbing import obname
    >>> Channel.linkage['SOURCE'] = obname('PARAMETER')
    >>> with dlisio.load('file.dlis') as (f, *_):
    ...     ch = f.object('channel', 'TDEP')
    ...     ch.source
    Parameter('2000T')

    The same can be achieved for a _specific_ object. Forcing a copy of the
    linkage-dict makes sure your changes only apply to that specific object:

    >>> ch = f.object('channel', 'TDEP')
    >>> ch.linkage = dict(ch.linkage)
    >>> ch.linkage['SOURCE'] = dlisio.plumbing.parse.obname('PARAMETER')
    >>> ch.source
    Parameter('2000T')
    """

    def __init__(self, attic, lf):
        self.type       = attic.type
        self.name       = attic.name.id
        self.origin     = attic.name.origin
        self.copynumber = attic.name.copynumber

        self.attic       = attic
        self.logicalfile = lf

    def __repr__(self):
        """Return a string representation of the object"""
        return '{}({})'.format(self.type.capitalize(), self.name)

    def __getitem__(self, key):
        """Parse attributes from attic.

        Intended to be called internally from the objects, properties. For
        end-users the preferred way of reaching object-attributes are through their
        properties.

        Parse attributes from attic based on parsing rules defined in
        :attr:`attributes`. Attributes containing references to other objects
        use :attr:`linkage` to resolve the references and create fingerprints
        which are then used to look up the objects in the :attr:`logicalfile`'s
        object-pool.

        Returns a default value for missing attributes. I.e. attributes defined
        in :attr:`attributes` but are not in :attr:`attic`.
        """
        if key not in self.attributes and key not in self.attic.keys():
            raise KeyError("'{}'".format(key))

        try:
            parse_as = self.attributes[key]
        except KeyError:
            # No rule for parsing, keep rp66value as is, i.e. vector
            parse_as = vector

        # report errors before checking for key presence - it might be a symptom
        if len(self.attic.log) > 0:
            # TODO: here and for attribute: we use fingerprint to report
            # context, not repr, to have origina and copynr, but is fingerprint
            # clear enough for the user?
            context = "{}".format(self.fingerprint)
            for error in self.attic.log:
                self.logicalfile.error_handler.log(
                    error.severity, context, error.problem,
                    error.specification, error.action)

        try:
            attribute = self.attic[key]
        except KeyError:
            return defaultvalue(parse_as)

        rp66value = attribute.value

        # already report errors. presence of key in the attic is enough
        if len(attribute.log) > 0:
            context = "{}-A.{}".format(self.fingerprint, key)
            for error in attribute.log:
                self.logicalfile.error_handler.log(
                    error.severity, context, error.problem,
                    error.specification, error.action)

        if rp66value is None: return defaultvalue(parse_as)
        if rp66value == []  : return defaultvalue(parse_as)

        if key in self.linkage and isreference(rp66value[0]):
            reftype = self.linkage[key]
            value = [lookup(self.logicalfile, reftype, v) for v in rp66value]
        else:
            value = [v.strip() if isinstance(v, str) else v for v in rp66value]

        return parsevalue(value, parse_as)

    def __eq__(self, rhs):
        try:
            return self.attic == rhs.attic
        except AttributeError:
            return False

    @property
    def fingerprint(self):
        """ Object fingerprint

        Return the fingerprint, a unique identifier, for this object. This is
        basically an objref type from the RP66 standard, but with a pythonic
        flavour, and suitable for keys in dicts.

        Returns
        -------

        fingerprint : str
        """
        return core.fingerprint(self.attic.type,
                                self.attic.name.id,
                                self.attic.name.origin,
                                self.attic.name.copynumber)
    @property
    def stash(self):
        """Attributes unknown to dlisio

        It is not uncommon for objects to have 'extra' attributes that are not
        defined by the standard. Because such attributes are unknown to dlisio,
        they cannot be reach through normal attributes.

        Returns
        -------

        stash : dict
            all attributes not defined in :attr:`attributes`
        """
        stash = {
            key : self.attic[key].value
            for key
            in self.attic.keys()
            if key not in self.attributes
        }

        for key, value in stash.items():
            value = [v.strip() if isinstance(v, str) else v for v in value]
            stash[key] = value

        return stash

    def describe(self, width=80, indent='', exclude='er'):
        """Printable summary of the object

        Parameters
        ----------

        width : int
            the maximum width of each line.

        indent : str
            string that will be prepended to each line.

        exclude : str
            exclude certain parts of the object in the summary.

        Returns
        -------

        summary : Summary
            A printable summary of the object

        Notes
        -----

        The exclude parameter gives the option to omit parts of the summary.
        The table below states the different modes available.

        ====== ==========================================
        option Description
        ====== ==========================================
        'h'    header
        'a'    known attributes
        's'    attributes from stash
        'u'    units
        'i'    attributes that violates the standard  [1]
        'e'    attributes with empty values (default) [2]
        ====== ==========================================

        [1] Only applicable to attributes that should be interpreted in a
        specific way, such as Parameter.values. If not applicable, it is
        ignored.

        [2] Do not print attributes that have no value.
        """
        from io import StringIO

        buf = StringIO()
        exclude = parseoptions(exclude)

        if not exclude['head']:
            describe_header(buf, self.type.capitalize(), width, indent)
            describe_dict(buf, headerinfo(self), width, indent, exclude)

        if not exclude['attr']:
            self.describe_attr(buf, indent=indent, width=width, exclude=exclude)

        if not exclude['stash']:
            if len(self.stash) > 0:
                describe_header(buf, 'Unknown attributes', width, indent, lvl=2)
                d = {k : k for k in self.stash.keys()}
                describe_attributes(buf, d, self, width, indent, exclude)

        return Summary(info=buf.getvalue())

    def describe_attr(self, buf, width, indent, exclude):
        """Describe the attributes of the object.

        This method is intended to be called internally from describe()
        """
        pass
