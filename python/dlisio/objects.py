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
                 if   os.type == "FRAME"       : obj = Frame(obj)
                 elif os.type == "CHANNEL"     : obj = Channel(obj)
                 elif os.type == "TOOL"        : obj = Tool(obj)
                 elif os.type == "PARAMETER"   : obj = Parameter(obj)
                 elif os.type == "CALIBRATION" : obj = Calibration(obj)
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
            obj.channels = [o for o in self.channels if obj.haschannel(o.name)]

        if obj.type == "tool":
            obj.channels = [o for o in self.channels if obj.haschannel(o.name)]
            obj.parameters = [o for o in self.parameters if obj.hasparameter(o.name)]

        if obj.type == "calibration":
            obj.uncal_ch = [o for o in self.channels if obj.hasuncalibrated_channel(o.name)]
            obj.cal_ch = [o for o in self.channels if obj.hascalibrated_channel(o.name)]
            obj.parameters = [o for o in self.parameters if obj.hasparameter(o.name)]

    def getobject(self, name, type):
        """ return object corresponding to the unique identifier given by name + type

        Parameters
        ----------
        name : tuple(str, int, int) or dlisio.core.obname
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
    def tools(self):
        """Tool objects"""
        return (o for o in self.objects if o.type == "tool")

    @property
    def parameters(self):
        """Parameter objects"""
        return (o for o in self.objects if o.type == "parameter")

    @property
    def calibrations(self):
        """Calibration objects"""
        return (o for o in self.objects if o.type == "calibration")

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
        obj : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        issource : bool
            True if obj is the source of channel, else False

        """
        return self.contains(self.source, obj)

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
        channel : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        haschannel : bool
            True if Frame has the channel obj, else False

        """
        return self.contains(self.channels, channel)

class Tool(basic_object):
    """
    The tool object reflects the logical record type TOOL (listed in Appendix
    A.2 - Logical Record Types, described in Chapter 5.8.4 - Static and Frame
    Data, TOOL objects)
    """
    def __init__(self, obj):
        super().__init__(obj, "tool")
        self.description    = None
        self.trademark_name = None
        self.generic_name   = None
        self.status         = None
        self.parts          = []
        self.channels       = []
        self.parameters     = []

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "DESCRIPTION"    : self.description    = attr.value[0]
            if attr.label == "TRADEMARK-NAME" : self.trademark_name = attr.value[0]
            if attr.label == "GENERIC-NAME"   : self.generic_name   = attr.value[0]
            if attr.label == "STATUS"         : self.status         = attr.value[0]
            if attr.label == "PARTS"          : self.parts          = attr.value
            if attr.label == "CHANNELS"       : self.channels       = attr.value
            if attr.label == "PARAMETERS"     : self.parameters     = attr.value

    def haschannel(self, channel):
        """
        Return True if channels is in tool.channels,
        else return False

        Parameters
        ----------
        channel : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        haschannel : bool
            True if Tool has the channel obj, else False

        """
        return self.contains(self.channels, channel)

    def hasparameter(self, param):
        """
        Return True if param is in tool.parameters,
        else return False

        Parameters
        ----------
        param : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        hasparam : bool
            True if Tool has the parameter obj, else False

        """
        return self.contains(self.parameters, param)


class Parameter(basic_object):
    """
    The Parameter object reflects the logical record type PARAMETER (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.8.2 - Static
    and Frame Data, PARAMETER objects)
    """
    def __init__(self, obj):
        super().__init__(obj, "parameter")
        self.long_name   = None
        self.dimension   = None
        self.axis        = None
        self.zones       = None
        self.values      = None

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "LONG-NAME" : self.long_name = attr.value[0]
            if attr.label == "DIMENSION" : self.dimension = attr.value
            if attr.label == "AXIS"      : self.axis      = attr.value
            if attr.label == "ZONES"     : self.zones     = attr.value

class Calibration(basic_object):
    """
    The Calibration reflects the logical record type CALIBRATION (listed in
    Appendix A.2 - Logical Record Types, described in Chapter 5.8.7.3 - Static and
    Frame Data, CALIBRATION objects)

    The calibrated_channels and uncalibrated_channels attributes are lists of
    refrences to Channel objects.
    """
    def __init__(self, obj):
        super().__init__(obj, "calibration")
        self.method               = None
        self.calibrated_channel   = []
        self.uncalibrated_channel = []
        self.coefficients         = []
        self.parameters           = []

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "METHOD":
                self.method = attr.value[0]
            if attr.label == "CALIBRATED-CHANNELS":
                self.calibrated_channel = attr.value
            if attr.label == "UNCALIBRATED-CHANNELS":
                self.uncalibrated_channel = attr.value
            if attr.label == "COEFFICIENTS":
                self.coefficients = attr.value
            if attr.label == "PARAMETERS":
                self.parameters = attr.value

    def hasuncalibrated_channel(self, channel):
        """
        Return True if channels is in Calibration.uncal_ch,
        else return False

        Parameters
        ----------
        channel : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        hasuncalchannel : bool
            True if Calibration has the channel obj in uncal_ch, else False

        """
        return self.contains(self.uncalibrated_channel, channel)

    def hascalibrated_channel(self, channel):
        """
        Return True if channels is in Calibration.cal_ch,
        else return False

        Parameters
        ----------
        channel : dlis.core.obname or tuple(str, int, int)

        Returns
        -------
        hasuncalchannel : bool
            True if Calibration has the channel obj in self.cal_ch, else False

        """
        return self.contains(self.calibrated_channel, channel)

    def hasparameter(self, param):
        """
        Return True if parameter is in calibration.parameter,
        else return False

        Parameters
        ----------
        param : dlis.core.obname, tuple(str, int, int)

        Returns
        -------
        hasparameter : bool
            True if Calibration has the param obj, else False

        """
        return self.contains(self.parameters, param)

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
