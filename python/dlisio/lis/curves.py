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
    fmt   = core.dfs_formatstring(dfsr)
    dtype = dfsr_dtype(dfsr, strict=strict)
    alloc = lambda size: np.empty(shape = size, dtype = dtype)

    return core.read_fdata(
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
        (ch.mnemonic, np.dtype(nptype[ch.reprc]))
        for ch in dfsr.specs
    ]

    if any([x for x in dfsr.specs if x.samples > 1]):
        raise RuntimeError("Fast channel not implemented")

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

