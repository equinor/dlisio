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

This returns an instance of :class:`dlisio.lis.PhysicalFile` - a tuple-like
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


Read the curves
---------------

Within a LIS Logical File, curves are defined and organized by Data Format
Specification Records (DFSR). A DFSR defines a set of channels/curves that are
sampled along the same index. There might be multiple Data Format Specification
Records in a Logical File, each defining different channels/curves and index.

Read all the curve data by passing each DFSR to :func:`dlisio.lis.curves`:

.. code-block:: python

    >>> for format_spec in f.data_format_specs:
    ...    _ = lis.curves(f, format_spec)

.. note::
   LIS79 opens for the presence of duplicated DFSR, for redundancy. Currently,
   dlisio has no support for identifying redundant DFSRs, and curves() will
   return empty arrays for these.


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
