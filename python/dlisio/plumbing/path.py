from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .linkage import obname
from .describe import describe_dict, describe_attributes, replist

from collections import OrderedDict


class Path(BasicObject):
    """
    Path Objects defines Channels in the Data Frames of a given Frame Type and
    are combined to define part or all of a Data Path, and variation in the
    alignment.

    Attributes
    ----------

    frame_type : Frame
        The frame in which the channel's of the current path are recorded.

    well_reference_point : Wellref
        Well Reference Point

    value : list(Channel)
        Value Channel for the current Path.

    borehole_depth
        Specifies the constant Borehole Depth coordinate for the
        current Path, It may or may not be described by a channel object.

    vertical_depth
        Specifies the constant Vertical Depth coordinate for the
        current Path, It may or may not be described by a channel object.

    radial_drift
        Specifies the constant Radial Drift coordinate for the
        current Path, It may or may not be described by a channel object.

    angular_drift
        Specifies the constant Angular Drift coordinate for the
        current Path, It may or may not be described by a channel object.

    time
        Specifies the constant Time coordinate for the
        current Path, It may or may not be described by a channel object.
        |crtime|

    depth_offset
        Specifies the Depth Offset, which indicates how much the *value*
        is "off depth".

    measure_point_offset
        Specifies a Measure Point Offset, which indicates a fixed distance
        along Borehole Depth from the Value Channel’s Measure Point to a
        Data Reference Point.

    tool_zero_offset
        Distance of the Data Reference Point for the current Path above
        the tool string’s Tool Zero Point.


    See also
    --------

    BasicObject : The basic object that Parameter is derived from

    Notes
    -----

    The Path object reflects the logical record type PATH, defined in
    rp66. PATH records are listed in Appendix A.2 - Logical Record Types and
    described in detail in Chapter 5.7.2 - Static and Frame Data, PATH
    objects.

    """
    attributes = {
        'FRAME-TYPE'           : scalar,
        'WELL-REFERENCE-POINT' : scalar,
        'VALUE'                : vector,
        'BOREHOLE-DEPTH'       : scalar,
        'VERTICAL-DEPTH'       : scalar,
        'RADIAL-DRIFT'         : scalar,
        'ANGULAR-DRIFT'        : scalar,
        'TIME'                 : scalar,
        'DEPTH-OFFSET'         : scalar,
        'MEASURE-POINT-OFFSET' : scalar,
        'TOOL-ZERO-OFFSET'     : scalar,
    }

    linkage = {
        'BOREHOLE-DEPTH'       : obname('CHANNEL'),
        'VERTICAL-DEPTH'       : obname('CHANNEL'),
        'RADIAL-DRIFT'         : obname('CHANNEL'),
        'ANGULAR-DRIFT'        : obname('CHANNEL'),
        'TIME'                 : obname('CHANNEL'),
        'FRAME-TYPE'           : obname('FRAME'),
        'WELL-REFERENCE-POINT' : obname('WELL-REFERENCE'),
        'VALUE'                : obname('CHANNEL')
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def frame(self):
        return self['FRAME-TYPE']

    @property
    def well_reference_point(self):
        return self['WELL-REFERENCE-POINT']

    @property
    def value(self):
        return self['VALUE']

    @property
    def borehole_depth(self):
        return self['BOREHOLE-DEPTH']

    @property
    def vertical_depth(self):
        return self['VERTICAL-DEPTH']

    @property
    def radial_drift(self):
        return self['RADIAL-DRIFT']

    @property
    def angular_drift(self):
        return self['ANGULAR-DRIFT']

    @property
    def time(self):
        return self['TIME']

    @property
    def depth_offset(self):
        return self['DEPTH-OFFSET']

    @property
    def measure_point_offset(self):
        return self['MEASURE-POINT-OFFSET']

    @property
    def tool_zero_offset(self):
        return self['TOOL-ZERO-OFFSET']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Frame']                = self.frame
        d['Well reference point'] = self.well_reference_point
        d['Value Channel(s)']     = replist(self.value, 'name')
        describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Borehole depth'] = 'BOREHOLE-DEPTH'
        d['Vertical depth'] = 'VERTICAL-DEPTH'
        d['Radial drift']   = 'RADIAL-DRIFT'
        d['Angular drift']  = 'ANGULAR-DRIFT'
        describe_attributes(buf, d, self, width, indent, exclude)

        d = OrderedDict()
        d['Time']                 = 'TIME'
        d['Depth offset']         = 'DEPTH-OFFSET'
        d['Measure point offset'] = 'MEASURE-POINT-OFFSET'
        d['Tool zero offset']     = 'TOOL-ZERO-OFFSET'
        describe_attributes(buf, d, self, width, indent, exclude)
