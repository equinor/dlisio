"""
Supporing methods for dlis class.
Are moved into separate file in order not to clutter interface
"""
import numpy as np
from . import core

def curves(dlis, frame, dtype, pre_fmt, fmt, post_fmt):
    """ For internal use.
    Reads curves for provided frame and position defined by frame format:
    pre_fmt (to skip), fmt (to read), post_fmt (to skip)
    """
    indices = dlis.fdata_index[frame.fingerprint]
    #note: shape is wrong for multiple data in one frame
    a = np.empty(shape = len(indices), dtype = dtype)
    core.read_fdata(pre_fmt, fmt, post_fmt, dlis.file, indices, a)
    return a
