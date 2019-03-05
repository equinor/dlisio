from . import core

class basic_object():
    """
    Python representation of the set of logical record types (listed in
    Appendix A - Logical Record Types, described in Chapter 5 - Static and
    Frame Data)

    All object-types are derived from basic_object, but that is just a way of
    adding the object-name field which is present in every object, as well as
    specifying the object type. These two fields makes a unique indentifier for
    the object.

    The attribute attic is a copy of the object as represented on disk and is
    mainly inteded for debugging purpuses.
    """
    def __init__(self, obj, type):
        self.name = obj.name
        self.type = type
        self.attic = obj

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


    @staticmethod
    def contains(base, name):
        """ Check if base cotains obj

        Parameters:
        ----------
        base : list of dlis.core.obname or list of any object derived from
            basic_object, e.g. Channel, Frame

        obj : dlis.core.obname, tuple (str, int, int)

        Returns
        -------
        isin : bool
            True if obj or (name, type) is in base, else False

        Examples
        --------

        Check if "frame" contain channel:

        >>> ans = contains(frame.channels, obj=channel.name)

        Check if "frame" contains a channel with name:
        >>> name = ("TDEP", 2, 0)
        >>> ans = contains(frame.channels, name)

        find all frames that have "channel":

        >>> fr = [o for o in frames if contains(o.channels, obj=channel.name)]
        """
        child = None
        parents = None

        if isinstance(name, core.obname):
            child = (name.id, name.origin, name.copynumber)
        else:
            child = name
        try:
            parents = [(o.id, o.origin, o.copynumber) for o in base]
        except AttributeError:
            parents = [(o.name.id, o.name.origin, o.name.copynumber) for o in base]

        if any(child == p for p in parents): return True

        return False
