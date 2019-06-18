from .. import core
from .valuetypes import *
from .linkage import link_attribute

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
        self.name       = None
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

        self._attribute_features = [link_attribute]

        try:
            self.name       = name.id
            self.origin     = int(name.origin)
            self.copynumber = int(name.copynumber)
        except AttributeError:
            pass

    def __repr__(self):
        return "dlisio.{}(id={}, origin={}, copynumber={})".format(
                self.type,
                self.name,
                self.origin,
                self.copynumber)

    def __str__(self):
        s  = "dlisio.{}:\n".format(self.type)
        for key, value in self.__dict__.items():
            s += "\t{}: {}\n".format(key, value)
        return s

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

        if self.attic is None: return

        attrs = self.attributes
        for label, value in self.attic.items():
            if value is None: continue

            try:
                attr, value_type = attrs[label]
            except KeyError:
                self.stash[label] = value
                continue

            val = vtvalue(value_type, value)

            for feature in self._attribute_features:
                if feature(self, attr, val): break
            else:
                setattr(self, attr, val)

        self.stripspaces()
