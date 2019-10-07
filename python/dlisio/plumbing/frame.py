from .basicobject import BasicObject
from ..dlisutils import curves
from .valuetypes import scalar, vector, boolean
from .linkage import obname
from .utils import *

import numpy as np
import logging


class Frame(BasicObject):
    """Frame

    A Frame is a logical gathering of multiple Channels (curves), typically
    Channels from the same run.  A Frame containing three Channels would look
    something like this::

           TDEP     AIBK    TENS_SL
          -------  -------  -------
          |          |           |
           |          |         |
            |         |        |
             |       |        |
              |       |       |
               |     |         |

    Usually, the first channel in the channel list is considered to be the
    index-channel of the Frame. See:attr:`index_type` for more information
    about the index channels.

    All Channels belonging to a Frame are directly accessible through
    :attr:`channels`.  A full table of all the curve-data can be accessed with
    :attr:`curves`.

    Attributes
    ----------

    description : str
        Textual description of the Frame.

    channels : list(Channel)
        Channels in the frame

    index_type : str
        The measurement of the index, e.g. borehole-depth. If **not** None, the
        first channel is considered to be an index channel. If index_type is
        None, then the Frame has no index channel and is implicitly indexed by
        samplenumber i.e. 0, 1, ..., n.

    direction : str
        Direction of the index (Increasing or decreasing)

    spacing
        Constant spacing in the index

    index_min
        Minimum value of the index

    index_max
        Maximum value of the index

    encrypted : bool
        If the frame was encrypted

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

        self.description = None
        self.channels    = []
        self.index_type  = None
        self.direction   = None
        self.spacing     = None
        self.encrypted   = False
        self.index_min   = None
        self.index_max   = None

        # Format-string of the frame. Mainly indended for internal use
        self._fmtstr     = ""

        # The data-type of the structured array that contains all samples
        # arrays from all channels.
        self._dtype      = None

        # Instance-specific dtype label formatter on duplicated mnemonics.
        # Defaults to Frame.dtype_format
        self.dtype_fmt = self.dtype_format

    @property
    def index(self):
        """The Channel that serves as an index for all other Channels in this
        Frame.

        Frames may or may not have an index Channel, see :attr:`index_type` for
        definition of existing index channel.

        Returns
        -------
        channel : Channel or None
        """
        msg = 'There is no index channel, see help(frame.index) for more info'
        index = None

        if self.index_type is None:
            logging.warning(msg)
            return index

        try:
            index = self.channels[0]
        except IndexError:
            logging.warning(msg)

        return index

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

        if self._dtype: return self._dtype

        seen = {}
        types = []

        duplerr = "duplicated mnemonics in frame '{}': {}"
        fmterr = "rich label for channel '{}' cannot be formatted in frame '{}'"
        info = 'name = {}, origin = {}, copynumber = {}'.format

        fmtlabel = self.dtype_fmt.format
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
            except (IndexError, ValueError):
                logging.error(fmterr.format(ch.name, self.name))
                logging.debug(info(ch.name, ch.origin, ch.copynumber))
                raise

            types.append((label, ch.dtype))

            # the first-seen curve with this name has already been updated
            if seen[ch.name] is None:
                continue

            prev_index, prev = seen[ch.name]

            try:
                label = fmtlabel(prev.name, prev.origin, prev.copynumber)
            except (IndexError, ValueError):
                logging.error(fmterr.format(ch.name, self.name))
                logging.debug(info(prev.name, prev.origin, prev.copynumber))
                raise

            # update the previous label with this name, and mark (with None)
            # for not needing update again
            types[prev_index] = (label, prev.dtype)
            seen[ch.name] = None

        try:
            self._dtype = np.dtype(types)
        except ValueError as exc:
            logging.error(duplerr.format(self.name, exc))
            raise

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
        Returns a structured numpy array of all the curves

        Examples
        --------

        The returned array supports both horizontal- and vertical slicing.
        Do a vertical slice by specifying a single Channel

        >>> curves = frame.curves()
        >>> curves['CHANN1']
        array([16677259., 852606., 16678259., 852606.])

        Access a subset of Channels, note the double-bracket syntax

        >>> curves[['CHANN2', 'CHANN3']]
        array([
            (16677259., 852606.),
            (16678259., 852606.),
            (16679259., 852606.),
            (16680259., 852606.)
        ])


        Do a horizontal slice of all Channels, i.e. read a subset of samples
        from all channels

        >>> curves[0:2]
        array([
            (16677259., 852606., 2233., 852606.),
            (16678259., 852606., 2237., 852606.)])

        Horizontal and vertical slicing can be combined

        >>> curves['CHANN2'][0]
        16677259.0

        And here the subscription order is irrelevant

        >>> curves[0]['CHANN2']
        16677259.0

        Some curves, like image curves, have multi-dimensional samples.
        Accessing a single sample from a 2-dimensional curve

        >>> curves = frame.curves()
        >>> sample = curves['MULTI_D_CHANNEL'][0]
        >>> sample
        array([[ 1,  2,  3],
               [ 4,  5,  6],
               [ 7,  8,  9],
               [10, 11,  12]])

        This sample is a 2-dimensional array of size 4x3. We can continue to
        slice this sample. Note that now the subscription order here **does**
        matter. Here we read the two last rows

        >>> sample[-2:]
        array([[  7,  8,  9],
               [ 10, 11, 12]])

        Lets read every second column

        >>> sample[:,::2]
        array([[ 1, 3],
               [ 4, 6],
               [ 7, 9],
               [10, 12]])

        Note the syntax. Within the brackets, everything before the ',' is row-
        operations and everything after are column-operations. Read it as: keep
        all rows (:) and then from first to last column, keep every 2nd column
        (::2). The comma syntax for indexing different axes extends to array's
        with higher orders as well.

        Combine the two to read a specific element

        >>> sample[0,0]
        1

        If you prefer to work with pandas over numpy, the conversion is
        trivial

        >>> import pandas as pd
        >>> curves = pd.DataFrame(frame.curves())

        If the Frame contains an index Channel, use that as index in the
        DataFrame

        >>> curves = frame.curves()
        >>> if frame.index_type:
        >>>     indexname  = curves.dtype.names[0]
        >>>     curvenames = curves.dtype.names[1:]
        >>>     pdcurves = pd.DataFrame(curves[list(curvenames)], index=curves[indexname])
        >>>     pdcurves.index.name = indexname
        >>> else:
        >>>     pdcurves = pd.DataFrame(curves)

        Let's walk through this. Firstly, check that *index_type* is not None,
        if it is, there is no index channel to set. Secondly, note how the
        curvenames are all stored in the array itself. Then all that is needed
        is to extract the first name as index and let the rest be added to the
        DataFrame as normal Channels.

        See also
        --------

        Channel.curves : Access the curve-data directly through the Channel
          objects

        Returns
        -------
        curves : np.ndarray

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
                    logging.warning(msg.format(self.fingerprint,
                                 ch.fingerprint, ch.frame.fingerprint))
                ch.frame = self
            except AttributeError:
                #happens if ch has been parsed as other type
                pass

    def describe_attr(self, buf, width=80, indent='', exclude=''):
        if len(self.channels) > 0:
            if self.index_type is not None:
                d = OrderedDict()
                d['Description']      =  self.description
                d['Indexed by']       =  self.index_type
                d['Interval']         =  str([self.index_min, self.index_max])
                d['Direction']        =  self.direction
                d['Constant spacing'] =  self.spacing
                d['Index channel']    =  self.channels[0]

                describe_header(buf, 'Channel indexing', width, indent, lvl=2)
                describe_dict(buf, d, width, indent, exclude)

            else:
                index  = 'There is no index channel, channels are indexed '
                index += 'by samplenumber, i.e [1,2,3,..,n]'
                describe_text(buf, index, indent=indent, width=width)

            describe_header(buf, 'Channels', width, indent, lvl=2)
            channels = replist(self.channels, 'name')
            describe_array(buf, channels, width, indent)
        else:
            describe_text(buf, 'Frame has no channels', width, indent)
