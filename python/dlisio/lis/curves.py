import numpy as np
import logging

from .. import core

""" reprc -> numpy format type-string
Conversion from lis' representation codes to type-strings that can be
interpreted by numpy.dtype.
"""
nptype = {
    core.lis_reprc.f16    : 'f4', # 16-bit floating point
    core.lis_reprc.f32    : 'f4', # 32-bit floating point
    core.lis_reprc.f32low : 'f4', # 32-bit low resolution floating point
    core.lis_reprc.f32fix : 'f4', # 32-bit fixed point
    core.lis_reprc.i8     : 'i1', # 8-bit signed integer
    core.lis_reprc.i16    : 'i2', # 16-bit signed integer
    core.lis_reprc.i32    : 'i4', # 32-bit signed integer
    core.lis_reprc.byte   : 'u1', # Byte
}


def curves(f, dfsr, strict=True):
    """ Read curves

    Read the curves described by Data Format Spec Record (DFSR). The curves are
    read into a Numpy Structured Array [1]. The mnemonics - as described by the
    DFSR - of the channels are used as column names.

    [1] https://numpy.org/doc/stable/user/basics.rec.html

    Parameters
    ----------

    f : logical_file
        The logcal file that the dfsr belongs to

    dfsr: dlisio.core.dfsr
        Data Format Specification Record

    strict : boolean, optional
        By default (strict=True) curves() raises a ValueError if there are
        multiple channels with the same mnemonic. Setting strict=False lifts
        this restriction and dlisio will append numerical values (i.e. 0, 1, 2
        ..) to the labels used for column-names in the returned array.

    Returns
    -------

    curves : np.ndarray
        Numpy structured ndarray with mnemonics as column names

    Raises
    ------

    ValueError
        If the DFSR contains the same mnemonic multiple times. Numpy Structured
        Array requires all column names to be unique. See parameter `strict`
        for workaround

    NotImplementedError
        If the DFSR contains one or more "Fast Channels". These are channels
        that are recorded at a higher sampling rate than the rest of the
        channels. dlisio does not currently support fast channels.

    NotImplementedError
        If Depth Record Mode == 1. The depth recording mode is mainly an
        internal detail about how the depth-index is recorded in the file.
        Currently dlisio only supports the default recording mode (0).

    Examples
    --------

    The returned array supports both horizontal- and vertical slicing.
    Slice on a subset of channels:

    >>> curves = dlisio.lis.curves(f, dfsr)
    >>> curves[['CHANN2', 'CHANN3']]
    array([
        (16677259., 852606.),
        (16678259., 852606.),
        (16679259., 852606.),
        (16680259., 852606.)
    ])

    Or slice a subset of the samples:

    >>> curves = dlisio.lis.curves(f, dfsr)
    >>> curves[0:2]
    array([
        (16677259., 852606., 2233., 852606.),
        (16678259., 852606., 2237., 852606.)])

    """

    # Check depth recording mode flag (type 13)
    #
    # If present and type 1, depth only occurs once in each data record, before
    # the first frame. The depth of all other frames in the data record follows
    # a constant sampling given by other entry blocks
    #
    # TODO: implement support
    if any(x for x in dfsr.entries if x.type == 13 and x.value == 1):
        msg = "lis::curves: depth recording mode == 1"
        raise NotImplementedError(msg)

    fmt   = core.dfs_formatstring(dfsr)
    dtype = dfsr_dtype(dfsr, strict=strict)
    alloc = lambda size: np.empty(shape = size, dtype = dtype)

    return core.read_data_records(
        fmt,
        f.io,
        f.index,
        dfsr.info,
        dtype.itemsize,
        alloc,
    )

def dfsr_dtype(dfsr, strict=True):
    types =[]
    types = [
        (ch.mnemonic, np.dtype(nptype[core.lis_reprc(ch.reprc)]))
        for ch in dfsr.specs
    ]

    if any(x for x in dfsr.specs if x.samples > 1):
        raise NotImplementedError("Fast channel not implemented")

    try:
        dtype = np.dtype(types)
    except ValueError as exc:
        msg = "duplicated mnemonics in frame '{}': {}"
        logging.error(msg.format(self.name, exc))
        if strict: raise

        types = mkunique(types)
        dtype = np.dtype(types)

    return dtype

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
                name += tail.format(tailcount)
                tailcount += 1
            tmp.append((name, dtype))
        types = tmp

    return types

