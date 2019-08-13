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
    A channel is a sequence of measured or computed samples that are index
    against e.g. depth or time. Each sample can be a scalar or a n-dimentional
    array.

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
        #: Descriptive name of the channel.
        self.long_name     = None

        #: Representation code
        self.reprc         = None

        #: Physical units of each element in the channel's sample arrays
        self.units         = None

        #: Property indicators that summerizes the characteristics of the
        #: channel and the processing that have produced it.
        self.properties    = []

        #: Dimensions of the samples
        self.dimension     = []

        #: Coordinate axes of the samples
        self.axis          = []

        #: The maximum size of the sample dimensions
        self.element_limit = []

        #: The source of the channel. Returns the source object, if any
        self.source        = None

        #: The numpy data type of the sample array
        self._dtype        = None

        #: Format-string of the channel. Mainly indended for internal use
        self._fmtstr       = None

        #: Frame to which channel belongs to
        self.frame        = None

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
        Reads curves for the channel.

        Examples
        --------
        Read curves for the channel and access 3rd sample

        >>> curves = channel.curves()
        >>> curves
        array([1.1, 2.2, 3.3])
        >>> curves[2]
        3.3

        Read curves for multidimensional channel

        >>> curves = multichannel.curves()
        >>> curves
        array([[[  1,  2,  3],
                [  4,  5,  6]],
               [[  7,  8,  9],
                [ 10, 11,  12]]])

        Access 2nd sample, 1st row

        >>> curves[1][0]
        array([7, 8, 9])

        Returns
        -------
        curves : np.array

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
