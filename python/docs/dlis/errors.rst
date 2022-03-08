Common errors
=============

If you received an error while working with dlis file, you might find
explanation for it in this section.

.. note::  Refer to :class:`dlisio.common.ErrorHandler` for possible remedies.

Errors on load
--------------

Although there are still some features of the DLIS spec that dlisio doesn't
implement full support for, it should be able to load all dlis files that
conform to the spec.

From experience we know that there exists a lot of files out there that don't
strictly adhere to the spec, and these might cause load to fail. It's rather
common that files are truncated, the file is zeroed out from some point or that
there are some extra "trash" bytes somewhere in the file. All of which can throw
dlisio parsing routines off. Hence described errors are mostly manifestations of
the same set of issues. The exact error text is dependent on where in the file
the issue occurs.

Load errors are in general non-recoverable and prevent user from further reading
the file. However they can be bypassed by using
:class:`dlisio.common.ErrorHandler` which helps to read the file up to the point
of failure.

could not find visible record envelope pattern
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  searched 200 bytes, but could not find visible record envelope pattern
  `0xFF 0x01`

This error might indicate:

* The file is not actually a .dlis file
* The file contains trash at the start or at the end of the file

incorrect format version
^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  rp66: Incorrect format version in Visible Record 1234

This error might indicate:

* The file is completely zeroed-out from certain point
* The file contains a zeroed-out chunk of data
* The file is missing a chunk of data in the middle
* The file is a non-standard TIF file

too short logical record
^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  Too short logical record. Length can't be less than 4, but was 0

This error might indicate:

* The file is completely zeroed-out from certain point
* The file contains a zeroed-out chunk of data

unexpected EOF when reading / file truncated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  rp66: unexpected EOF when reading record - got 1234 bytes, expected
  there to be 5678 more

.. code-block:: text

  File truncated ...

This error might indicate:

* The file is incomplete, unknown amount of information is missing from the
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

These (and similar) errors indicate that the file breaks specification in a way
that is too ambiguous. When encountered, dlisio no longer knows how to interpret
data that follows, so it stops processing data further.

Some common situations that might lead to this error:

* Incorrect invariant attribute in template
* Invalid LRS padbytes value
* Fileheader set is declared to be named, but is not

field occurs more than once
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  field 'DEPTH.1.0' occurs more than once

According to specification, every channel may appear in the frame once and only
once.
So this error may indicate:

* Channel is repeated for user convenience. It's likely the case if repeated
  channel can be assumed to be index of the frame, like for example "DEPTH"
* Something is broken in frame-channel relationships and you should be cautious
  with trusting the data

To bypass this error call::

  frame.curves(strict=False)

fmtstr would read past end
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: text

  corrupted record: fmtstr would read past end

There is less data than what the metadata claims there to be. Either the
metadata is incorrect or the file is missing data, or both. It's not obvious
which one it is. The inconsistency between the metadata and the raw data makes
it impossible for dlisio to correctly parse the data. Hence there is no recovery
from this.

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
correctly. You might experiment with :py:func:`dlisio.common.set_encodings`.

.. hint::  If unsure, try "latin1". It's likely to present you with relevant
           result.
