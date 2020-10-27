Physical and logical files
--------------------------

The dlis standard distinguishes between physical files and logical files. A
physical file would be a .dlis file. A logical file, on the other hand, is a
collection of data that are logically connected. Typically this can be all
measurements and metadata gathered at one run. A physical file may contain
multiple logical files, where each logical file is independent of the other
logical files::

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
see how to access specific objects, check out :py:class:`dlisio.logicalfile`
