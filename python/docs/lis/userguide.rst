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

This returns an instance of :class:`dlisio.lis.physical_file` - a tuple-like
object containing all the Logical Files (LF) in ``myfile.lis``.

.. note::
    If you are unfamiliar with Logical Files and the internal structure of a
    LIS file, please refer to :class:`dlisio.lis.logical_file` and
    :class:`dlisio.lis.physical_file`.

Lets have a closer look at one of the Logical Files returned by load:

.. code-block:: python

   >>> f, *tail = files

The Logical File, ``f``, is an instance of :class:`dlisio.lis.logical_file`
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
