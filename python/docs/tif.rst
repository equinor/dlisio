Tape Image Format (TIF)
=======================

From version 0.1.17 dlisio supports Tape Image Format (TIF) files. TIF is a
file format used to wrap other file formats, like DLIS, such that the file can be
read by tape readers. A TIF'd DLIS-file is simply a regular DLIS-file plus some
extra information that tape readers rely on in order to read the file. This
information is of no use to the consumer of the file and **there is no
semantic distinction between a regular DLIS-file and a TIF'd DLIS-file**.

Unlike other known DLIS-readers, dlisio does not require you to run the file
through a tapemark-remover prior to opening it or to explicitly inform dlisio
whether or not the passed file is DLIS or TIF. In practice this means that you
as a consumer of dlis-files never need to know nor care whether your file is
TIF'd or not, and can always open the file as if it was a regular DLIS:

.. code-block:: python

   with dlisio.load('tif.dlis') as files:
      pass
