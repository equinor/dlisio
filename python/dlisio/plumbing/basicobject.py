from .. import core
from .valuetypes import *
from .utils import *

import logging

class BasicObject():
    """Basic object
    Python representation of the set of logical record types (listed in
    Appendix A - Logical Record Types, described in Chapter 5 - Static and
    Frame Data)

    All object-types are derived from BasicObject, but that is just a way of
    adding the object-name field which is present in every object, as well as
    specifying the object type. These two fields makes a unique indentifier for
    the object.

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

    stash : dict_like
        Dictionary with all attributes not specified in
        :py:attr:`~attributes`.

    """

    attributes = {}
    """dict: Index of all the attributes this object is expected to have.
    DLISIO will use this index on object parsing. If an attribute is not in
    index, it will be ignored when parsing the file.
    If attributes list is to be updated manually for the class:

    >>> Coefficient.attributes['MY_PARAM'] = valuetypes.scalar('myparam')
    ... dlisio.load(fpath)

    All the Coefficient objects will map MY_PARAM from the source file
    to myparam. Updating object instance attributes will actually update
    attributes for the whole class

    >>> coeff = f.objects[key]
    ... coeff['MY_PARAM'] = valuetypes.scalar('myparam')

    In order to update attributes only for one particular object, redefine
    the attributes dictionary for the object and reload

    >>> coeff.attributes = dict(coeff.attributes)
    ... coeff.attributes['UNIQUE_PARAM'] = valuetypes.scalar('uniqueparam')
    ... coeff.load()

    Values for the dictionary are valuetypes:

    + *scalar* 1 value
    + *vector* list of values
    + *reverse* list of values will be reversed
    + *skip* skip the value on object parsing. Custom action might be
      performed later

    """

    linkage    = {}
    """dict: Linkage defines the rules for how each attribute links to other
    objects.
    During load stage all the objects of obname, objref and attref types
    are put into refs. During link stage they are linked to actually
    loaded objects based on information provided in linkage.
    If linkage is to be updated manually for the class:

    >>> Coefficient.linkage['myparam'] = linkage.obname("PARAMETER")
    ... dlisio.load(fpath)

    or

    >>> coeff = f.objects[key]
    ... ceoff.linkage['myparam'] = linkage.obname("PARAMETER")

    The values must be either *linkage.obname("TYPE")* or *linkage.objref*.
    To update linkage for one object only redefine linkage:

    >>> coeff.linkage = dict(coeff.linkage)
    ... ceoff.linkage['myparam'] = linkage.obname("PARAMETER")

    To relink (when refs or linkage is updated):

    >>> coeff.link(f.objects)
    """

    def __init__(self, obj, name = None, type = None):
        self.type       = type
        self.name       = name
        self.origin     = None
        self.copynumber = None
        self.attic      = obj

        #: Dictionary with all unexpected attributes.
        #: While all expected attributes are presented as members of object
        #: class, attributes not mentioned in specification are put into stash
        self.stash      = {}

        #: References to linked objects.
        #: Keeps originally stored value references to objects (obname, objref,
        #: attref) in the form of dictionary (expected attribute name : value)
        self.refs       = {}

        try:
            self.name       = name.id
            self.origin     = int(name.origin)
            self.copynumber = int(name.copynumber)
        except AttributeError:
            pass

    def __repr__(self):
        """Return a string representation of the object"""
        return '{}({})'.format(self.type.capitalize(), self.name)

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
        return core.fingerprint(self.type,
                                self.name,
                                self.origin,
                                self.copynumber)

    def stripspaces(self):
        """Strip spaces

        Remove leading and trailing withspaces for object attributes as they
        may be padded with whitespaces.
        """

        def strip(d):
            for key, value in d.items():
                if isinstance(value, str):
                    d[key] = value.strip()
                elif isinstance(value, list):
                    for inx, v in enumerate(value):
                        if isinstance(v, str):
                            d[key][inx] = v.strip()

        strip(self.__dict__)
        strip(self.stash)

    def link(self, objects):
        """ Link objects

        Iterate through values in refs and link objects based on
        provided linkage
        """

        linkage = self.linkage

        for attr, link in linkage.items():
            try:
                ref = self.refs[attr]
            except KeyError:
                continue

            if ref is None: continue

            def get_link(v):
                try:
                    fp = link(v)
                except (AttributeError, TypeError):
                    msg = ('wrong linkage for attribute \'{}\' of object {} of '
                           'class {}: can\'t  link object \'{}\' with expected '
                           'linkage type \'{}\'. Make sure linkage contains '
                           'references only to linkable objects and object is a'
                           ' link of expected type')
                    logging.warning(msg.format(attr, self.name,
                                               self.__class__, v, link))
                    return None

                try:
                    return objects[fp]
                except KeyError:
                    msg = ('missing attribute \'{}\' {} referenced from object '
                           '{} of class {}')
                    logging.warning(msg.format(attr, v, self.name,
                                               self.__class__))
                    return None

            if isinstance(ref, list):
                links = []
                for v in ref:
                    lnk = get_link(v)
                    links.append(lnk)
                setattr(self, attr, links)
            else:
                lnk = get_link(ref)
                setattr(self, attr, lnk)

    @classmethod
    def create(cls, obj, name = None, type = None, file = None):
        """ Create Python object of provided class and load values
        from native object

        This process is generalized for most of the types derived from
        basic_object.
        """
        self = cls(obj, name = name)
        self.load()
        return self

    def load(self):
        """Populate the Python object with values from the native c++ object.

        This is achieved by looping over the Python class' attribute list
        (which maps the native c++ attribute names to the attribute names in the
        Python class) and extracting the value(s). Essensially, this is whats
        going on:

        >>> for label, value in obj.items():
        ...     if label == 'LONG-NAME': self.long_name = value
        ...     if label == 'CHANNEL'  : self.channel   = value

        For labels which are not present in attribute list, instance stash
        is updated
        """

        def islink(val):
            # TODO: update to check repcode when repcode is back
            return (isinstance (val, core.obname) or
                    isinstance (val, core.objref) or
                    isinstance (val, core.attref))

        attrs = self.attributes
        for label, value in self.attic.items():
            if value is None: continue
            if len(value) == 0: continue

            try:
                attr, value_type = attrs[label]
            except KeyError:
                self.stash[label] = value
                continue

            if value_type == ValueTypeSkip:
                continue

            val = vtvalue(value_type, value, label, self)

            if islink(value[0]):
                self.refs[attr] = val
            else:
                setattr(self, attr, val)

        self.stripspaces()

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

        The exclude parameter gives the option to ommit parts of the summary.
        The table below states the different modes available.

        ====== ==========================================
        option Description
        ====== ==========================================
        'h'    header
        'a'    known attributes
        's'    attributes from stash                  [1]
        'i'    attributes that violates the standard  [2]
        'e'    attributes with empty values (default) [3]
        'r'    attributes from refs (default)         [4]
        ====== ==========================================

        [1] Stash contains attributes that are unknown to dlisio
        [2] Only applicable to attributes that should be interpreted in a
        specific way, such as Parameter.values. If not applicable, it is
        ignored.
        [3] Do not print attributes that have no value.
        [4] refs is a dict of attributes that contains references to other
        objects. If found, dlisio populates attributes with the objects
        corresponding to the references. The original reference, as represented
        on disk, can be accessed through the refs attribute.
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
                describe_dict(buf, self.stash, width, indent, exclude)

        if not exclude['refs']:
            if len(self.refs) > 0:
                describe_header(buf, 'References', width, indent, lvl=2)
                describe_dict(buf, self.refs, width, indent, exclude)

        return Summary(info=buf.getvalue())

    def describe_attr(self, buf, width, indent, exclude):
        """Describe the attributes of the object.

        This method is intended to be called internally from describe()
        """
        pass
