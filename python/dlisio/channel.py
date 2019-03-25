from .basicobject import BasicObject
from .reprc import dtype

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
    def __init__(self, obj = None):
        super().__init__(obj, "CHANNEL")
        self._long_name     = None
        self._reprc         = None
        self._units         = None
        self._properties    = []
        self._dimension     = []
        self._axis          = []
        self._element_limit = []
        self._source        = None
        self._dtype         = None
        self.source_ref     = None

    @staticmethod
    def load(obj):
        self = Channel(obj)
        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "LONG-NAME"          : self._long_name     = attr.value[0]
            if attr.label == "REPRESENTATION-CODE": self._reprc         = attr.value[0]
            if attr.label == "UNITS"              : self._units         = attr.value[0]
            if attr.label == "PROPERTIES"         : self._properties    = attr.value
            if attr.label == "DIMENSION"          : self._dimension     = attr.value
            if attr.label == "AXIS"               : self._axis          = attr.value
            if attr.label == "ELEMENT-LIMIT"      : self._element_limit = attr.value
            if attr.label == "SOURCE"             : self.source_ref     = attr.value[0]

        self.stripspaces()
        return self

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

    @property
    def long_name(self):
        """Long name

        Long descriptive name of the channel.

        A long_name can be either:
        1. A unstructured desciptive string
        2. An dlis.core.obname referencing a Longname object

        Returns
        -------

        long_name : str or dlisio.core.obname
        """
        return self._long_name

    @property
    def reprc(self):
        """Representation code

        reprc specifies the Representation Code of each element of a sample
        value, i.e. if the values are represented as float, double etc..

        Returns
        -------
        reprc : int
        """
        return self._reprc

    @property
    def units(self):
        """Units

        Physical units of each element in the channel's sample arrays

        Returns
        -------

        units : str
        """
        return self._units

    @property
    def properties(self):
        """Properties

        List of property indicators. Property indicators summerizes the
        characteristics of the channel and the processing that have
        produced it.

        Notes
        -----

        Property indicators are described in rp66, Appendix C

        Returns
        -------

        property: list of str
        """
        return self._properties

    @property
    def dimension(self):
        """Dimensions

        The array structure of each channel sample. Each element in *dimension*
        specifies the number of elements along each dimension of the channel
        sample array's. The dimensionality of the sample arrays is implicitly
        given by len(dimension).  E.g: if **dimension = [10, 50, 20]** then
        each channel sample array is a 3-dimensional array of size 10x50x20.

        Notes
        -----

        The dimension attribute is defined in rp66, Chapter 4.4.3 - DIMENSION
        Attribute

        Returns
        -------

        dimension : list of int
        """
        return self._dimension

    @property
    def axis(self):
        """Axis

        Coordinate axes of the channel's sample arrays

        While *Channel.dimension* spesifies the shape and size of the sample
        arrays, the axis describes the coordinate axes of the sample arrays.
        The axis is a list of references to a Axis objects.

        Notes
        -----

        The axis attribute is defined in rp66, Chapter 4.4.4 - AXIS
        Attribute

        Returns
        -------

        axis : list of dlisio.core.obname
            each element is a reference to an axis object
        """
        return self._axis

    @property
    def element_limit(self):
        """Element limit

        Maximum size of the channel's sample arrays. I.e. the maxiumum value of
        the elements and lenght of *Channel.dimension*.

        Notes
        -----

        Ref rp66

        Returns
        -------

        element_limit : list of int

        """
        return self._element_limit

    @property
    def source(self):
        """Source

        The source of this channel, e.g. a Tool, Process or Calibration Object.

        Returns
        -------
        source
        """
        return self._source

    def link(self, objects, sets):
        if self.source_ref is None:
            return

        ref = self.source_ref.fingerprint
        try:
            self._source = objects[ref]
        except KeyError:
            problem = 'channel source referenced, but not found. '
            ids = 'channel = {}, source = {}'.format(self.fingerprint, ref)

            info = 'not populating source attribute for {}'
            info = info.format(self.fingerprint)

            logging.warning(problem + ids)
            logging.info(info)
