Common API Reference
====================

Strings and encodings
---------------------
.. autofunction:: dlisio.set_encodings
.. autofunction:: dlisio.get_encodings

Open
----
.. autofunction:: dlisio.open

Error handling
--------------

.. note::
   Although the error-handling features of dlisio are not tied to a specific
   file format, it's currently only used by the DLIS reader.

.. autoclass:: dlisio.errors.ErrorHandler()
.. autoclass:: dlisio.errors.Actions()

