
from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .linkage import obname


class Path(BasicObject):
    """
    Path Objects defines Channels in the Data Frames of a given Frame Type and
    are combined to define part or all of a Data Path, and variation in the
    alignment.


    Attributes
    ----------

    frame_type : Frame
        The frame in which the channel's of the current path are recorded.

    well_reference_point : Well Reference Point
        Well reference point reference the Object in the current Logical File
        that specifies the Well Reference Point for entities specified by the
        remaining Attributes of the Path Object.

    value : list of Channel
        Value Channel for the current Path.

    borehole_depth
        Specifies the constant Borehole Depth coordinate for the
        current Path, It may or may not be described by a channel object.

    vertical_depth
        Specifies the constant vertical depth coordinate for the
        current Path, It may or may not be described by a channel object.

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
        self.radial_drift         = None
        self.angular_drift        = None
        self.time                 = None
        self.depth_offset         = None
        self.measure_point_offset = None
        self.tool_zero_offset     = None
        self.vertical_depth       = None
