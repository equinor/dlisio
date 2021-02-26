import logging
import numpy as np

from collections.abc import Sequence

def issequence(obj):
    """Check if object is a sequence, but ignore string and bytes objects"""
    if isinstance(obj, str): return False
    if isinstance(obj, bytes): return False
    return isinstance(obj, (Sequence, np.ndarray))

def validshape(data, shape, samplecount=None):
    """Return a valid shape that can be used to sample the data.
    For a shape to be valid, the following relationship must hold::

        len(data) % prod(shape) == 0

    In case it does not, validshape will try to infer a new shape:

    - if data has one element, which is a common case, it is safe to assume
    that shape = [1]

    - If len(data) == samplecount. This is useful in cases where the structured
    array is closly linked with e.g. number of zones. Hence len(zones) can be
    uses as a guess for the samplecount.

    Parameters
    ----------

    data : 1-d list_like
        list to be reshaped

    shape : list
        shape of each sample, follows definition by rp66. E.g. [2, 3] is a 2-d
        array with size 2 x 3

    samplecount : int
        a guess of how many samples the structured data should have

    Raises
    ------

    ValueError
        No valid shape is found

    Returns
    -------

    shape : list
        a shape that can be used to reshape the data
    """
    error  = 'cannot reshape array of size {} into shape {}'

    if not issequence(data): return [1]

    size = len(data)
    if size == 0: return shape

    if shape == []:
        if   len(data) == samplecount : shape = [1]
        elif len(data) == 1           : shape = [1]
        else: raise ValueError(error.format(size, shape))

    samplesize = np.prod(np.array(shape))

    if not size % samplesize: return shape
    raise ValueError(error.format(size, shape))

def sampling(data, shape, single=False):
    """Samplify takes a flat array and returns a structured numpy array, where
    each sample is shaped by shape, i.e. each sample may be scalar or ndarray.

    To structure the array, sampling assumes that this relationship holds::

        len(data) % prod(shape) == 0

    Parameters
    ----------

    data : 1-d list_like
        list to be reshaped

    shape : list
        shape of each sample, follows definition by rp66. E.g. [2, 3] is a 2-d
        array with size 2 x 3

    single : boolean
        return only the first sample from the sampled array, even if there is
        more. In that case this is logged as info.

    Returns
    -------

    sampled : np.ndarray
        structured array

    Examples
    --------

    Create a structured array

    >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    >>> dimensions = [2, 3]
    >>> sampled(data, dimensions)
    array(([[[1, 2, 3], [4 , 5, 6]],
            [[7, 8, 9], [10, 11, 12]]])

    Access the 1st sample:

    >>> arr[0]
    array([[1, 2, 3],
           [3, 4, 5])
    """
    if not issequence(data): return np.empty(0)

    size = len(data)
    if size == 0: return np.empty(0)

    samplesize = np.prod(np.array(shape))
    samplecount = size // samplesize

    #TODO: Properly handle types that evaluates to dtype(object) by numpy
    if isinstance(data[0], tuple):
        elem_shape = (len(data[0]), )
    else:
        elem_shape = ()

    data = np.array(data)
    elem_dtype = np.dtype((data.dtype, elem_shape))

    if shape == [1]: dtype = np.dtype(elem_dtype)
    else:            dtype = np.dtype((elem_dtype, tuple(shape)))

    array = np.ndarray(shape=(samplecount,), dtype=dtype, buffer=data)

    if single:
        if len(array) != 1:
            msg = 'found {} samples, should be 1'
            logging.warning(msg.format(len(array)))
        return array[0]

    return array
