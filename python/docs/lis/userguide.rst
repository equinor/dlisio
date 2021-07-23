LIS User Guide
==============

First things first, import the LIS submodule:

.. code-block:: python

   >>> from dlisio import lis

.. currentmodule:: dlisio.lis

The main entry point for the LIS reader is :func:`dlisio.lis.load`, which is
designed to work with python's ``with``-statement:

.. code-block:: python

   >>> with lis.load('myfile.lis') as files:
   ...      pass

You can also use ``load`` without the ``with``-statement, but then the exercise
of closing the filehandle is left to you:

.. code-block:: python

   >>> files = lis.load('myfile.lis')
   >>> # Work with your file, then close when done
   >>> files.close()

``load`` returns an instance of :class:`dlisio.lis.PhysicalFile` - a tuple-like
object containing all the Logical Files (LF) in ``myfile.lis``.

.. note::
    If you are unfamiliar with Logical Files and the internal structure of a
    LIS file, please refer to :class:`dlisio.lis.LogicalFile` and
    :class:`dlisio.lis.PhysicalFile`.

Lets have a closer look at one of the Logical Files returned by load:

.. code-block:: python

   >>> f, *tail = files

The Logical File, ``f``, is an instance of :class:`dlisio.lis.LogicalFile`
which is the main interface for interacting with Logical Files.

A Logical File contains a File Header Logical Header (FTLR), and optionally a
File Trailer Logical Record (FTLR). These contain general information specific
to *this* LF such as the file name and date of generation:

.. code-block:: python

   >>> header = f.header()
   >>> trailer = f.trailer()

While the FHLR and FTLR are specific to one Logical File, the Reel
Header/Trailer (RHLR/RTLR) and Tape Header/Trailer (THLR/TTLR) contain general
information that applies to the reel and tape, respectively. These records can
also be reached directly from the Logical File:

.. code-block:: python

   >>> header = f.reel.header()
   >>> trailer = f.reel.trailer()

For a full overview of the content off all these records, please refer to :ref:`LIS Logical Records`.


Working with the curves
-----------------------

Getting the overview
....................

Within a LIS Logical File, curves are defined and organized by Data Format
Specification Records (DFSR). A DFSR defines a set of channels/curves that are
sampled along the same index. There might be multiple Data Format Specification
Records in a Logical File, each defining different channels/curves and index.

.. note::
    LIS79 opens for the presence of duplicated DFSR, for redundancy. Currently,
    dlisio has no support for identifying redundant DFSRs, and
    :func:`dlisio.lis.curves` will return empty arrays for these.

The :class:`dlisio.lis.DataFormatSpec` can be accessed directly from the
:class:`dlisio.lis.LogicalFile`:

.. code-block:: python

    >>> formatspecs = f.data_format_specs()

A DFSR contains information about the logset in general, such as logging
direction and information about the index. In addition it contains a list of
Spec Blocks, :attr:`dlisio.lis.DataFormatSpec.specs`. Each Spec Block describes
one of the channels/curves in the logset. But let's begin by looking at the
index:

.. code-block:: python

    >>> format_spec = formatspecs[0]
    >>> format_spec.index_mnem
    'DEPT'
    >>> format_spec.index_units
    '.1IN'
    >>> format_spec.spacing
    60
    >>> format_spec.spacing_units
    '.1IN'
    >>> format_spec.direction
    255

This tells us that the current logset is indexed against depth, and that the
depth is measured in 1/10 of an inch. There is also a constant spacing of 60
.1IN (or 6 IN) between samples. Note that there is no general requirement that
the index is evenly spaced. In that case ``spacing`` and ``spacing_units``
might not be recorded. Lastly we see that the measurements are taken going
down-hole (refer to :attr:`dlisio.lis.DataFormatSpec.direction`).

Now lets look at the individual channels/curves in the logset. We can list the
mnemonics and the units of measurement by simply looping the Spec Blocks:

.. code-block:: python

    >>> for spec in format_spec.specs:
    ...     print("Index: {} (units={})".format(spec.mnem, spec.units))
    "Index: 'DEPT', units: '.1IN')"
    "Index: 'TIME', units: 'ms  ')"
    "Index: 'CHX ', units: 'M   ')"
    "Index: 'RCCL', units: '    ')"

.. note::
    Please refer to :class:`dlisio.lis.DataFormatSpec` and
    :class:`dlisio.core.spec_block_0` / :class:`dlisio.core.spec_block_1` for
    the complete documentation of DFSR and Spec Blocks, respectively.

Reading the curves
..................

The :class:`dlisio.lis.DataFormatSpec` only contains the metadata about the
logset. To read the actual curves, pass the DFSR ``format_spec`` to
:func:`dlisio.lis.curves` together with the filehandle ``f``:

.. code-block:: python

    >>> curves = lis.curves(f, format_spec)

This returns a `structured numpy.ndarray`_ containing all the curves in the
logset. The array can be indexed by the mnemonics from the Spec Blocks.

Fast Channels
.............

There is one caveat to reading the curves from a logset that is necessary to be
aware of. LIS supports a concept it refers to as 'Fast Channels'. In short this
means that channels within the *same* logset can have different sampling rates.

When a logset contains curves with different sampling rates, these have to be
read separately. I.e. multiple calls to the :func:`dlisio.lis.curves` are
necessary in order to read all the curves. The sampling rate of a channel is
recorded in its Spec Block:

.. code-block:: python

    >>> ch = format_spec.specs[-1]
    >>> ch.mnem
    'RCCL'
    >>> ch.samples
    6

The last channel in this Data Format Spec, ``RCCL``, has a sampling rate of 6,
which means it's sampled 6 times as frequent as the index channel. Remember,
that the index ``DEPT`` was sampled once every 6th inch. That implicitly means
that ``RCCL`` is sampled once every inch.

You can also get a set of all sample rates in the DataFormatSpec:

.. code-block:: python

    >>> format_spec.sample_rates()
    {1, 6, 30}

There are 3 different sampling rates. Only channels with the same sample rate
can be read in one go. To read all the curves several calls to
:func:`dlisio.lis.curves()` are necessary:

.. code-block:: python

    >>> data_01 = lis.curves(f, format_spec, sample_rate=1)
    >>> data_06 = lis.curves(f, format_spec, sample_rate=6)
    >>> data_30 = lis.curves(f, format_spec, sample_rate=30)

.. note::
    Please refer to :func:`dlisio.lis.curves` for a more comprehensive
    explanation of this topic.

.. note::
    When reading channels with a higher sampling rate, the index is still
    included in the resulting numpy array, and the missing values are linearly
    interpolated between the samples in the file. This behaviour is defined by
    LIS79 itself.

Associate curves and metadata
.............................

:func:`dlisio.lis.curves` has a sister function
:func:`dlisio.lis.curves_metadata`. This function can be useful if you want to
associate the curves and metadata (Spec Blocks):

.. code-block:: python

    >>> data = lis.curves(f, format_spec, sample_rate=6)
    >>> meta = lis.curves_metadata(format_spec, sample_rate=6)

When passing the same DFSR and ``sample_rate`` to
:func:`dlisio.lis.curves_metadata` and :func:`dlisio.lis.curves` you get a
dict with the corresponding Spec Blocks. Like the numpy array returned by
``curves()`` this dict uses the mnemonics from the Spec Blocks as keys. This
makes it easy to get both the curve itself and its metadata:

.. code-block:: python

    >>> data['RCCL']
    array([-0.00488281, -0.00488281, -0.00488281, ...,  0.01904297,
        0.01806641,  0.01806641], dtype=float32)

    >>> meta['RCCL']
    dlisio.core.spec_block0('mnemonic=RCCL')



A complete example
..................

Putting this all together to read *all* the curves- and metadata from the
Logical File, ``f``, we get:

.. code-block:: python

    >>> for format_spec in f.data_format_specs():
    ...    for sample_rate in format_spec.sample_rates():
    ...        data = lis.curves(f, format_spec, sample_rate)
    ...        meta = lis.curves_metadata(format_spec, sample_rate)
    ...        # Do something fun with it

Reading parameters and other metadata from Information Records
--------------------------------------------------------------

The records :ref:`Job Identification`, :ref:`Tool String Info` and
:ref:`Wellsite Data` may contain useful information such as company- and
well-name, or parameters of some kind. These records are structured identically,
and in dlisio they share the common interface of
:class:`dlisio.lis.InformationRecord`.

.. note::
   The LIS79 specification does not have a precise definition of when to
   use which record type. Hence it's up to the producers to decide which of the
   above record types to use.

The records can be accessed through their own methods on
:class:`dlisio.lis.LogicalFile`. E.g. all the Wellsite Data Records can be read
with :func:`dlisio.lis.LogicalFile.wellsite_data()`:

.. code-block:: python

    >>> records = f.wellsite_data()
    >>> print(records)
    [InformationRecord(type=lis_rectype.wellsite_data, ltell=62)]


This particular file only contains a single Wellsite Data Record, but it's not
uncommon that a file contains multiple Information Records of the same type.
Let's have a closer look at its content:

.. code-block:: python

   >>> inforec = records[0]
   >>> inforec.components()
   [dlisio.core.component_block(mnem='TYPE', units='    ', component='CONS'),
    dlisio.core.component_block(mnem='MNEM', units='    ', component='WN  '),
    dlisio.core.component_block(mnem='STAT', units='    ', component='ALLO'),
    dlisio.core.component_block(mnem='PUNI', units='    ', component='    '),
    dlisio.core.component_block(mnem='TUNI', units='    ', component='    '),
    dlisio.core.component_block(mnem='VALU', units='    ', component='15/9-F-15 '),
    dlisio.core.component_block(mnem='MNEM', units='    ', component='CN  '),
    dlisio.core.component_block(mnem='STAT', units='    ', component='ALLO'),
    dlisio.core.component_block(mnem='PUNI', units='    ', component='    '),
    dlisio.core.component_block(mnem='TUNI', units='    ', component='    '),
    dlisio.core.component_block(mnem='VALU', units='    ', component='StatoilHydro')]

As you can see, Information Records are essentially a list of
:class:`dlisio.core.component_block`. Each Component Block contains a specific
piece of information, e.g. a parameter.

Tables in Information Records
.............................

Some Information Records are intended to be read as tables. I.e. each Component
Block is an entry in a table. This can be checked by calling
:func:`dlisio.lis.InformationRecord.isstructured()`:

.. code-block:: python

   >>> inforec.isstructured()
   True

If so, dlisio can create the table for you, in form of a `Numpy Structured Array
<https://numpy.org/doc/stable/user/basics.rec.html>`_. The mnemonics from the
Component Blocks are used as field names (column names):

.. code-block:: python

   >>> inforec.table(simple=True)
   [('WN  ', 'ALLO', '    ', '    ', '15/9-F-15 '),
    ('CN  ', 'ALLO', '    ', '    ', 'StatoilHydro')]

Setting the argument ``simple=True`` means that only the values from the
Component Blocks are used in the table. Setting it to ``False``, which is the
default behavior, means that the entire Component Blocks are put into the
array. This is useful if you e.g. want to preserve other parts of the Component
Blocks, such as units.

.. note::
   The data returned from ``table()`` is the same data as returned from
   ``components()``, it's just formatted differently.

.. _`structured numpy.ndarray`: https://numpy.org/doc/stable/user/basics.rec.html
