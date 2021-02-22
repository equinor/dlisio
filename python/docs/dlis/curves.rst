.. currentmodule:: dlisio.plumbing

DLIS Curves
===========

The primary data of a dlis-file are curves, also referred to as channels.
Typically a curve is the recorded measurements taken along the borehole,
indexed against an axis, like depth or time. But a curve can also be a
computation of some sort, e.g. a calibrated version of a measured curve.

In dlisio, curves are accessed through :class:`Frame`- or
:class:`Channel`-objects, by calling their :func:`curves` methods.  The primary
data type for curves is `structured numpy.ndarray`_.  This enables quick and
easy mathematical operations on the data you care about.

Frame-objects
-------------

Curves are organized in frames. Conceptually, a frame can be seen as a table of
data where each column is a curve, like in the time-indexed frame below.
Frames almost always have an index channel that provides the position in e.g.
depth or time at which the rest of the values in the row were measured. Each
frame usually corresponds to a log run, but otherwise frames impose little
structure except grouping channels that have a common index. There is no
restrictions on the number of channels per frame, or the number of frames in a
file.

Frames are described by :class:`Frame`-objects. These contain a list of
:class:`Channel`-objects, which describe the individual curves in more detail.
Frame objects also contain additional information about the index channel, such
as its min/max values, spacing, direction and type-of-index.  See
:class:`Frame` for a full list of its attributes.

.. csv-table:: _`A TIME indexed frame`
   :header: "FRAMENO", "TIME", "TDEP", "ETIM", "LMVL", "UMVL", "CFLA", "OCD"
   :widths: 10, 20, 20, 20, 20, 20, 20, 20

    1 , 16677259 , 852606.0 , 0.  , 585 , 635 , 18 , 6789.05
    2 , 16677659 , 852606.0 , 0.4 , 585 , 635 , 18 , 6789.05
    3 , 16678059 , 852606.0 , 0.8 , 585 , 635 ,  0 , 6789.05
    4 , 16678459 , 852606.0 , 1.2 , 585 , 635 ,  0 , 6789.05
    5 , 16678859 , 852606.0 , 1.6 , 585 , 635 ,  0 , 6789.05

.. note::
   FRAMENO: The first column of every Frame is always FRAMENO, which is the row
   number. Generally FRAMENO is not that interesting, but it can aid in
   debugging strange-looking curve-data. For example if you are suspecting that
   some of the data is missing (or even is out-of-order).

Channel-objects
---------------

Curve-metadata is recorded in :class:`Channel`-objects. Each
:class:`Channel`-object describes a single curve, e.g. TDEP, GR, VDL, WF1, etc.
The metadata includes a description, the dimension of each sample and their
units, which :class:`Frame` the curve belongs to and the source of the curve.
The source is the entity that produced the curve. For measured curves, that is
typically a :class:`Tool`.  For computed curves, the source might be a
:class:`Computation`.  Additionally, :class:`Channel` contains a list of
property indicators. These indicate the general intrinsic properties of the
Channel. Some examples are MEASURED, COMPUTED, DEPTH-MATCHED and AVERAGED.
`Appendix C`_ of RP66v1 defines the full list of property indicators with
descriptions.

N-dimensional curve samples
---------------------------

By far the most common case is that each channel has scalar samples i.e.  a
single measured numerical value per row, however RP66v1 allows each sample to
be a multi- dimensional array. For example, this is common for ultrasonic logs,
where some channels contain a one-dimensional array of values per row,
representing measurements made at different azimuthal angles. For other
channels each sample may even be a 2- or 3-dimensional array.

RP66v1 imposes no limit on the dimensionality that a channel-sample can have,
nor does dlisio.

.. note::
   Thanks to numpy's `structured numpy.ndarray`_, dlisio is able to support
   n-dimensional curves of any shape and form. However, other popular formats
   such as Pandas DataFrame or CSV are only able to handle tabular data, i.e.
   frames where all channels have scalar sample values. Hence, conversion to
   these formats may not always be possible.

Channels with no data
---------------------

It is not uncommon for files to have :class:`Channel`-objects describing
curves that are not present in the file. I.e. there is metadata describing a
curve, but the curve itself is missing.

This typically happens because metadata like :class:`Tool`-objects and all the
curves it can produce is recorded prior to the acquisition. However when
acquisition starts only a subset of the channels is actually recorded, but the
metadata for the unused channels are never removed.

.. note::
   Calls to :func:`Channel.curves()` and :attr:`Channel.frame` returns
   :code:`None` when there is no recorded curve data.

.. _`structured numpy.ndarray`: https://numpy.org/doc/stable/user/basics.rec.html
.. _`Appendix C`: http://w3.energistics.org/rp66/V1/rp66v1_appc.html
