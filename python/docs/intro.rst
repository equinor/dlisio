About the project
=================

Welcome to dlisio. dlisio is a python package for reading Digital Log
Interchange Standard (DLIS) v1. Version 2 exists, and has been around for
quite a while, but it is our understanding that most dlis files out there are
still version 1. Hence dlisio's focus is put on version 1 [1]_, for now.

dlisio is an attempt at abstracting away a lot of the pain of dlis and give
access to the data in a simple and easy-to-use manner. It gives the user the
ability to work with dlis-files without having to know the details of the
standard itself. Its main focus is making the data accessible while putting
little assumptions on how the data is to be used.

dlisio is written and maintained by Equinor ASA as a free, simple, easy-to-use
library to read well logs that can be tailored to our needs, and as a
contribution to the open-source community.

Please note that dlisio is still in alpha, so expect breaking changes between
versions.

Digital Log Interchange Standard (DLIS)
=======================================

dlis is a binary file format for well logs, developed by Schlumberger in the
late 80's and published by the American Petroleum Institute (API) in 1991. It
is now the Petroleum Open Standards Consortium (POSC) [2]_ that has the
stewardship.

When developing dlis standard, the main emphasis was put on easy writing. The
files are structured in such a way that data can be written directly while
acquiring the logs. This is very handy for the producers of the files, and
equally tedious for the consumer that wants to read them later on.  Additionally
it is a very tolerant standard. It specifies general data-structures within the
file, such as channels and frames, but allows the producers to modify these to
fit their needs. It also allows for completely new structures, not defined by
the standard itself, such as vendor-specific object-types. This all sums up to
a fairly complex standard with a lot of quirks and weirdness to it.  It is safe
to say that dlis a particularly difficult format to work with.

Physical and logical files
--------------------------

The dlis standard distinguishes between physical files and logical files. A
physical file would be a .dlis file. A logical file, on the other hand, is a
collection of data that are logically connected. Typically this can be all
measurements and metadata gathered at one run. A physical file may contain
multiple logical files, where each logical file is completely independent of
the other logical files::

                            physical file (.dlis)
            --------------------------------------------------------
           | logical file 0 | logical file 1 | ... | logical file n |
            --------------------------------------------------------

dlisio's main entrypoint, :py:func:`dlisio.load()` takes a physical file and
returns a tuple-like object with all the logical files.

Logical files can be thought of as a pool of metadata and curve-values that all
are related in some way. Some common metadata objects are Fileheader, Origin,
Frame, Channel, Tool, Parameter and Calibration. For a full list of all metadata
objects, see :ref:`Object types`::

                            logical file
            ------------------------------------------------------
           | Fileheader | Origin | Frame1 | Channel | Frame2 | .. |
            ------------------------------------------------------

This is a simplified illustration of the logical file structure, but to work
with dlis-files this is pretty much how you should think of logical files. To
see how to access specific objects, check out :py:class:`dlisio.dlis`

Curves
------

The primary data of a dlis-file are curves (or channels). A curve is the
recorded measurements from an instrument indexed against an axis, typically
depth or time. In dlisio, curves are accessed through Frames or
Channel-objects.

Channel objects contain both the metadata about the curve, and the actual curve
data. A Frame is a gathering of multiple Channels, typically acquired at the
same run.  Both Frame- and Channel-objects implement a :code:`curves()`-method
that returns the relevant curve(s). The primary data type for curves is a
structured numpy.ndarray [3]_. All examples use ``np`` for the numpy namespace.
This enables quick and easy mathematical operations on the data you care about.


Please refer to :py:class:`dlisio.plumbing.Channel` and :py:class:`dlisio.plumbing.Frame`

.. [1] API RP66 v1, http://w3.energistics.org/RP66/V1/Toc/main.html
.. [2] POSC, https://www.energistics.org/
.. [3] Numpy, structured arrays, https://docs.scipy.org/doc/numpy-1.16.0/user/basics.rec.html
