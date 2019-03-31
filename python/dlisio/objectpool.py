from collections import defaultdict
import logging

from . import core
from .fileheader import Fileheader
from .origin import Origin
from .frame import Frame
from .channel import Channel
from .tool import Tool
from .parameter import Parameter
from .calibration import Calibration
from .unknown import Unknown

class Objectpool():
    """ The Objectpool implements a pool of all metadata objects.

    Notes
    -----

    For now dlisio only support read operarations, hence any
    user-modification of these objects is NOT reflected on-disk
    """
    def __init__(self):
        self.objects = {}
        self.object_sets = defaultdict(dict)
        self.problematic = []

        self.types = {
            'FILE-HEADER': Fileheader.load,
            'ORIGIN'     : Origin.load,
            'FRAME'      : Frame.load,
            'CHANNEL'    : Channel.load,
            'TOOL'       : Tool.load,
            'PARAMETER'  : Parameter.load,
            'CALIBRATION': Calibration.load,
        }

    def load(self, sets):
        """ Load and enrich raw objects into the object pool

        This method converts the raw object sets into first-class dlisio python
        objects, and puts them in the the objects, object_sets and problematic
        members.

        Parameters
        ----------
        sets : iterable of object_set

        Notes
        -----
        This is a part of the two-phase initialisation of the pool, and should
        rarely be called as an end user. This is primarily a mechanism for
        testing and prototyping for developers, and the occasional
        live-patching of features so that dlisio is useful, even when something
        in particular is not merged upstream.

        """
        problem = 'multiple distinct objects '
        where = 'in set {} ({}). Duplicate fingerprint = {}'
        action = 'continuing with the last object'
        duplicate = 'duplicate fingerprint {}'

        objects = {}
        object_sets = defaultdict(dict)
        problematic = []

        for os in sets:
            # TODO: handle replacement sets
            for o in os.objects:
                try:
                    obj = self.types[os.type](o)
                except KeyError:
                    obj = Unknown.load(o, type = os.type)

                fingerprint = obj.fingerprint
                if fingerprint in objects:
                    original = objects[fingerprint]

                    logging.info(duplicate.format(fingerprint))
                    if original.attic != obj.attic:
                        msg = problem + where
                        msg = msg.format(os.type, os.name, fingerprint)
                        logging.error(msg)
                        logging.warning(action)
                        problematic.append((original, obj))

                objects[fingerprint] = obj
                object_sets[obj.type][fingerprint] = obj

        for obj in objects.values():
            obj.link(objects, object_sets)

        self.objects = objects
        self.object_sets = object_sets
        self.problematic = problematic
        return self

    def __len__(self):
        """x.__len__() <==> len(x)"""
        return len(self.objects)

    def __repr__(self):
        return "Objectpool(objects =  {})".format(len(self))

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
        return self.objects.values()

    @property
    def fileheader(self):
        """Fileheader objects"""
        return self.object_sets['FILE-HEADER'].values()

    @property
    def origin(self):
        """Origin objects"""
        return self.object_sets['ORIGIN'].values()

    @property
    def channels(self):
        """Channel objects"""
        return self.object_sets['CHANNEL'].values()

    @property
    def frames(self):
        """Frame objects"""
        return self.object_sets['FRAME'].values()

    @property
    def tools(self):
        """Tool objects"""
        return self.object_sets['TOOL'].values()

    @property
    def parameters(self):
        """Parameter objects"""
        return self.object_sets['PARAMETER'].values()

    @property
    def calibrations(self):
        """Calibration objects"""
        return self.object_sets['CALIBRATION'].values()

    @property
    def unknowns(self):
        """Frame objects"""
        return (obj
            for typename, object_set in self.object_sets.items()
            for obj in object_set.values()
            if typename not in self.types
        )
