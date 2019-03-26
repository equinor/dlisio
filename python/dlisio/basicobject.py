from . import core

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
    def __init__(self, obj, type):
        self._name = obj.name
        self._type = type
        self._attic = obj

    def __repr__(self):
        return "dlisio.{}(id={}, origin={}, copynumber={})".format(
                self.type,
                self.name.id,
                self.name.origin,
                self.name.copynumber)

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
        fingerprint
        """
        return self.name.fingerprint(self.type)

    @property
    def name(self):
        """ Name

        Name is the main identifier for dlis-objects and consists of three
        subfields: id(str), origin(int) and copynumber(int).

        The name is required to be unique for all object of the same type
        (within a Logical File), e.g: Two channel objects cannot have the same
        name. However a channel object can have the same name as a frame
        object.

        Examples
        --------

        Access each individual field:

        >>> id  = Object.name.id
        >>> origin = Object.name.origin
        >>> copynr = Object.name.copynumber

        Returns
        -------

        name : dlis.core.obname
        """
        return self._name

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

    def stripspaces(self):
        """Strip spaces

        Remove leading and trailing withspaces for object attributes as they
        may be padded with whitespaces.
        """
        for key, value in self.__dict__.items():
            if isinstance(value, str):
                self.__dict__[key] = value.strip()
            if isinstance(value, list):
                if not isinstance(value, str): continue
                for inx, v in enumerate(value):
                    self.__dict__[key][inx] = v.strip()

    def link(self, objects, sets):
        """ Link objects

        The default implementation is a no-op - individual object types
        themselves are aware on how to link to other objects
        """
        pass
