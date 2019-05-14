from .. import core
from .valuetypes import *

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
    """

    attributes = {}
    """dict: Index of all the attributes this object is expected to have.
    DLISIO will use this index on object parsing. If an attribute is not in
    index, it will be ignored when parsing the file.
    If attributes list is to be updated manually for the class:

    >>> Coefficient.attributes['MY_PARAM'] = valuetypes.scalar('myparam')
    ... dlisio.load(fpath)

    All the Coefficient objects will map MY_PARAM from the source file
    to myparam. It's also possible to update attributes for one object
    only and reload afterwards:

    >>> coeff = f.objects[key]
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

    The values must be either *linkage.obname("TYPE")* or *linkage.objref*.
    To relink just one object (when refs or linkage is updated):

    >>> coeff.link(f.objects)
    """

    def __init__(self, obj, name = None, type = None):
        self._type      = type
        self.name       = None
        self.origin     = None
        self.copynumber = None
        self._attic     = obj

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

    @property
    def type(self):
        """ Type

        The type of the object. Together, the type- and name-attribute form a
        unique object-identifier across all objects in the Logical File

        Returns
        -------

        type : str
        """
        return self._type

    @property
    def attic(self):
        """ The original object as represented on disk

        Attic refers the underlying basic_object, which is a
        dict-representation of the data on disk. The attic can be None if this
        particular instance was not loaded from disk.

        Notes
        -----

        This attribute is mainly intended for debugging purpuses

        Returns
        -------

        attic : dl:basic_object
        """
        return self._attic

    def update_stash(self, label, value):
        """ Stashes attributes

        Adds provided label-value pair to stash dictionary.
        If value already exists in the dictionary, it's updated
        """
        self.stash[label] = value

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
                    if lnk:
                        links.append(lnk)
                setattr(self, attr, links)
            else:
                lnk = get_link(ref)
                setattr(self, attr, lnk)

    @classmethod
    def create(cls, obj, name = None, type = None):
        """ Create Python object of provided class and load values
        from native object

        This process is generalized for all object types derived from
        basic_object.
        """
        if type is None:
            self = cls(obj, name = name)
        else:
            self = cls(obj, name = name, type = type)

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

            try:
                attr, value_type = attrs[label]
            except KeyError:
                self.update_stash(label, value)
                continue

            val = vtvalue(value_type, value)

            if islink(value[0]):
                self.refs[attr] = val
            else:
                setattr(self, attr, val)

        self.stripspaces()
