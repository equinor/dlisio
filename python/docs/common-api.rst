Common API Reference
====================

Strings and encodings
---------------------
.. autofunction:: dlisio.common.set_encodings
.. autofunction:: dlisio.common.get_encodings

Open
----
.. autofunction:: dlisio.common.open

Error handling
--------------

.. note::
   Although the error-handling features of dlisio are not tied to a specific
   file format, it's currently only used by the DLIS reader.

.. autoclass:: dlisio.common.ErrorHandler()
.. autoclass:: dlisio.common.Actions()

