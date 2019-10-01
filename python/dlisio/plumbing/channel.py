from .basicobject import BasicObject
from ..reprc import dtype, fmt
from ..dlisutils import curves
from .valuetypes import scalar, vector
from .linkage import obname, objref
from .utils import *

import numpy as np
from collections import OrderedDict


class Channel(BasicObject):
    """
    A channel is a sequence of measured or computed samples that are indexed
    against some physical quantity e.g. depth or time. The standard supports
    multi-dimensional samples. Each sample can be a scalar or a n-dimensional
    array. In addition to giving access to the actual curve-data, the Channel
    object contains metadata about the curve.

    All Channels are a part of one, and only one, Frame. The parent Frame can
    be reached directly through :py:attr:`frame`.

    Refer to the :py:func:`curves` to see some examples on how to access the
    curve-data.

    Attributes
    ----------

    long_name : str or Longname
        Descriptive name of the channel.

    reprc : int
        Representation code

    units : str
        Physical units of each element in the channel's sample arrays

    properties : list(str)
        Property indicators that summarizes the characteristics of the
        channel and the processing that have produced it.

    dimension : list(int)
        Dimensions of the samples

    axis : list(Axis)
        Coordinate axes of the samples

    element_limit : list(int)
        The maximum size of the sample dimensions

    source
        The source of the channel. Returns the source object, if any

    frame : Frame
        Frame to which channel belongs to

    See also
    --------

    BasicObject : The basic object that Channel is derived from

    Notes
    -----

    The Channel object reflects the logical record type CHANNEL, defined in
    rp66. CHANNEL records are listed in Appendix A.2 - Logical Record Types and
    described in detail in Chapter 5.5.1 - Static and Frame Data, CHANNEL
    objects.
    """
    attributes = {
        'LONG-NAME'          : scalar('long_name'),
        'REPRESENTATION-CODE': scalar('reprc'),
        'UNITS'              : scalar('units'),
        'PROPERTIES'         : vector('properties'),
        'DIMENSION'          : vector('dimension'),
        'AXIS'               : vector('axis'),
        'ELEMENT-LIMIT'      : vector('element_limit'),
        'SOURCE'             : scalar('source')
    }

    linkage = {
        'long_name' : obname("LONG-NAME"),
        'axis'      : obname("AXIS"),
        'source'    : objref
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'CHANNEL')
        self.long_name     = None
        self.reprc         = None
        self.units         = None
        self.properties    = []
        self.dimension     = []
        self.axis          = []
        self.element_limit = []
        self.source        = None

        # The numpy data type of the sample array
        self._dtype        = None
        # Format-string of the channel. Mainly intended for internal use
        self._fmtstr       = None
        self.frame        = None

    @property
    def index(self):
        """The Channel this Channel is indexed against, if any. See
        :attr:`Frame.index_type` for definition of existing index channel.

        Returns
        -------

        channel : Channel or None
        """
        msg = 'This channel is an index channel'
        index = self.frame.index

        if index == self: logging.info(msg)
        return index

    @property
    def dtype(self):
        """dtype

        data-type of each sample in the channel's sample array. The dtype-label
        is *channel.name.id*.

        Returns
        -------

        dtype : np.dtype
        """
        if self._dtype: return self._dtype

        if len(self.dimension) == 1:
            shape = self.dimension[0]
        else:
            shape = tuple(self.dimension)

        self._dtype = np.dtype((dtype[self.reprc], shape))

        return self._dtype

    def load(self):
        super().load()
        self.frame = None
        # Order of elements is reversed due to RP66 column-first data
        # storage approach
        self.dimension        = self.dimension[::-1]
        try:
            self.refs['axis'] = self.refs['axis'][::-1]
        except KeyError:
            pass
        self.element_limit    = self.element_limit [::-1]

    def fmtstr(self):
        """Generate format-string for Channel

        The format-string is mainly intended for internal use.

        Returns
        -------

        fmtstr : str
        """
        if self._fmtstr: return self._fmtstr

        samples = np.prod(np.array(self.dimension))
        reprc = fmt[self.reprc]
        self._fmtstr = samples * reprc

        return self._fmtstr

    def curves(self):
        """
        Returns a numpy ndarray with the curves-values.

        Examples
        --------

        Read the full curve

        >>> curve = channel.curves()
        >>> curve
        array([1.1, 2.2, 3.3, 4.4])

        The returned array supports common slicing operations

        >>> curve[::2]
        array([1.1, 3.3])

        Read the full curve from a multidimensional channel

        >>> curve = multichannel.curves()
        >>> curve
        array([[[  1,  2,  3],
                [  4,  5,  6]],
               [[  7,  8,  9],
                [ 10, 11,  12]]])

        This curve has two samples, that both are of size 2x3. From the 1st
        sample, read the element located in the 2nd row, 3rd column

        >>> curve[0][1][2]
        6

        See also
        --------

        Frame.curves() : Read all the curves in a Frame in one go

        Returns
        -------
        curves : np.ndarray
        """
        frame = self.frame
        pre_fmt, fmt, post_fmt = frame.fmtstrchannel(self)
        return curves(frame.file, frame, self.dtype, pre_fmt, fmt, post_fmt)

    def describe_attr(self, buf, width, indent, exclude):
        describe_description(buf, self.long_name, width, indent, exclude)

        d = OrderedDict()
        d['Physical unit of sample']   = self.units
        d['Sample dimensions']         = self.dimension
        d['Axis']                      = self.axis
        d['Maximum sample dimensions'] = self.element_limit
        d['Property indicators']       = self.properties
        d['Source']                    = self.source

        describe_dict(buf, d, width, indent, exclude)
