LIS Specification
=================

The Log Information Standard (LIS) [1]_ is a binary file format for well logs,
developed by Schlumberger in 1974. The 1974 version is commonly referred to as
LIS79 or the 79 Subset. An extension to the LIS format was introduced by
Schlumberger in 1984. This version is commonly referred to as LIS84 or Enhanced
LIS. LIS is the predecessor to the :ref:`DLIS Specification`.

When developing LIS standard, the main emphasis was put on easy writing. The
files are structured in such a way that data can be written directly while
acquiring the logs. This is very handy for the producers of the files, and
equally tedious for the consumer that wants to read them later on.

LIS was designed to work with the physical medium tape. Physical tapes have a
lot of limitations that modern computers do not have, such as a fixed storage
size. LIS implements several layers of file segmentation mechanisms to
effectively handle this. Some LIS files also embed access mechanics that let
tape-readers effectively seek the tape. This is all generally uninteresting
information for a modern computer, but as these mechanics are embedded in the
files, modern software still has to account for it. This adds additional layers
of complexity.

.. [1] LIS79, https://www.energistics.org/sites/default/files/2022-10/lis-79.pdf
