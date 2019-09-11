from .. import core
from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .linkage import obname, objref
from .utils import describe_dict

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
        'DESCRIPTION' : scalar('description'),
        'OBJECT-TYPE' : scalar('objecttype'),
        'OBJECT-LIST' : vector('objects'),
        'GROUP-LIST'  : vector('groups'),
    }

    linkage = {
        'objects' : objref,
        'groups'  : obname('GROUP'),

    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'GROUP')
        self.description = None
        self.objecttype  = None
        self.objects     = []
        self.groups      = []

        self.linkage = deepcopy(self.linkage)


    def link(self, objects):
        """
        Group.objects references other objects either by objref
        or by obname(self.objecttype). DLISIO assumes objref as default, but
        checks before linking and changes to obname(self.objecttype) if
        nessesary'
        """
        try:
            ref = self.refs['objects'][0]
        except KeyError:
            ref = None

        if isinstance(ref, core.obname):
            self.linkage['objects'] = obname(self.objecttype)

        super().link(objects)

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Description']  = self.description
        d['Object list']  = self.objects
        d['Group list']   = self.groups

        describe_dict(buf, d, width, indent, exclude)
