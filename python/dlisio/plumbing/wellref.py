from .basicobject import BasicObject
from .valuetypes import scalar, skip
from .utils import *

from collections import OrderedDict


class Wellref(BasicObject):
    """
    Well reference defines origin of well with coordinates.

    Attributes
    ----------

    permanent_datum : str
        Level from where vertical distance is measured

    vertical_zero : str
        Vertical zero is an entity that corresponds to zero depth.

    permanent_datum_elevation
        Permanent datum, structure or entity from which the vertical distance
        can be measured.

    above_permanent_datum
        Distance of permanent Datum above mean sea level. Negative values
        indicates that the Permanent datum is below mean sea level

    magnetic_declination
        Angle between  the line of direction to geographic north and the line
        of direction to magnetic north. This defines angle with vertex at well
        reference point.

    coordinate : dict
        Independent spatial coordinates. Typically, latitude, longitude and
        elevation

    See also
    --------

    BasicObject : The basic object that Wellref is derived from

    Notes
    -----

    The Well Reference  object reflects the well reference point of a well,
    defined in rp66. Well reference records are listed in Appendix A.2 -
    Logical Record Types are described in detail in Chapter 5.2.2 - Static and
    Frame Data, Well reference objects.
    """
    attributes = {
        'PERMANENT-DATUM'           : scalar('permanent_datum'),
        'VERTICAL-ZERO'             : scalar('vertical_zero'),
        'PERMANENT-DATUM-ELEVATION' : scalar('permanent_datum_elevation'),
        'ABOVE-PERMANENT-DATUM'     : scalar('above_permanent_datum'),
        'MAGNETIC-DECLINATION'      : scalar('magnetic_declination'),
        'COORDINATE-1-NAME'         : skip(),
        'COORDINATE-1-VALUE'        : skip(),
        'COORDINATE-2-NAME'         : skip(),
        'COORDINATE-2-VALUE'        : skip(),
        'COORDINATE-3-NAME'         : skip(),
        'COORDINATE-3-VALUE'        : skip(),
    }


    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'WELL-REFERENCE')
        self.permanent_datum           = None
        self.vertical_zero             = None
        self.permanent_datum_elevation = None
        self.above_permanent_datum     = None
        self.magnetic_declination      = None
        self.coordinates               = {}


    def load(self):
        super().load()

        self.coordinates = {}
        custom_label = 'COORDINATE-{}'
        name = 'COORDINATE-{}-NAME'
        value = 'COORDINATE-{}-VALUE'

        for i in range(1, 4):
            key = self.attic.get(name.format(i), [custom_label.format(i)])[0]
            val = self.attic.get(value.format(i), [None])[0]
            self.coordinates[key] = val

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Permanent datum']           =  self.permanent_datum
        d['Vertical zero']             =  self.vertical_zero
        d['Permanent datum elevation'] =  self.permanent_datum_elevation
        d['Above permanent datum']     =  self.above_permanent_datum
        d['Magnetic declination']      =  self.magnetic_declination

        describe_dict(buf, d, width, indent, exclude)

        describe_header(buf, 'Coordinates', width, indent, lvl=2)
        describe_dict(buf, self.coordinates, width, indent, exclude)
