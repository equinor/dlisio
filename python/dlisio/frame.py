from .basicobject import BasicObject
from .reprc import fmt

import numpy as np


class Frame(BasicObject):
    """Frame-type

    A Frame is a horizontal segment of the log data, possibly containing multiple
    channels. A frame objects identifies all channels that are a part of each
    Frame, along with the type- and range of the index of the channels.
    Note that the index itself is also a channel object.

    Notes
    -----

    The Frame object reflects the logical record type FRAME, defined in rp66.
    FRAME objects are listed in Appendix A.2 - Logical Record Types, and
    described in detail in Chapter 5.7.1 - Static and Frame Data, FRAME
    objects.

    See also
    --------

    dlisio.Channel : Channel objects.
    """
    def __init__(self, obj = None):
        super().__init__(obj, "FRAME")
        self._description = None
        self.channel_refs = []
        self._channels    = []
        self._index_type  = None
        self._direction   = None
        self._spacing     = None
        self._encrypted   = False
        self._index_min   = None
        self._index_max   = None
        self._fmtstr      = ""
        self._dtype       = None

    @staticmethod
    def load(obj):
        self = Frame(obj)
        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "DESCRIPTION": self._description = attr.value[0]
            if attr.label == "CHANNELS"   : self.channel_refs = attr.value
            if attr.label == "INDEX-TYPE" : self._index_type  = attr.value[0]
            if attr.label == "DIRECTION"  : self._direction   = attr.value[0]
            if attr.label == "SPACING"    : self._spacing     = attr.value[0]
            if attr.label == "ENCRYPTED"  : self._encrypted   = True
            if attr.label == "INDEX-MIN"  : self._index_min   = attr.value[0]
            if attr.label == "INDEX-MAX"  : self._index_max   = attr.value[0]

        self.stripspaces()
        return self

    @property
    def dtype(self):
        """dtype

        data-type of each frame. I.e. the sum of channel.dtype of each channel
        in self.channels.

        See also
        --------

        dlisio.Channel.dtype : dtype of each sample in the channel's sample
        array.

        Returns
        -------

        dtype : np.dtype
        """
        if self._dtype: return self._dtype

        self._dtype = np.dtype([(ch.name.id, ch.dtype) for ch in self.channels])
        return self._dtype

    @property
    def description(self):
        """Description

        Textual description of the Frame.

        Returns
        -------

        description : str
        """
        return self._description

    @property
    def channels(self):
        """Channels

        List of all channels in the frame.

        Returns
        -------

        channels : list of Channel
        """
        return self._channels

    @property
    def index_type(self):
        """Index type

        The measurement of the index, e.g. borehole-depth, vertical depth,
        etc..

        Returns
        -------

        index_type : str
        """
        return self._index_type

    @property
    def direction(self):
        """Direction

        Specifies whether the index is increasing or decreasing.

        Notes
        -----

        The direction is also implicitly given by the sign of *Frame.spacing*
        (if present). If there is no index channel (*Frame.index_type* is None)
        the spacing attribute is meaningless.

        Returns
        -------

        direction : str
        """
        return self._direction

    @property
    def spacing(self):
        """Spacing

        Specifies a *constant* spacing of the index from one frame to the next.
        The value is the signed difference of the later minus the former index.
        If there is no index channel (*Frame.index_type* is None) the spacing
        attribute is meaningless.

        Notes
        -----

        The direction of the index is implicitly given by the sign of this
        attribute.


        Returns
        -------

        spacing : undefined
        """
        return self._spacing

    @property
    def encrypted(self):
        """Encrypted

        Specifies whether the data from this frame is encrypted or not.

        Returns
        -------

        encrypted : bool
        """
        return self._encrypted

    @property
    def index_min(self):
        """Index min

        The minimum value of index. If there is no index channel
        (*Frame.index_type* is None) the minimum index is set to 1.

        Returns
        -------

        index_min : undefined
        """
        return self._index_min

    @property
    def index_max(self):
        """Index max

        The maximum value of the index. If there is no index channel
        (*Frame.index_type* is None), the maximum index is set to number of
        frames in this frame-type.

        Returns
        -------

        index_max : undefined
        """
        return self._index_max

    def fmtstr(self):
        """Generate format-string for Frame

        Generate a format-string for this Frame. All frames of the same
        Frame-type have the same channels-list resulting in the same
        format-string for all frames of a given Frame-type.

        The format-string is mainly intended for internal use.

        Returns
        -------

        fmtstr : str
        """

        if self._fmtstr: return self._fmtstr

        for ch in self.channels:
            samples = np.prod(np.array(ch.dimension))
            reprc = fmt[ch.reprc]
            self._fmtstr += samples * reprc

        return self._fmtstr

    def link(self, objects, sets):
        self._channels = [
            sets['CHANNEL'][ref.fingerprint('CHANNEL')]
            for ref in self.channel_refs
        ]
