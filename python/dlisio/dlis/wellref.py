from collections import OrderedDict

from .basicobject import BasicObject
from . import utils


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
        'PERMANENT-DATUM'           : utils.scalar,
        'VERTICAL-ZERO'             : utils.scalar,
        'PERMANENT-DATUM-ELEVATION' : utils.scalar,
        'ABOVE-PERMANENT-DATUM'     : utils.scalar,
        'MAGNETIC-DECLINATION'      : utils.scalar,
        'COORDINATE-1-NAME'         : utils.scalar,
        'COORDINATE-1-VALUE'        : utils.scalar,
        'COORDINATE-2-NAME'         : utils.scalar,
        'COORDINATE-2-VALUE'        : utils.scalar,
        'COORDINATE-3-NAME'         : utils.scalar,
        'COORDINATE-3-VALUE'        : utils.scalar,
    }


    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def permanent_datum(self):
        return self['PERMANENT-DATUM']

    @property
    def vertical_zero(self):
        return self['VERTICAL-ZERO']

    @property
    def permanent_datum_elevation(self):
        return self['PERMANENT-DATUM-ELEVATION']

    @property
    def above_permanent_datum(self):
        return self['ABOVE-PERMANENT-DATUM']

    @property
    def magnetic_declination(self):
        return self['MAGNETIC-DECLINATION']

    @property
    def coordinates(self):
        coordinates = {}
        custom_label = 'COORDINATE-{}'
        name = 'COORDINATE-{}-NAME'
        value = 'COORDINATE-{}-VALUE'

        for i in range(1, 4):
            try:
                key = self.attic[name.format(i)].value[0]
            except KeyError:
                key = custom_label.format(i)

            try:
                val = self.attic[value.format(i)].value[0]
            except KeyError:
                val = None

            coordinates[key] = val
        return coordinates

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Permanent datum']           =  'PERMANENT-DATUM'
        d['Vertical zero']             =  'VERTICAL-ZERO'
        d['Permanent datum elevation'] =  'PERMANENT-DATUM-ELEVATION'
        d['Above permanent datum']     =  'ABOVE-PERMANENT-DATUM'
        d['Magnetic declination']      =  'MAGNETIC-DECLINATION'

        utils.describe_attributes(buf, d, self, width, indent, exclude)

        # TODO: print units for coordinates
        # Postponed as wellref object hasn't been seen in real files
        utils.describe_header(buf, 'Coordinates', width, indent, lvl=2)
        utils.describe_dict(buf, self.coordinates, width, indent, exclude)
