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
    core.lis_reprc.string : 'O',  # String
}


def curves(f, dfsr, strict=True, skip_fast=False):
    """ Read curves

    Read the curves described by the :ref:`Data Format Specification` Record
    (DFSR). The curves are read into a Numpy Structured Array [1]. The
    mnemonics - as described by the DFSR - of the channels are used as column
    names.

    [1] https://numpy.org/doc/stable/user/basics.rec.html

    Parameters
    ----------

    f : LogicalFile
        The logcal file that the dfsr belongs to

    dfsr: dlisio.lis.DataFormatSpec
        Data Format Specification Record

    strict : boolean, optional
        By default (strict=True) curves() raises a ValueError if there are
        multiple channels with the same mnemonic. Setting strict=False lifts
        this restriction and dlisio will append numerical values (i.e. 0, 1, 2
        ..) to the labels used for column-names in the returned array.

    skip_fast : boolean, optional
        By default (skip_fast=False) curves() will raise if the dfsr contains
        one or more fast channels. A fast channel is one that is sampled at a
        higher frequency than the rest of the channels in the dfsr.
        skip_fast=True will drop all the fast channels and return a numpy array
        of all normal channels.

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
        If the DFSR contains one or more channel where the type of the samples
        is lis::mask

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
    validate_dfsr(dfsr)

    # Check depth recording mode flag (type 13)
    #
    # If present and type 1, depth only occurs once in each data record, before
    # the first frame. The depth of all other frames in the data record follows
    # a constant sampling given by other entry blocks
    #
    # TODO: implement support
    if any(x for x in dfsr.entries if x.type == 13 and x.value == 1):
        msg = "lis.curves: depth recording mode == 1"
        raise NotImplementedError(msg)

    if any(x for x in dfsr.specs if x.samples > 1) and not skip_fast:
        raise NotImplementedError("Fast channel not implemented")

    fmt   = dfsr_fmtstr(dfsr)
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

def reprc2fmt(reprc):
    if   reprc == core.lis_reprc.i8:     fmt = core.lis_fmt.i8
    elif reprc == core.lis_reprc.i16:    fmt = core.lis_fmt.i16
    elif reprc == core.lis_reprc.i32:    fmt = core.lis_fmt.i32
    elif reprc == core.lis_reprc.f16:    fmt = core.lis_fmt.f16
    elif reprc == core.lis_reprc.f32:    fmt = core.lis_fmt.f32
    elif reprc == core.lis_reprc.f32low: fmt = core.lis_fmt.f32low
    elif reprc == core.lis_reprc.f32fix: fmt = core.lis_fmt.f32fix
    elif reprc == core.lis_reprc.string: fmt = core.lis_fmt.string
    elif reprc == core.lis_reprc.byte:   fmt = core.lis_fmt.byte
    elif reprc == core.lis_reprc.mask:   fmt = core.lis_fmt.mask
    else:
        raise ValueError("Invalid representation code")

    return chr(fmt)


def dfsr_fmtstr(dfsr):
    """Create a fmtstr for the current dfsr"""

    fmtstr = []
    for spec in dfsr.specs:
        size = spec.reserved_size
        if size < 0 or spec.samples > 1:
            fmtstr.append(chr(core.lis_fmt.suppress) + str(abs(size)))
            continue

        sample_size = size / spec.samples

        reprc  = core.lis_reprc(spec.reprc)
        if reprc == core.lis_reprc.string or reprc == core.lis_reprc.mask:
            fmt = reprc2fmt(reprc) + str(int(sample_size))
        else:
            entry_size = core.lis_sizeof_type(reprc)
            fmt = reprc2fmt(reprc) * int(sample_size / entry_size)

        fmtstr.append(fmt)

    return ''.join(fmtstr)

def spec_dtype(spec):
    # As strings does not have encoded length, the length is implicitly given
    # by the number of reserved bytes for one *sample*. This means that
    # channels that use lis::string as their data type _always_ have exactly
    # one entry
    reprc = core.lis_reprc(spec.reprc)
    if reprc == core.lis_reprc.string:
        return np.dtype(( nptype[reprc] ))

    sample_size = spec.reserved_size / spec.samples
    entries     = sample_size / core.lis_sizeof_type(spec.reprc)

    if entries == 1: dtype = np.dtype(( nptype[reprc] ))
    else:            dtype = np.dtype(( nptype[reprc], int(entries) ))
    return dtype

def dfsr_dtype(dfsr, strict=True):
    """ Crate a valid numpy.dtype for the given DFSR

    Warnings
    --------

    This function does not do any sanity-checking of the DFSR itself. It's only
    guaranteed to create a valid fmtstr if validate_dfsr() returns successfully
    for the given DFSR.
    """
    types = []

    for ch in dfsr.specs:
        if ch.reserved_size < 0: continue
        if ch.samples > 1: continue

        types.append((ch.mnemonic, spec_dtype(ch)))

    try:
        dtype = np.dtype(types)
    except ValueError as exc:
        msg = "duplicated mnemonics in frame '{}': {}"
        logging.error(msg.format(dfsr, exc))
        if strict: raise

        types = mkunique(types)
        dtype = np.dtype(types)

    return dtype

def validate_reprc(reprc, mnemonic):
    if reprc is None:
        msg = "Invalid representation code ({}) in curve {}"
        raise ValueError(msg.format(reprc, mnemonic))

    if core.lis_reprc(reprc) == core.lis_reprc.mask:
        msg = "lis::mask is not supported as a curve type"
        raise NotImplementedError(msg)

    if core.lis_reprc(reprc) not in nptype:
        msg = "Invalid representation code ({}) in curve {}"
        raise ValueError(msg.format(int(reprc), mnemonic))


def validate_dfsr(dfsr):
    """ Sanity check the Data Format Spec

    I.e. verify that it's possible to create valid format-strings and
    numpy.dtype from its content.
    """

    mode = dfsr.depth_mode
    if mode != 0 and mode != 1:
        raise ValueError("Invalid depth recording mode")

    index_mnem = dfsr.specs[0].mnemonic if mode == 0 else 'DEPT'
    index_repr = dfsr.specs[0].reprc    if mode == 0 else dfsr.depth_reprc

    validate_reprc(index_repr, index_mnem)

    if core.lis_reprc(index_repr) == core.lis_reprc.string:
        msg = "Invalid type for index (string)"
        raise ValueError(msg)

    if mode == 0:
        index = dfsr.specs[0]
        if index.reserved_size < 0:
            raise ValueError("Index channel is suppressed")

        if index.samples > 1:
            msg = "Index channel cannot be a fast channel (samples={})"
            raise ValueError(msg.format(index.samples))

        reprsize = core.lis_sizeof_type(index.reprc)
        if  index.reserved_size > reprsize:
            msg = "Index channel cannot have multiple entries per sample"
            raise ValueError(msg)

    for spec in dfsr.specs:
        if spec.samples < 1:
            msg =  "Invalid number of samples ({}) for curve {}, "
            msg += "should be > 0)"
            raise ValueError(msg.format(spec.samples, spec.mnemonic))

        sample_size = spec.reserved_size / spec.samples
        if sample_size % 1:
            msg =  "Invalid sample size ({}) for curve {}, "
            msg += "should be an integral number of bytes"
            raise ValueError(msg.format(sample_size, spec.mnemonic))

        validate_reprc(spec.reprc, spec.mnemonic)
        reprc = core.lis_reprc(spec.reprc)

        if reprc == core.lis_reprc.string or reprc == core.lis_reprc.mask:
            continue

        reprsize = core.lis_sizeof_type(spec.reprc)
        entries  = sample_size / reprsize
        if entries % 1:
            msg =  "Invalid number of entries per sample ({}) in curve {}. "
            msg += "should be an integral number of entries"
            raise ValueError(msg.format(entries, spec.mnemonic))

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

    # Update each occurrence of duplicated labels. Each set of duplicates
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

