from .basicobject import BasicObject
from ..reprc import fmt

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
    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'FRAME')

        #: Textual description of the Frame.
        self.description = None

        #: References to the channels
        self.channel_refs = []

        #: Channels in the frame
        self.channels    = []

        #: The measurement of the index, e.g. borehole-depth
        self.index_type  = None

        #: Direction of the index (Increasing or decreasing)
        self.direction   = None

        #: Constant spacing in the index
        self.spacing     = None

        #: Encrypted frame
        self.encrypted   = False

        #: Minimum value of the index
        self.index_min   = None

        #: Maximum value of the index
        self.index_max   = None

        #: Format-string of the frame. Mainly indended for internal use
        self._fmtstr     = ""

        #: The data-type of the structured array that contains all samples
        #: arrays from all channels.
        self._dtype      = None

    @staticmethod
    def load(obj, name = None):
        self = Frame(obj, name = name)
        for label, value in obj.items():
            if value is None: continue

            if label == "DESCRIPTION": self.description = value[0]
            if label == "CHANNELS"   : self.channel_refs = value
            if label == "INDEX-TYPE" : self.index_type  = value[0]
            if label == "DIRECTION"  : self.direction   = value[0]
            if label == "SPACING"    : self.spacing     = value[0]
            if label == "ENCRYPTED"  : self.encrypted   = True
            if label == "INDEX-MIN"  : self.index_min   = value[0]
            if label == "INDEX-MAX"  : self.index_max   = value[0]

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

        self._dtype = np.dtype([(ch.name, ch.dtype) for ch in self.channels])
        return self._dtype

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

        if self._fmtstr != "" : return self._fmtstr

        for ch in self.channels:
            samples = np.prod(np.array(ch.dimension))
            reprc = fmt[ch.reprc]
            self._fmtstr += samples * reprc

        return self._fmtstr

    def link(self, objects, sets):
        self.channels = [
            sets['CHANNEL'][ref.fingerprint('CHANNEL')]
            for ref in self.channel_refs
        ]
