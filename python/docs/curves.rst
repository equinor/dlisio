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
structured numpy.ndarray [1]_. All examples use ``np`` for the numpy namespace.
This enables quick and easy mathematical operations on the data you care about.


Please refer to :py:class:`dlisio.plumbing.Channel` and :py:class:`dlisio.plumbing.Frame`

.. [1] Numpy, structured arrays, https://docs.scipy.org/doc/numpy-1.16.0/user/basics.rec.html
