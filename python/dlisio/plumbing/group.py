from .. import core
from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .linkage import obname, objref
from .describe import describe_dict

from collections import OrderedDict
from copy import deepcopy

class Group(BasicObject):
    """
    Group Objects indicate logical groupings of other Objects. A Group is
    defined by the producer by any associations deemed useful.

    Attributes
    ----------

    description : str

    object_type  : str
        Specifies the type of object that is referenced in the object list
        attribute.

    object_list : list
        References to arbitrary objects.

    group_list : list(Group)
        Reference to other Group objects

    Notes
    -----

    The Group object reflects the logical record type Group, defined in
    rp66. Group records are listed in Appendix A.2 - Logical Record Types and
    described in detail in Chapter 5.8.8 - Static and Frame Data, Group
    objects.
    """
    attributes = {
        'DESCRIPTION' : scalar,
        'OBJECT-TYPE' : scalar,
        'OBJECT-LIST' : vector,
        'GROUP-LIST'  : vector,
    }

    linkage = {
        'OBJECT-LIST' : objref,
        'GROUP-LIST'  : obname('GROUP'),

    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)
        self.linkage = deepcopy(self.linkage)

    @property
    def description(self):
        return self['DESCRIPTION']

    @property
    def objecttype(self):
        return self['OBJECT-TYPE']

    @property
    def objects(self):
        try:
            ref = self.attic['OBJECT-LIST'].value[0]
        except (KeyError, IndexError):
            return []

        if isinstance(ref, core.obname):
            self.linkage['OBJECT-LIST'] = obname(self.objecttype)

        return self['OBJECT-LIST']

    @property
    def groups(self):
        return self['GROUP-LIST']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Description']  = self.description
        d['Object list']  = self.objects
        d['Group list']   = self.groups

        describe_dict(buf, d, width, indent, exclude)
