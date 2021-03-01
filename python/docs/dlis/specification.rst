DLIS Specification
==================

dlis is a binary file format for well logs, developed by Schlumberger in the
late 80's and published by the American Petroleum Institute (API) in 1991. In
1998 the stewardship was handed off to Petrotechnical Open Software Corporation
(POSC), now known as energistics [1]_


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

.. [1] POSC, https://www.energistics.org/
