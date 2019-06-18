from .basicobject import BasicObject
from ..reprc import fmt
from ..dlisutils import curves
from .valuetypes import scalar, vector, boolean
from .linkage import obname
from .dataobjectutils import combined_dtype

import logging
import numpy as np


class Frame(BasicObject):
    """Frame-type

    A Frame is a horizontal segment of the log data, possibly containing multiple
    channels. A frame objects identifies all channels that are a part of each
    Frame, along with the type- and range of the index of the channels.
    Note that the index itself is also a channel object.

    Attributes
    ----------
    dtype_format : str
        The basic format string for duplicated mnemonics - this string is the
        default formatting for creating unique labels from the
        mnemonic-origin-copynumber triple in dtype.

    See also
    --------

    BasicObject : The basic object that Frame is derived from
    Channel     : Channel objects

    Notes
    -----

    The Frame object reflects the logical record type FRAME, defined in rp66.
    FRAME objects are listed in Appendix A.2 - Logical Record Types, and
    described in detail in Chapter 5.7.1 - Static and Frame Data, FRAME
    objects.
    """
    attributes = {
        'DESCRIPTION': scalar('description'),
        'CHANNELS'   : vector('channels'),
        'INDEX-TYPE' : scalar('index_type'),
        'DIRECTION'  : scalar('direction'),
        'SPACING'    : scalar('spacing'),
        'ENCRYPTED'  : boolean('encrypted'),
        'INDEX-MIN'  : scalar('index_min'),
        'INDEX-MAX'  : scalar('index_max')
    }

    linkage = {
        'channels' : obname("CHANNEL")
    }

    dtype_format = '{:s}.{:d}.{:d}'

    def __init__(self, obj = None, name = None, file = None):
        super().__init__(obj, name = name, type = 'FRAME')

        self.file        = file

        #: Textual description of the Frame.
        self.description = None

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

        #: Instance-specific dtype label formatter on duplicated mnemonics.
        #: Defaults to Frame.dtype_format
        self.dtype_fmt = self.dtype_format

    @classmethod
    def create(cls, obj, name = None, type = None, file = None):
        self = Frame(obj, name = name, file = file)
        self.load()
        return self

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
        ('TIME.0.0', 'TDEP', 'TIME.1.0').

        Duplicated mnemonics are formatted by the dtype_fmt attribute. To use a
        custom format for a specific frame instance, set dtype_fmt for the
        Frame object. If you want to have some other formatting for *all*
        dtypes, set the dtype_format class attribute. It has to be a 3-element
        format-string taking a string and two ints. Custom formatting is
        particularly useful for peculiar files where the full stop (.) appears
        in the mnemonic itself, and a consistent way of parsing origin and
        copynumber are needed.

        Returns
        -------

        dtype : np.dtype

        Examples
        --------

        A frame with two TIME channels:

        >>> frame.dtype
        dtype([('TIME.0.0', '<f4'), ('TDEP', '<i2'), ('TIME.1.0', '<i2')])

        Override instance-specific mnemonic formatting

        >>> frame.dtype
        dtype([('TIME.0.0', '<f4'), ('TDEP', '<i2'), ('TIME.1.0', '<i2')])
        >>> frame.dtype_fmt = '{:s}-{:d}-{:d}'
        >>> frame.dtype
        dtype([('TIME-0-0', '<f4'), ('TDEP', '<i2'), ('TIME-1-0', '<i2')])
        """
        if self._dtype:
            return self._dtype
        parts = [(ch, ch.dtype) for ch in self.channels]
        self._dtype = combined_dtype(parts, self.dtype_fmt.format)
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
            self._fmtstr += ch.fmtstr()

        return self._fmtstr

    def curves(self):
        """
        Reads curves for the frame.

        Examples
        --------
        Read curves from the frame and show curves from CHANN1 and CHANN2

        >>> curves = frame.curves()
        >>> curves["CHANN1"]
        array([1.1, 2.2, 3.3])
        >>> curves["CHANN2"]
        array([6.6, 7.7, 8.8])

        Read curves from the frame, show curves from MULTI_D_CHANNEL

        >>> curves = frame.curves()
        >>> curves["MULTI_D_CHANNEL"]
        array([[[  1,  2,  3],
                [  4,  5,  6]],
               [[  7,  8,  9],
                [ 10, 11,  12]]])

        Show only second sample

        >>> curves["MULTI_D_CHANNEL"][1]
        array([[  7,  8,  9],
               [ 10, 11, 12]])

        Returns
        -------
        curves : np.array

        """
        return curves(self.file, self, self.dtype, "", self.fmtstr(), "")

    def fmtstrchannel(self, channel):
        """Generate format-strings for one Frame channel

        To access the data of one channel only we still need to know its
        position in the frame. Method will generate format strings for
        data preceding channel data, for channel data and remaining data.

        The format-strings are mainly intended for internal use.

        Returns
        -------
        pre_fmt, ch_fmt, post_fmt : str, str, str
        """
        fmt = ""
        for ch in self.channels:
            fmtstr = ch.fmtstr()
            if ch == channel:
                pre_fmt = fmt
                ch_fmt = fmtstr
                fmt = ""
            else:
                fmt += fmtstr
        post_fmt = fmt

        return pre_fmt, ch_fmt, post_fmt

    def link(self, objects):
        super().link(objects)
        for ch in self.channels:
            try:
                if ch.frame:
                    msg = ("Frame {} contract is broken. "
                           "Channel {} already belongs to frame {}. "
                           "Assigning a new one")
                    logging.warn(msg.format(self.fingerprint,
                                 ch.fingerprint, ch.frame.fingerprint))
                ch.frame = self
            except AttributeError:
                #happens if ch has been parsed as other type
                pass
