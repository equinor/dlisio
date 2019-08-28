from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .linkage import obname
from .utils import describe_dict, replist

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
        'FRAME-TYPE'           : scalar('frame'),
        'WELL-REFERENCE-POINT' : scalar('well_reference_point'),
        'VALUE'                : vector('value'),
        'BOREHOLE-DEPTH'       : scalar('borehole_depth'),
        'VERTICAL-DEPTH'       : scalar('vertical_depth'),
        'RADIAL-DRIFT'         : scalar('radial_drift'),
        'ANGULAR-DRIFT'        : scalar('angular_drift'),
        'TIME'                 : scalar('time'),
        'DEPTH-OFFSET'         : scalar('depth_offset'),
        'MEASURE-POINT-OFFSET' : scalar('measure_point_offset'),
        'TOOL-ZERO-OFFSET'     : scalar('tool_zero_offset')
    }

    linkage = {
        'borehole_depth'       : obname('CHANNEL'),
        'vertical_depth'       : obname('CHANNEL'),
        'radial_drift'         : obname('CHANNEL'),
        'angular_drift'        : obname('CHANNEL'),
        'time'                 : obname('CHANNEL'),
        'frame'                : obname('FRAME'),
        'well_reference_point' : obname('WELL-REFERENCE'),
        'value'                : obname('CHANNEL')
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'PATH')
        self.frame                = None
        self.well_reference_point = None
        self.value                = []
        self.borehole_depth       = None
        self.vertical_depth       = None
        self.radial_drift         = None
        self.angular_drift        = None
        self.time                 = None
        self.depth_offset         = None
        self.measure_point_offset = None
        self.tool_zero_offset     = None

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Frame']                = replist(self.frame, 'name')
        d['Well reference point'] = replist(self.well_reference_point, 'name')
        d['Value Channel(s)']     = replist(self.value, 'name')
        describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Borehole depth'] = self.borehole_depth
        d['Vertical depth'] = self.vertical_depth
        d['Radial drift']   = self.radial_drift
        d['Angular drift']  = self.angular_drift
        describe_dict(buf, d, width, indent, exclude)

        d = OrderedDict()
        d['Time']                 = self.time
        d['Depth offset']         = self.depth_offset
        d['Measure point offset'] = self.measure_point_offset
        d['Tool zero offset']     = self.tool_zero_offset
        describe_dict(buf, d, width, indent, exclude)
