Errors reference
================

If you received an error while working with dlisio, you might find explanation
for it in this section.

.. note::  This section doesn't describe *all* the errors you might see and not
           *all* the reasons why these messages appear, but the most *common*
           ones.

.. note::  Please note that error messages might get updated while this sections
           might not be, so treat them more as a hint than as a strict
           guideline.

.. note::  Refer to :class:`dlisio.errors.ErrorHandler` to juggle with the way
           errors are dealt with, if possible.

.. contents:: :local:


Installation
------------

ModuleNotFoundError: No module named 'dlisio'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Python that you use can't find dlisio installed among its packages.
Make sure that you use correct combination of python/pip if several versions are
installed on your system. ::

    python3 -m pip install dlisio
    python3 -c "import dlisio"

Use
---

Segmentation fault
^^^^^^^^^^^^^^^^^^
While running dlisio you might see message similar to this:

.. code-block:: text

    Process finished with exit code 139 (interrupted by signal 11: SIGSEGV)

This might happen for two reasons: incorrect use of the library or actual
issue in dlisio.

First of all make sure that dlisio objects are not closed. dlisio reads certain
data only when requested. Hence if file handle is closed too early, segfault
might occur (in older versions of dlisio *iostream error* was reported).

File will happen to be closed if *with* statement is used incorrectly::

    with dlisio.load(path) as (f, *_):
        pass
    # at this moment f is already closed and shouldn't be used
    for frame in f.frames:
        frame.curves()

If you do not believe segfault to be caused by unclosed handles, you might want
to log an issue to `dlisio issues`_.

Memory leak
^^^^^^^^^^^
If while running dlisio you notice that memory usage is significantly higher
than the size of the file you are processing, it might indicate that library is
used inefficiently or there is a bug in dlisio.
If you suspect it to be dlisio problem, please log an issue to `dlisio issues`_.

Poor performance
^^^^^^^^^^^^^^^^
If you notice significant lag in dlisio performance, it might be caused by
library or (accidentally) inefficient use of the library by users.

As of version 0.2.5, dlisio doesn't cache objects in Python anymore. Thus every
query causes fetching objects from C++ anew. In large quantities it becomes
time-consuming. If so, performance problems might be mitigated by refactoring
user's code.

If you believe that performance lag is caused directly by dlisio, please log an
issue to `dlisio issues`_.

File lock is not released
^^^^^^^^^^^^^^^^^^^^^^^^^
Might be visible when you attempt to remove file from the system, but lock error
is reported. This might indicate that you never close the dlis objects or there
is a bug in dlisio.

Remember that every file opened by dlisio must be closed.
``with`` context manager will do it for you::

    with dlisio.load(path) as lfs:
        # do something

If you do not want to use context manager, remember to close file explicitly
when you are done with it::

    lfs = dlisio.load(path)
    # do something
    lfs.close()

If you are sure that all filehandles are closed, please log an issue to
`dlisio issues`_.

Errors on load
--------------
Load errors are in general non-recoverable and prevent user from further
reading the file.

could not find visible record envelope pattern
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  searched 200 bytes, but could not find visible record envelope pattern
  ``0xFF 0x01``

This error might indicate:

* File is not actually a .dlis file
* File contains trash at the start or at the end of the file

incorrect format version
^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  rp66: Incorrect format version in Visible Record 1234

This error might indicate:

* File is missing a chunk of data in the middle
* File is completely zeroed-out from certain point
* File contains a zeroed-out chunk of data
* File is a non-standard TIF file

too short logical record
^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  Too short logical record. Length can't be less than 4, but was 0

This error might indicate:

* File is completely zeroed-out from certain point
* File contains a zeroed-out chunk of data

unexpected EOF when reading / file truncated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  rp66: unexpected EOF when reading record - got 1234 bytes, expected
  there to be 5678 more

.. code-block:: text

  File truncated ...

This error might indicate:

* File is incomplete, unknown amount of information is missing from the
  end

logical record segment expects successor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

  End of logical file, but last logical record segment expects successor

.. code-block:: text

  Reached EOF, but last logical record segment expects successor

This error might indicate:

* Logical file is incomplete, end of file or new logical file follows.

Parsing errors
--------------

Some errors which occur during parsing of objects or curves.

error parsing / unexpected end-of-record
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  error parsing object descriptor

.. code-block:: text

  unexpected end-of-record

.. code-block:: text

  unexpected end-of-record in template

These (and similar) errors indicate that file breaks specification in a way that
is too ambiguous. When encountered, dlisio no longer knows how to interpret data
that follows, so it stops processing data further.

Some common situations that might lead to this error:

* Incorrect invariant attribute in template
* Invalid LRS padbytes value
* Fileheader set is declared to be named, but is not

field occurs more than once
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  field 'DEPTH.1.0' occurs more than once

Happens when accessing curves. According to specification, every channel may
appear in the frame once and only once.
So this error may indicate:

* Something is broken in frame-channel relationships and you should be cautious
  with trusting the data
* Channel is repeated for user convenience. It's likely the case if repeated
  channel can be assumed to be index of the frame, like for example "DEPTH"

To bypass this error call::

  frame.curves(strict=False)

fmtstr would read past end
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  corrupted record: fmtstr would read past end

Error happens when reading curves. It indicates that more curves data is
expected than there is actually present. dlisio doesn't know what precisely
caused data to be incorrect, hence can't recover from it.

Possible reasons:

* Invalid LRS padbytes value

day is out of range/month must be
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  day is out of range for month

.. code-block:: text

  month must be in 1..12

Standard Python errors on creation of invalid date. Error would mean that date
stored in the file is broken, like (1990, 0, 0, 0, 0, 0, 0).


Warnings
--------

unable to decode
^^^^^^^^^^^^^^^^
.. code-block:: text

  UnicodeWarning: unable to decode string

Data in the file wasn't written in UTF-8 as it should have been. dlisio doesn't
know which encoding was used, so it doesn't know how to represent this data
correctly. You might experiment with :py:func:`dlisio.set_encodings`.

.. hint::  If unsure, use "latin1". It's likely to present you with relevant
           result.

.. _`dlisio issues`: https://github.com/equinor/dlisio/issues
.. _`RP66`: http://w3.energistics.org/rp66/V1/Toc/main.html
