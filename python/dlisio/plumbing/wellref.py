from .basicobject import BasicObject
from .valuetypes import scalar, dictentry, vtvalue


class Wellref(BasicObject):
    """
    Well reference defines origin of well with coordinates.

    Attributes
    ----------

    permanent_datum : str
        Permanent datum defines level from where vertical distance is measured

    vertical_zero : str
        Vertical zero is an entity that corresponds to zero depth.

    permanent_datum_elevation :
        Permanent datum, structure or entity from which the vertical distance
        can be measured.

    above_permanent_datum :
        Distance of permanent Datum above mean sea level. Negative values
        indicates that the Permanent datum is below mean sea level

    magnetic_declination :
        Magnetic Declination is  angle between  the line of direction to
        geographic north and the line of direction to magnetic north. This
        defines angle with vertex at well reference point.

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
        'COORDINATE-1-NAME'         : dictentry('coordinate'),
        'COORDINATE-1-VALUE'        : dictentry('coordinate'),
        'COORDINATE-2-NAME'         : dictentry('coordinate'),
        'COORDINATE-2-VALUE'        : dictentry('coordinate'),
        'COORDINATE-3-NAME'         : dictentry('coordinate'),
        'COORDINATE-3-VALUE'        : dictentry('coordinate'),
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
        buf = {
            'COORDINATE-1-NAME'  : 'coordinate1',
            'COORDINATE-1-VALUE' : None,
            'COORDINATE-2-NAME'  : 'coordinate2',
            'COORDINATE-2-VALUE' : None,
            'COORDINATE-3-NAME'  : 'coordinate3',
            'COORDINATE-3-VALUE' : None
        }
        attrs = self.attributes
        for label, value in self.attic.items():
            if value is None: continue

            try:
                attr, value_type = attrs[label]
            except KeyError:
                self.stash[label] = value
                continue

            val = vtvalue(value_type, value)

            if label in buf:
                buf[label] = val
            else:
                setattr(self, attr, val)

        coords = {
            buf['COORDINATE-1-NAME'] : buf['COORDINATE-1-VALUE'],
            buf['COORDINATE-2-NAME'] : buf['COORDINATE-2-VALUE'],
            buf['COORDINATE-3-NAME'] : buf['COORDINATE-3-VALUE']
        }

        self.coordinates = coords
        self.stripspaces()

