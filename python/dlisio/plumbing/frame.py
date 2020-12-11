from .basicobject import BasicObject
from ..dlisutils import curves
from .valuetypes import scalar, vector, boolean
from .linkage import obname
from .utils import *

from .. import core

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
        'DESCRIPTION': scalar,
        'CHANNELS'   : vector,
        'INDEX-TYPE' : scalar,
        'DIRECTION'  : scalar,
        'SPACING'    : scalar,
        'ENCRYPTED'  : boolean,
        'INDEX-MIN'  : scalar,
        'INDEX-MAX'  : scalar,
    }

    linkage = {
        'CHANNELS' : obname('CHANNEL')
    }

    dtype_format = '{:s}.{:d}.{:d}'

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)
        # Instance-specific dtype label formatter on duplicated mnemonics.
        # Defaults to Frame.dtype_format
        self.dtype_fmt = self.dtype_format

    @property
    def description(self):
        return self['DESCRIPTION']

    @property
    def channels(self):
        return self['CHANNELS']

    @property
    def index_type(self):
        return self['INDEX-TYPE']

    @property
    def direction(self):
        return self['DIRECTION']

    @property
    def spacing(self):
        return self['SPACING']

    @property
    def encrypted(self):
        return 'ENCRYPTED' in self.attic.keys()

    @property
    def index_min(self):
        return self['INDEX-MIN']

    @property
    def index_max(self):
        return self['INDEX-MAX']

    @property
    def index(self):
        """Mnemonic of the channel all channels in this Frame are indexed
        against, if any. See :attr:`Frame.index_type` for definition of
        existing index channel.

        Returns
        -------

        mnemonic : str
        """
        msg = 'Frame has no channels'
        index = None
        if len(self.channels) == 0:
            logging.info(msg)
            return index

        if self.index_type is None: index = 'FRAMENO'
        else:                       index = self.channels[0].name
        return index

    def dtype(self, strict=True):
        """dtype

        data-type of each frame, i.e. the sum of channel.dtype of each channel
        in self.channels. The first column is always FRAMENO.

        If all curve mnemonics are unique, then dtype.names == ['FRAMENO'] +
        [ch.name for ch in self.channels]. If there are more than one channel
        with the same name for this frame, all duplicated mnemonics are
        enriched with origin and copynumber.

        Consider a frame with the channels mnemonics [('TIME', 0, 0), ('TDEP',
        0, 0), ('TIME, 1, 0)]: dtype.names for this frame would be
        ('FRAMENO', 'TIME.0.0', 'TDEP', 'TIME.1.0').

        Duplicated mnemonics are formatted by the dtype_fmt attribute. To use a
        custom format for a specific frame instance, set dtype_fmt for the
        Frame object. If you want to have some other formatting for *all*
        dtypes, set the dtype_format class attribute. It has to be a 3-element
        format-string taking a string and two ints. Custom formatting is
        particularly useful for peculiar files where the full stop (.) appears
        in the mnemonic itself, and a consistent way of parsing origin and
        copynumber are needed.

        In addition to the customizable dtype.names, ch.fingerprint is always
        used as field title, which serves as an alias for the name.

        Returns
        -------
        dtype : np.dtype

        Examples
        --------
        A frame with two TIME channels:

        >>> dtype = frame.dtype()
        >>> dtype.names
        dtype([('FRAMENO', '<i4'),
               (('T.CHANNEL-I.TIME-O.0-C.0','TIME.0.0'), '<f4'),
               (('T.CHANNEL-I.TDEP-O.0-C.0','TDEP'), '<i2'),
               (('T.CHANNEL-I.TIME-O.1-C.0','TIME.1.0'), '<i2')])

        Override instance-specific mnemonic formatting

        >>> frame.dtype().names
        (FRAMENO', 'TIME.0.0', 'TDEP', 'TIME.1.0')
        >>> frame.dtype_fmt = '{:s}-{:d}-{:d}'
        >>> frame.dtype()
        (FRAMENO','TIME-0-0', 'TDEP','TIME-1-0')
        """
        seen = {}
        types = [('FRAMENO', 'i4')]

        duplerr = "duplicated mnemonics in frame '{}': {}"
        fmterr = "rich label for channel '{}' cannot be formatted in frame '{}'"
        info = 'name = {}, origin = {}, copynumber = {}'.format

        fmtlabel = self.dtype_fmt.format
        for i, ch in enumerate(self.channels, start = 1):
            current = ((ch.fingerprint, ch.name), ch.dtype)

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

            types.append(((ch.fingerprint, label), ch.dtype))

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
            types[prev_index] = ((prev.fingerprint, label), prev.dtype)
            seen[ch.name] = None

        try:
            dtype = np.dtype(types)
        except ValueError as exc:
            logging.error(duplerr.format(self.name, exc))
            if strict: raise

            types = mkunique(types)
            dtype = np.dtype(types)

        return dtype

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
        # The first part of every frame is always FRAMENO, which is an
        # variable-lenght unsigned integer (i).
        return 'i' + ''.join([x.fmtstr() for x in self.channels])

    def curves(self, strict=True):
        """All curves belonging to this frame

        Get all the curves in this frame as a structured numpy array. The frame
        includes the frame number (FRAMENO), to detect errors such as missing
        entries and out-of-order frames.

        Parameters
        ----------

        strict : boolean, optional
            By default (strict=True) curves() raises a ValueError if there are
            multiple channel with the same values for both name, origin and
            copynumber. This would be a clear violation of the dlis-spec.
            Setting strict=False lifts this restriction and dlisio will append
            numerical values (i.e. 0, 1, 2 ..) to the labels used for
            column-names in the returned array.

        Returns
        -------
        curves : np.ndarray
            curves with dtype = self.dtype

        Raises
        ------

        ValueError
            If there multiple channels with identical name, origin, copynumber
            in Frame.channels. This can be suppressed by passing strict=False

        See also
        --------
        Channel.curves : Access the curve-data directly through the Channel
          objects
        Frame.dtype : dtype of the array

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

        Note that pandas (and CSV) *only* supports scalar sample values. I.e.
        frames containing one or more channels that have none-scalar sample
        values cannot be converted to pandas.DataFrame or CSV directly.

        If the Frame contains an index Channel, use that as index in the
        DataFrame

        >>> curves = frame.curves()
        >>> pdcurves = pd.DataFrame(curves, index=curves[frame.index])
        >>> pdcurves.index.name = frame.index

        By default the returned np.ndarray have column-names that reflects the
        mnemonics of each Channel

        >>> frame.channels
        [Channel(TDEP), Channel(TIME), Channel(GR)]

        >>> curves = frame.curves()
        >>> curves.dtype.names
        ('FRAMENO', 'TDEP', 'TIME', 'GR')

        Sometimes a Frame can contain multiple Channels with the same
        name/mnemonic, in that case the labels are augmented with the origin and
        copynumber:

        >>> frame.channels
        [Channel(TDEP), Channel(TDEP), Channel(GR)]

        >>> curves = frame.curves()
        >>> curves.dtype.names
        ('FRAMENO', 'TDEP.0.0', 'TDEP.0.1', 'GR')

        This augmentation is customizable by changing :attr:`dtype_fmt`. See
        :attr:`dtype`. Some frames have multiple instances of the same channel
        or mulitple channels where name, origin and copynumber are identical.
        This is a clear violation of the dlis spec and :func:`curves` will raise
        an ValueError by default.

        >>> frame.channels
        [Channel(TDEP), Channel(TDEP), Channel(GR)]

        >>> Frame.curves()
        ValueError: field 'TDEP.0.0' occurs more than once

        However, :func:`curves` offers an escape-hatch to get the underlying data.
        By passing strict=False dlisio appends numerical values to the identical
        channels

        >>> curves = frame.curves(strict=False)
        >>> curves.dtype.names
        ('FRAMENO', 'TDEP.0.0(0)', 'TDEP.0.0(1)', 'GR')
        """
        return curves(self.logicalfile,
                      self,
                      self.dtype(strict=strict),
                      "",
                      self.fmtstr(),
                      "")

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

    def describe_attr(self, buf, width=80, indent='', exclude=''):
        if len(self.channels) > 0:
            if self.index_type is not None:

                index = self.channels[0]
                d = OrderedDict()

                d['Description']      = 'DESCRIPTION'
                d['Indexed by']       = 'INDEX-TYPE'
                d['Index units']      = index.units
                d['Index min']        = 'INDEX-MIN'
                d['Index max']        = 'INDEX-MAX'
                d['Direction']        = 'DIRECTION'
                d['Constant spacing'] = 'SPACING'
                d['Index channel']    = index

                describe_header(buf, 'Channel indexing', width, indent, lvl=2)
                describe_attributes(buf, d, self, width, indent, exclude)
            else:
                index  = 'There is no index channel, channels are indexed '
                index += 'by samplenumber, i.e [1,2,3,..,n]'
                describe_text(buf, index, indent=indent, width=width)

            describe_header(buf, 'Channels', width, indent, lvl=2)
            channels = replist(self.channels, 'name')
            describe_array(buf, channels, width, indent)
        else:
            describe_text(buf, 'Frame has no channels', width, indent)


def mkunique(types):
    """ Append a tail to duplicated labels in types

    Parameters
    ----------

    types : list(tuple)
        list of tuples with labels and dtype

    Returns
    -------

    types : list(tuple)
        list of tuples with labels and dtype

    Examples
    --------

    >>> mkunique([('TIME', 'i2'), ('TIME', 'i4')])
    [('TIME(0)', 'i2'), ('TIME(1)', 'i4')]
    """
    from collections import Counter

    tail = '({})'
    labels = [label for label, _ in types]
    duplicates = [x for x, count in Counter(labels).items() if count > 1]

    # Update each occurance of duplicated labels. Each set of duplicates
    # requires its own tail-count, so update the list one label at the time.
    for duplicate in duplicates:
        tailcount = 0
        tmp = []
        for name, dtype in types:
            if name == duplicate:
                field, label = name
                field += tail.format(tailcount)
                label += tail.format(tailcount)
                tailcount += 1
                name = (field, label)
            tmp.append((name, dtype))
        types = tmp

    return types
