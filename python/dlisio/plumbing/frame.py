from .basicobject import BasicObject
from ..reprc import fmt
from .valuetypes import scalar, vector, boolean

import numpy as np
import logging


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
    attributes = {
        'DESCRIPTION': scalar('description'),
        'CHANNELS'   : vector('channel_refs'),
        'INDEX-TYPE' : scalar('index_type'),
        'DIRECTION'  : scalar('direction'),
        'SPACING'    : scalar('spacing'),
        'ENCRYPTED'  : boolean('encrypted'),
        'INDEX-MIN'  : scalar('index_min'),
        'INDEX-MAX'  : scalar('index_max')
    }

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

    @property
    def dtype(self):
        """dtype

        data-type of each frame. I.e. the sum of channel.dtype of each channel
        in self.channels.

        If all curve mnemonics are unique, then dtype.names == [ch.name for ch
        in self.channels]. If there are more than one channel with the same
        name for this frame, all duplicated mnemonics are enriched with origin
        and copynumber.

        Consider a frame with the channels mnemonics [('TIME', 0, 0), ('TDEP',
        0, 0), ('TIME, 1, 0)]. The dtype names for this frame would be
        ('TIME:0:0', 'TDEP', 'TIME:1:0').

        See also
        --------

        dlisio.Channel.dtype : dtype of each sample in the channel's sample
        array.

        Returns
        -------

        dtype : np.dtype
        """
        if self._dtype: return self._dtype

        seen = {}
        types = []

        source = "duplicated mnemonic in frame '{}'"
        problem = "but rich label for channel '{}' cannot be formatted"
        msg = ', '.join((source, problem))
        info = 'name = {}, origin = {}, copynumber = {}'.format

        fmtlabel = '{:s}:{:d}:{:d}'.format
        for i, ch in enumerate(self.channels):
            # current has to be a list (or something mutable at least), because
            # it have to be updated on multiple labes
            current = (ch.name, ch.dtype)

            # first time for this label, register it as "seen before"
            if ch.name not in seen:
                seen[ch.name] = (i, ch)
                types.append(current)
                continue

            try:
                label = fmtlabel(ch.name, ch.origin, ch.copynumber)
            except (TypeError, ValueError):
                logging.error(msg.format(self.name, ch.name))
                logging.debug(info(ch.name, ch.origin, ch.copynumber))
                raise

            types.append((label, ch.dtype))

            # the first-seen curve with this name has already been updated
            if seen[ch.name] is None:
                continue

            prev_index, prev = seen[ch.name]

            try:
                label = fmtlabel(prev.name, prev.origin, prev.copynumber)
            except (TypeError, ValueError):
                logging.error(msg.format(self.name, ch.name))
                logging.debug(info(prev.name, prev.origin, prev.copynumber))
                raise

            # update the previous label with this name, and mark (with None)
            # for not needing update again
            types[prev_index] = (label, prev.dtype)
            seen[ch.name] = None

        self._dtype = np.dtype(types)
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
