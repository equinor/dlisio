from .basicobject import BasicObject
from ..reprc import dtype
from .valuetypes import scalar, vector

import numpy as np

import logging

class Channel(BasicObject):
    """Channel

    A channel is a sequence of measured or computed samples that are index
    against e.g. depth or time. Each sample can be a scalar or a n-dimentional
    array.

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
        'SOURCE'             : scalar('source_ref')
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

        #: The source of the channel. Returns the reference to a source object
        self.source_ref    = None

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

    def link(self, objects, sets):
        if self.source_ref is None:
            return

        ref = self.source_ref.fingerprint
        try:
            self.source = objects[ref]
        except KeyError:
            problem = 'channel source referenced, but not found. '
            ids = 'channel = {}, source = {}'.format(self.fingerprint, ref)

            info = 'not populating source attribute for {}'
            info = info.format(self.fingerprint)

            logging.warning(problem + ids)
            logging.info(info)
