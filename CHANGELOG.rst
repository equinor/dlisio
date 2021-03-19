Changelog
=========
All notable changes to this project will be documented in this file, for a
complete overview of changes, please refer to the git log.

The format is based on `Keep a Changelog`_,
but most notably, without sectioning changes into type-of-change.

0.3.1_ - 2021.03.10
-------------------
* Solves an issue in the Windows deploy pipeline on Appveyor that resulted in
  the pipeline failing to upload the python wheels to PyPi.

0.3.0_ - 2021.03.09
-------------------
* Added an initial pass at a Log Information Standard 79 (LIS79) reader. Like
  the DLIS reader, the new LIS reader is mainly implemented in C/C++ with
  python bindings on top. The reader is not feature complete at this point. But
  it can read most curves, with a few exceptions (see the docs of
  dlisio.lis.curves). Basic metadata such as LIS Header/trailer Records (RHLR,
  RTLR, THLR, TTLR, FHLR, FTLR) can also be read. Support for more complex LIS
  Records such Information Records is not yet added. The LIS reader
  resides in the python submodule ``dlisio.lis``.
* The python module is restructured to accommodate the new LIS reader. Most
  notably, all DLIS related functionality is moved to the submodule
  ``dlisio.dlis``. I.e.  this release breaks the main entry point of dlisio
  ``dlisio.load`` which from this release and onwards is moved to
  ``dlisio.dlis.load``. For a full overview of the restructuring see
  commit ``#736d545``.
* The documentation on readthedocs_ has been given an overhaul to fit the new
  module structure and LIS documentation is added.
* Added support for DLIS NOFORM objects.
* Better debug information for broken DLIS files.
* Better error message when passing a directory as path to ``dlisio.dlis.load``.
* Nicer error message when failing to construct datetime objects due to invalid
  dates in the file.
* Added support for python 3.9
* Dropped support for python 3.5
* Restructuring the C/C++ core of dlisio, please refer to the git log for a
  full overview of the restructuring.
* The C and C++ targets are merged into one target ``dlisio``, and
  ``dlisio-extension`` ceased to exist.

0.2.6_ - 2020.12.16
-------------------
* Fixes a bug that caused ``dlisio.load`` to fail on files >2GB on Windows.
* dlisio can now read data from truncated files, this feature is opt-in.
* dlisio can now read data from files that are padded at the end, this feature
  is opt-in.
* How dlisio handles spec-violations in files is now customisable.
* ``describe()`` includes attributes units
* ``Batch`` has been renamed to ``physicalfile``.
* ``dlis`` has been renamed to ``logicalfile``
* ``dlis.match`` (now ``logicalfile.match``) is deprecated in favor of
  ``logicalfile.find``

0.2.5_ - 2020.10.20
-------------------
* Fixed a bug where dlisio silently misinterpreted vax-floats.
* More robust handling of encoded strings.
* Internal restructuring. Metadata handling is partially moved to C++.

0.2.4_ - 2020.07.27
-------------------
* fixes a bug in ``dl::findoffsets`` that caused an infinite loop for certain
  broken files.

0.2.3_ - 2020.06.19
-------------------
* Fixes a bug in ``dlisio.load()`` that caused it to leak open file handles when
  load failed.
* Added official support and distributed wheels for python 3.8.
* Better error message is reported when attempting to load files which do not
  exist.
* dlisio can now read files which contain empty logical records.
* The cli tool describe.cpp is removed as it has not been maintained and used.

0.2.2_ - 2020.06.15
-------------------
* Fixes a bug in ``dlisio.load()`` that caused it to leak an open file handle.

0.2.1_ - 2020.06.05
-------------------
* Fixes a bug in the build script that creates the macos wheels. The lfp
  library was not properly included, resulting in an import error when
  importing dlisio.

0.2.0_ - 2020.06.04
-------------------
* dlisio can now read files wrapped in Tape Image Format (tif).
* dlisio can now read files that do not contain a Storage Unit Label.
* The numpy array returned by ``frame.curves()`` can now be indexed with
  fingerprints in addition to the normal mnemonic indexing. Fingerprints are a
  more reliable indexing method as these are required to be unique by the
  standard, unlike mnemonics. This should mainly be of interest to automation
  pipelines where reliable indexing is key.
* dlisio can now read frames with duplicated channels. This behavior is
  explicitly forbidden by the spec. However, it is frequently violated. By
  default, ``frame.curves()`` still fails, but this can now be bypassed with
  ``strict=False``.
* dlisio no longer accepts files where the last Visible Record is truncated, but
  the last Logical Record is intact. Support for such truncated files was
  never intended in the first place, but happened to work.
* ``Channel.curves()`` fails more gracefully when there is no recorded curve
  data.
* The documentation has been revamped and new sections focusing on
  understanding the content and structure of dlis-files are added.
* Fixes a bug that caused ``channel.curves()`` to use too much memory.
* Fixes a bug that causes ``dlisio.load()`` to fail if the file contained
  encrypted fdata record(s).
* Fixes a bug that caused ``dlisio.load()`` to fail if the obname of a fdata
  record spanned multiple Visible Records.
* Fixes a bug that re-read unknown objects from disk even if they were cached
  from previous reads.

0.1.16_ - 2020.01.16
--------------------
* Fixes a bug were ``dlisio.load()`` did not properly close the memory mapping to
  the file when loading failed.
* Fixes a bug where ``dlis.match()`` and ``dlis.object()`` returned the same object
  multiple times under certain circumstances.
* ``dlis.describe()`` again includes the object-count of each object-type.
* ``dlisio.load()`` now warns if a file contains ``Update``-objects. The current lack
  of support for such objects means that dlisio may wrongfully present data in
  files with ``Update``-objects.
* There is now a list of organization codes on readthedocs
* Fixes a bug in the Process-docs

0.1.15_ - 2019.12.18
--------------------
* Metadata objects are now parsed and loaded when needed, rather than all at
  once in ``dlisio.load()``. This is not directly observable for the user, other
  than it improves performance for ``dlisio.load()``. For files with a lot of
  metadata, the performance gain is huge.
* dlisio can now read even more curve-data. Specifically, where multiple FDATA
  (rows) are stored in the same IFLR.
* The array from ``Frame.curves()`` now includes FRAMENO as the first column.
  FRAMENO are the row numbers as represented in the file. It might happen that
  there are missing rows or that they are out-of-order in the file, that is now
  observable by inspecting FRAMENO.
* Better support for non-ascii strings. It is now possible to tell dlisio which
  string encodings to try if decoding with 'utf-8' fails. Supply a list of
  encodings o ``set_encodings()`` and dlisio will try them in order.
* ``Frame.index`` now returns the Channel mnemonic, not the ``Channel``-object.
* ``Channel.index`` is removed.
* Validated types are now represented as tuples, not lists.
* Fixes a bug were microseconds in datetime objects were interpreted as
  milliseconds.
* Better error message when incomplete Channels objects cause parsing of curves
  to fail as a result.

0.1.14_ - 2019.10.14
--------------------
* dlisio has learned to read curves with variable length data types. Thus,
  every data-type that the standard allows for curves is now supported by
  dlisio.
* ``Frame``- and ``Channel``-objects now have an index-property. ``index`` returns the
  ``Channel``-object that serves as the index-channel for the given Frame/Channel.

0.1.13_ - 2019.10.3
-------------------
* The sphinx documentation on readthedocs_ has a few new sections: About the
  project, an introduction to some dlis-concepts and a quick guide to help new
  users to get started with dlisio.
* API documentation has seen some improvements as well. The ``dlis``-class
  documentation is revamped to better help users to work with logical files and
  accessing objects. ``Frame`` and ``Channel`` are more thoroughly documented, and
  more examples on how to work with curve data are provided.
* Direct access to specific objects has been made more convenient with
  ``dlis.object()``.
* ``dlis.match()`` is no longer case sensitive.
* ``dlis.fileheader`` now returns the ``Fileheader``-object directly, not wrapped as
  dict_values.
* ``dlis.objects`` has been removed
* CircleCI is added to the ci-pipeline for building and testing on linux
* Python test suite has seen some refactoring
* It is now possible to build the python module with ``setup.py``, provided the
  core library is already installed on the system.

0.1.12_ - 2019.08.15
--------------------
* Output a readable summary of any metadata-object, logical file or batch-object
  with ``.describe()``.
* Access to curves directly through ``Frame``- and ``Channel``-objects.
* dlisio has learned to read the following metadata-objects: ``Process``, ``Path``,
  ``Splice``, ``Well reference point``, ``Group``, ``Message``, ``Comment``.
* ``dlis.match()`` lets you search for objects with a regular expression.
* dlisio now reads even more files. Restrictions such as number-of-objects in an
  object_set and missing representation codes in templates have been lifted.
* The parsing routine has seen some improvements. This includes giving the user
  more freedom to customize object-parsing.
* Multidimensional metadata attributes are handled correctly.
* ``BasicObject.update_stash`` has been removed.
* ``dlis.getobjects()`` has been removed.
* ``dlis.object_set`` has been renamed to ``dlis.indexedobjects``.
* ``Computation.source`` is now a scalar, not vector.
* ``BasicObject``'s ``type`` and ``attic`` is now attributes, not properties.
* Objects are allowed to have empty ids (name/mnemonic).
* The API documentation has seen some minor updates.
* dlisio uses endianness.h rather than its own implementation.
* Some of the binary test files have been simplified.
* core functionality such as ``findfdata``, ``findsul``, ``findvrl``, ``findoffsets`` and
  ``stream.at`` are more thoroughly tested.
* Parts of the Python test suite have been refactored.
* Fixed a bug were long obnames were allocated insufficient memory.
* Fixed a bug were multi-dimensional fdata were interpreted incorrectly.
* Fixed a bug that caused incorrectly partitioning from physical- to logical
  file(s).
* Fixed a bug that caused parsing of a encrypted logical record to fail.

0.1.11_ - 2019.06.04
--------------------
* Support for logical files - dlisio now partitions the loaded physical file
  into logical files. This has resulted in a behavioral change were
  ``dlisio.load()`` now returns a tuple-like object of n-logical files.

.. _`Keep a changelog`: https://keepachangelog.com/en/1.0.0/
.. _readthedocs: https://dlisio.readthedocs.io/en/stable/

.. _0.3.1: https://github.com/equinor/dlisio/compare/v0.3.0...v0.3.1
.. _0.3.0: https://github.com/equinor/dlisio/compare/v0.2.6...v0.3.0
.. _0.2.6: https://github.com/equinor/dlisio/compare/v0.2.5...v0.2.6
.. _0.2.5: https://github.com/equinor/dlisio/compare/v0.2.4...v0.2.5
.. _0.2.4: https://github.com/equinor/dlisio/compare/v0.2.3...v0.2.4
.. _0.2.3: https://github.com/equinor/dlisio/compare/v0.2.2...v0.2.3
.. _0.2.2: https://github.com/equinor/dlisio/compare/v0.2.1...v0.2.2
.. _0.2.1: https://github.com/equinor/dlisio/compare/v0.2.0...v0.2.1
.. _0.2.0: https://github.com/equinor/dlisio/compare/v0.1.16...v0.2.0
.. _0.1.16: https://github.com/equinor/dlisio/compare/v0.1.15...v0.1.16
.. _0.1.15: https://github.com/equinor/dlisio/compare/v0.1.14...v0.1.15
.. _0.1.14: https://github.com/equinor/dlisio/compare/v0.1.13...v0.1.14
.. _0.1.13: https://github.com/equinor/dlisio/compare/v0.1.12...v0.1.13
.. _0.1.12: https://github.com/equinor/dlisio/compare/v0.1.11...v0.1.12
.. _0.1.11: https://github.com/equinor/dlisio/compare/v0.1.10...v0.1.11
