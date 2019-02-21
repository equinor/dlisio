from . import core

class Objectpool():
    """ The Objectpool implements a pool of all metadata objects.

    Linking objects:
    Some objects have attributes that reference other object of different
    classes e.g. frames have a channels attribute. The on-disk representation
    of these attributes are meerly list of unique object names. dlisio resolves
    these object names an creates refrences to the python objects. However,
    dlisio assumes that there exist an object with that unique name on file.
    If not, that entry is silently dropped from the refrencing object
    attribute.

    Note that the attic attribute contains all object attributes as represented
    on disk. Dropped entries can be identified by simply comparing the the
    attribute from the python object with the corresponding attribute in attic

    Also note that for now dlisio only support read operarations, hence any
    user-modification of these objects is NOT reflected on-disk
    """
    def __init__(self, objects):
        self.objects = []
        self.index = 0

        for os in objects:
            for obj in os.objects:
                 if   os.type == "FRAME"   : obj = Frame(obj)
                 elif os.type == "CHANNEL" : obj = Channel(obj)
                 else: obj = Unknown(obj)
                 self.objects.append(obj)

        for obj in self.objects:
            self.link(obj)

    def __len__(self):
        """x.__len__() <==> len(x)"""
        return len(self.objects)

    def __repr__(self):
        return "Objectpool(objects =  {})".format(len(self))

    def link(self, obj):
        if obj.type == "channel":
            if obj.source is not None:
                for o in self.objects:
                    if o.name == obj.source.name: obj.source = o

        if obj.type == "frame":
            obj.channels = [r for r in self.channels if r.name in obj.channels]

    def getobject(self, name, type):
        """ return object corresponding to the unique identifier given by name + type

        Parameters
        ----------
        name : tuple or dlisio.core.obname
        type : str

        Returns
        -------
        obj : object

        Examples
        --------

        >>> name = ("TDEP", 2, 2)
        >>> obj = objects[name, "channel"]
        """

        n = (None, None, None)
        if isinstance(name, tuple):
            n = name

        if isinstance(name, core.obname):
            n = (name.id, name.origin, name.copynumber)

        for o in self.objects:
            if o.type != type            : continue
            if o.name.id != n[0]         : continue
            if o.name.origin != n[1]     : continue
            if o.name.copynumber != n[2] : continue
            return o

    @property
    def allobjects(self):
        """
        Returns a generator of all objects on file
        """
        return (o for o in self.objects)

    @property
    def channels(self):
        """Channel objects"""
        return (o for o in self.objects if o.type == "channel")

    @property
    def frames(self):
        """Frame objects"""
        return (o for o in self.objects if o.type == "frame")

    @property
    def unknowns(self):
        """Frame objects"""
        return (o for o in self.objects if o.type == "unknown")

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

class Channel(basic_object):
    """
    The Channel object reflects the logical record type CHANNEL (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.5.1 - Static and
    Frame Data, CHANNEL objects).
    """
    def __init__(self, obj):
        super().__init__(obj, "channel")
        self.long_name     = None
        self.reprc         = None
        self.units         = None
        self.properties    = []
        self.dimension     = []
        self.axis          = []
        self.element_limit = []
        self.source        = None

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "LONG-NAME"          : self.long_name     = attr.value[0]
            if attr.label == "REPRESENTATION-CODE": self.reprc         = attr.value[0]
            if attr.label == "UNITS"              : self.units         = attr.value[0]
            if attr.label == "PROPERTIES"         : self.properties    = attr.value
            if attr.label == "DIMENSION"          : self.dimension     = attr.value
            if attr.label == "AXIS"               : self.axis          = attr.value
            if attr.label == "ELEMENT-LIMIT"      : self.element_limit = attr.value
            if attr.label == "SOURCE"             : self.source        = attr.value[0]

    def hassource(self, obj):
        """
        Check if obj is the source of channel

        Parameters
        ----------
        obj : dlis.core.obname or any object class derived from basic_object

        Returns
        -------
        issource : bool
            True if obj is the source of channel, else False

        """
        if self.source is None: return False

        if isinstance(obj, core.obname): child = obj
        else : child = obj.name

        if isinstance(self.source, core.obname): parent = self.source
        else : parent = self.source.name

        return parent == child

class Frame(basic_object):
    """
    The Frame object reflects the logical record type FRAME (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.7.1 - Static and
    Frame Data, FRAME objects)
    """
    def __init__(self, obj):
        super().__init__(obj, "frame")
        self.description = None
        self.channels    = []
        self.index_type  = None
        self.direction   = None
        self.spacing     = None
        self.encrypted   = None
        self.index_min   = None
        self.index_max   = None

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "DESCRIPTION": self.description = attr.value[0]
            if attr.label == "CHANNELS"   : self.channels    = attr.value
            if attr.label == "INDEX-TYPE" : self.index_type  = attr.value[0]
            if attr.label == "DIRECTION"  : self.direction   = attr.value[0]
            if attr.label == "SPACING"    : self.spacing     = attr.value[0]
            if attr.label == "ENCRYPTED"  : self.encrypted   = attr.value[0]
            if attr.label == "INDEX-MIN"  : self.index_min   = attr.value[0]
            if attr.label == "INDEX-MAX"  : self.index_max   = attr.value[0]

    def haschannel(self, channel):
        """
        Return True if channels is in frame.channels,
        else return False

        Parameters
        ----------
        channel : dlis.core.obname or Channel object

        Returns
        -------
        haschannel : bool
            True if Frame has the channel obj, else False

        """
        if len(self.channels) == 0: return False

        if isinstance(channel, core.obname): child = channel
        else : child = channel.name

        for ch in self.channels:
            if isinstance(ch, core.obname):
                if ch == child: return True
            if isinstance(ch, Channel):
                if ch.name == child: return True
        return False

class Unknown(basic_object):
    """
    The unknown object implements a dict interface and is intended as a
    fall-back object if the object-type is not recognized by dlisio, e.g.
    vendor spesific object types
    """
    def __init__(self, obj):
        super().__init__(obj, "unknown")
        self.attributes = {a.label.lower() : a.value for a in obj.values()}
        self._stripspaces()

    def __getattr__(self, key):
        return self.attributes[key]

    def __str__(self):
        s  = "dlisio.unknown:\n"
        s += "\tname: {}\n".format(self.name)
        s += "\ttype: {}\n".format(self.type)
        for key, value in self.attributes.items():
            s += "\t{}: {}\n".format(key, value)
        s += "\tattic: {}\n".format(self.type)
        return s

    def _stripspaces(self):
        for key, value in self.attributes.items():
            if isinstance(value, str): self.attributes[key] = value.strip()
            if isinstance(value, list):
                for inx, v in enumerate(value):
                    if isinstance(v, str):
                        self.attributes[key][inx] = v.strip()
