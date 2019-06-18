from .basicobject import BasicObject
from .dataobjectutils import *

def zoned():
    return Zoned
def sampled():
    return Sampled
def simple():
    return Simple

class DataObject(BasicObject):
    """ DataObject

    Represents object that is supposed to contain data defined by dimension attribute.
    Provides functionality that helps to deal with it and convert data to numpy arrays.

    See also
    --------

    BasicObject : The basic object that Computation is derived from

    """

    datamap = {}
    """dict:
    Contains information about attributes that actually depend on dimensions,
    therefore would be converted into numpy array during file load.
    Keys should be names of the attributes that actually represent data.
    Value should be a type of that data:
    * zoned   - attribute is zoned
    * sampled - attribute contains multiple samples
    * simple  - attribute depends on dimension attribute only

    It's also possible to remove the values from map in case user doesn't want them
    to be transformed.

    >>> del Measurement.datamap['minus_tolerance']

    With this code 'minus_tolerance' attribute of Measurement class won't longer be
    transformed to a numpy array and will be left as a list of data.

    """

    dtype_format = '{:s}.{:d}.{:d}'
    """
    Used to create named fields in numpy array for zoned or channeled data.
    However it would be used only if simple name is not unique.

    >>> print(param.values["ZONE-A.10.0"][0])

    Note that 'param.values["ZONE-A.10.0"]' returns user an array of data
    which corresponds to proived field label, so if run on 1 object only,
    1-element list will be returned. However, if multiple objects are combined,
    list won't contain only 1 element anymore.
    """

    def __init__(self, obj = None, name = None, type = None):
        super().__init__(obj, name = name, type = type)

        #: Instance-specific dtype label formatter on duplicated mnemonics.
        #: Defaults to DataObject.dtype_format
        self.dtype_fmt = self.dtype_format

        #: Array structure of a single value
        self.dimension   = []

        #: Coordinate axes of the values
        self.axis        = []

        #all the attributes with existing data
        self.datapoints  = {}

        self._attribute_features.extend([data_attribute])

    def reshape(self, loaded=False):
        """
        Will reshape current data into array corresponding to dimension attribute.
        Datapoints will be reshaped to empty in case of mismatch between data.

        Parameters
        ----------
        loaded: boolean
            True if object has been loaded from file. This would cause reversal of dimension
            and axis attributes from Fortran (column-major) to C (row-major) type.
            False if dimension has been supplied by user, hence is row-major already.
        """
        reshape_datapoints(self, loaded)
