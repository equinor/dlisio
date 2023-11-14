import numpy as np

import logging
log = logging.getLogger(__name__)

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

def curves_metadata(dfsr, sample_rate=None, strict=True):
    """ Get the metadata corresponding to curves()

    This is a sister-function to :func:`dlisio.lis.curves`, that returns the
    metadata objects (Spec Blocks) corresponding to the curves returned by
    :func:`dlisio.lis.curves`.

    The keys of the returned dict exactly match the (column) names in the numpy
    array returned by `curves.lis.curves`. The values are the corresponding
    Spec Blocks.

    Notes
    -----

    :func:`curves_metadata` and :func:`curves` should be called with the same
    values for both parameters `sample_rate` and `strict` for the metadata and
    curves to match.

    If dfsr.depth_mode is 1, then there is no Spec Block for the index. In this
    case None is used as value for the index in the returned dict.

    See Also
    --------

    :attr:`DataFormatSpec.index_mnem`  : The mnemonic of the index
    :attr:`DataFormatSpec.index_units` : The units of the index

    Returns
    -------

    metadata : dict

    Examples
    --------

    Lets say that you want to read all curves that are sampled 6x the index,
    and you don't care if the mnemonics are repeated. And that you are also
    interested in the metadata of the curves you read:

    >>> rate = 6
    >>> strict = False
    >>> curves = lis.curves(f, fs, sample_rate=rate, strict=strict)
    >>> metadata = lis.curves_metadata( fs, sample_rate=rate, strict=strict)

    You now have the curves and their metadata. The metadata lookup mirrors the
    (column) names in the data. E.g. access data and metadata for the *first*
    RCCL curve in this log set:

    >>> data = curves['RCCL(0)']
    >>> spec = metadata['RCCL(0)']
    """
    if len(dfsr.specs) == 0: return dict()

    if not uniform_sampling(dfsr) and sample_rate is None:
        msg  = "Multiple sampling rates in file, "
        msg += "please explicitly specify which to read"
        raise RuntimeError(msg)

    if sample_rate is None: sample_rate = 1

    channels = []
    for i, spec in enumerate(dfsr.specs):
        if spec.samples != sample_rate: continue
        if is_index(i, dfsr.depth_mode): continue
        channels.append(spec)

    index = dfsr.specs[0] if dfsr.depth_mode == 0 else None

    # Make sure that we also pass the index mnemonic to `unique_mnemonic` such
    # that the postfix matches even when the index itself is repeated.
    mnemonics = [dfsr.index_mnem] + [x.mnemonic for x in channels]
    uniques   = unique_mnemonics(mnemonics)

    if strict and uniques != mnemonics:
        msg = "duplicated mnemonics in '{}'"
        raise ValueError(msg.format(dfsr))

    return dict(zip(uniques, [index] + channels))

def curves(f, dfsr, sample_rate=None, strict=True):
    """ Read curves

    Read the curves described by the :ref:`Data Format Specification` Record
    (DFSR). The curves are read into a Numpy Structured Array [1]. The
    mnemonics - as described by the DFSR - of the channels are used as column
    names.

    **Fast Channels**

    Some log sets contain curves that are sampled at unequal sampling rate.
    More specifically, curves can be sampled at a greater frequency than the
    recorded index. These are referred to in the LIS79 specification as Fast
    Channels. The sample rate is not absolute, but rather a factor relative to
    the index. E.g. a sampling rate of 1 means that the curve are sampled at the same
    frequency as the index, while a sample rate of 6 means the channel is sampled
    at 6 times the frequency of the index.

    When the sampling rate of a curve is higher than the index, the index is
    linearly interpolated to create the missing values samples. This is the
    LIS79 defined behavior [2]. Note that this is *only* true for the index.
    Other channels will not be re-sampled.

    These LIS79 mechanics of multiple sampling rates within a logset do mean
    that the result of the entire logset is a sparse array. That is, curves at
    lower sampling rates will have a lot of undefined samples. Take this example
    with 2 channels, ``CH01`` and ``CH02``, where ``CH01`` has a sample rate of
    1, and ``CH02`` has a sample rate of 3. The full log set would then look
    like this::

        DEPTH       CH01        CH02
        ----------------------------
        0           -           1
        0           -           2
        300         500         3
        310         -           4
        320         -           5
        330         510         6

    The only depth samples that are recorded in the file are ``300`` and
    ``330``. The rest is interpolated between these depth samples.  Notice how
    the first depth samples are 0. That is because there is no prior recorded
    depth to interpolate against - and constant spacing is not guaranteed.

    Looking at ``CH01`` in the above logset we see that only a third of the
    samples contains actual measurements. Remember, no interpolation rules are
    defined for curves that are not the index. This is an undesirable situation
    both from dlisio's point-of-view - and from the consumer of the log. dlisio
    would have to fill all these undefined samples with some value on behalf of
    the user, as there is no such thing as a sparse numpy array. This will have
    a negative effect on memory consumption. And, depending on the application
    of course, the consumer of the log would likely want to filter out the
    "absent-values" and re-sample the logs anyway. To avoid this, **only
    equally sampled curves can be read into the same numpy array by**
    :func:`dlisio.lis.curves`. **This means that multiple calls to this
    function  are required to read all the curves in the logset.** The
    parameter ``sample_rate`` is used to define which curves to read. Please
    refer to the example section for more details.

    [1] Structured Arrays, https://numpy.org/doc/stable/user/basics.rec.html

    [2] LIS79 ch 3.3.2.2,  https://www.energistics.org/sites/default/files/2022-10/lis-79.pdf

    Parameters
    ----------

    f : LogicalFile
        The logcal file that the dfsr belongs to

    dfsr: dlisio.lis.DataFormatSpec
        Data Format Specification Record

    sample_rate : None
        Read channels matching a specific sampling rate (relative to the
        recorded index). If all curves are sampled equally compared to the
        index, this can be omitted. If not, a value must be given to tell which
        subset of the curves in the log set should be read.

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
        If the DFSR contains one or more channel where the type of the samples
        is lis::mask

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

    When the logset described by the DFSR contains channels with different
    sampling rates, multiple calls to curves are necessary to read all the
    curves. E.g. we can read *all* curves that are sampled at the same rate as
    the index:

    >>> dlisio.lis.curves(f, dfsr, sample_rate=1)
    array([(300, 500),
           (330, 510)],
      dtype=[('DEPT', '<i4'), ('CH01', '<i4')])

    As we can see the outputted logset contains the index curve (DEPT) and
    CH01. However, we know from examination of the current dfsr that there is
    another channel in this logset, ``CH02``, which is sampled at 3 times the
    rate of the index. This curve (and all other curves which are sampled equally
    to it) can be read by a separate call to curves:

    >>> dlisio.lis.curves(f, dfsr, sample_rate=3)
    array([(  0, 1),
           (  0, 2),
           (300, 3),
           (310, 4),
           (320, 5),
           (330, 6)],
      dtype=[('DEPT', '<i4'), ('CH02', '<i4')])

    Note that it's the same index curve as previously, only re-sampled to fit
    the higher sampling rate of ``CH02``.
    """

    if not uniform_sampling(dfsr) and sample_rate is None:
        msg =  "Multiple sampling rates in file, "
        msg += "please explicitly specify which to read"
        raise RuntimeError(msg)

    if sample_rate is None: sample_rate = 1

    validate_dfsr(dfsr)

    mode      = dfsr.depth_mode
    spacing   = dfsr.directional_spacing() if mode == 1 else 0
    idx, fmt  = dfsr_fmtstr(dfsr, sample_rate=sample_rate)
    dtype     = dfsr_dtype(dfsr, sample_rate=sample_rate, strict=strict)
    framesize = dtype.itemsize

    config = core.frameconfig(idx, fmt, sample_rate, mode, spacing, framesize)
    alloc  = lambda size: np.empty(shape = size, dtype = dtype)

    return core.read_data_records(
        f.io,
        f.index,
        dfsr.info,
        config,
        alloc,
    )


def uniform_sampling(dfsr):
    """ Returns True if all channels (except index channel) are sampled equally,
    otherwise returns False """
    rates = set()
    for i, ch in enumerate(dfsr.specs):
        if is_index(i, dfsr.depth_mode): continue
        rates.add(ch.samples)

    return len(rates) <= 1


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


def is_index(i, mode):
    """ Returns true if the i-th channel is an index channel, otherwise, False
    """
    if mode == 0 and i == 0: return True
    else:                    return False

def dfsr_fmtstr(dfsr, sample_rate):
    """Create a fmtstr for the current dfsr

    The fmtstr is an internal string representation of the channels in a DFSR
    used to instruct the parsing routines how to interpret the Implicit Data
    Records. Each channel is represented by a FMT char + a number:

        fmt + count

    fmt is a dlisio defined character, corresponding to a specific lis datatype. E.g.
    "l" corresponds to lis::i32. The count is defined differently depending on the value
    of fmt. For all int and float channels:

        fmt(spec.reprc) + number of entries pr sample

    string-channels are a bit special in that they are limited to one entry pr sample. In this
    case the count refers to the length of the fixed-size string:

        fmt(spec.reprc) + length of string

    If a channel is suppressed, a special fmt char is used and the count refers
    to the total number of bytes that are to be ignored:

       "S" + abs(spec.reserved_size)

    Notes
    -----

    Number of samples is not embedded into the format string

    Warnings
    --------

    This function does not do any sanity-checking of the DFSR itself. It's only
    guaranteed to create a valid fmtstr if validate_dfsr() returns successfully
    for the given DFSR.

    Returns
    -------

    str, str : fmtstr of the index, fmtstr of all non-index channels (in order
               of appearance in dfsr)

    """
    indexfmt = None
    if dfsr.depth_mode == 1:
        reprc = core.lis_reprc( dfsr.depth_reprc )
    else:
        index_channel = dfsr.specs[0]
        reprc = core.lis_reprc( index_channel.reprc )

    indexfmt = reprc2fmt(reprc) + '1'

    fmtstr = []
    for i, spec in enumerate(dfsr.specs):
        if is_index(i, dfsr.depth_mode): continue

        if spec.reserved_size < 0:
            suppress = chr(core.lis_fmt.suppress) + str(abs(spec.reserved_size))
            fmtstr.append(suppress)
            continue

        if spec.samples != sample_rate:
            suppress = chr(core.lis_fmt.suppress) + str(abs(spec.reserved_size))
            fmtstr.append(suppress)
            continue

        sample_size = abs(int( spec.reserved_size  / spec.samples) )

        reprc  = core.lis_reprc(spec.reprc)
        if reprc == core.lis_reprc.string or reprc == core.lis_reprc.mask:
            fmt = reprc2fmt(reprc) + str(int(sample_size))
        else:
            entry_size = core.lis_sizeof_type(reprc)
            fmt = reprc2fmt(reprc) + str(int(sample_size / entry_size))

        fmtstr.append(fmt)

    return indexfmt, ''.join(fmtstr)

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

def dfsr_dtype(dfsr, sample_rate, strict=True):
    """ Crate a valid numpy.dtype for the given DFSR

    Warnings
    --------

    This function does not do any sanity-checking of the DFSR itself. It's only
    guaranteed to create a valid fmtstr if validate_dfsr() returns successfully
    for the given DFSR.
    """
    types = []
    mode = dfsr.depth_mode
    if mode == 1:
        reprc = core.lis_reprc( dfsr.depth_reprc )
        types.append((dfsr.default_index_mnem, nptype[reprc]))

    for i, ch in enumerate(dfsr.specs):
        if ch.reserved_size < 0: continue
        if is_index(i, mode) or ch.samples == sample_rate:
            types.append((ch.mnemonic, spec_dtype(ch)))

    try:
        dtype = np.dtype(types)
    except ValueError as exc:
        msg = "duplicated mnemonics in frame '{}': {}"
        log.error(msg.format(dfsr, exc))
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
    if not len(dfsr.specs):
        raise ValueError("{} has no channels".format(dfsr))

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
        if spec.reserved_size == 0:
            msg =  "Invalid size ({}) for curve {}, "
            msg += "should be != 0)"
            raise ValueError(msg.format(spec.reserved_size, spec.mnemonic))

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


def unique_mnemonics(mnemonics):
    from collections import Counter
    tail = '({})'
    duplicates = [x for x, count in Counter(mnemonics).items() if count > 1]

    # Update each occurrence of duplicated labels. Each set of duplicates
    # requires its own tail-count, so update the list one label at the time.
    for duplicate in duplicates:
        tailcount = 0
        tmp = []
        for name in mnemonics:
            if name == duplicate:
                name += tail.format(tailcount)
                tailcount += 1
            tmp.append(name)
        mnemonics = tmp

    return mnemonics


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
    labels, dtype = zip(*types)
    labels = unique_mnemonics(labels)
    return list(zip(labels, dtype))

