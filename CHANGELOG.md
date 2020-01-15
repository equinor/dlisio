# Changelog
All notable changes to this project will be documented in this file, for a
complete overview of changes, please refer to the git log.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
but most notably, without sectioning changes into type-of-change.

## [0.1.16] - 2010.01.16
* Fixes a bug where `dlisio.load` did not properly close the memory mapping to
  the file when loading failed.
* Fixes a bug where `dlis.match` and `dlis.object` returned the same object
  multiple times under certain circumstances.
* `dlis.describe()` again includes the object-count of each object-type.
* `dlisio.load` now warns if a file contains `Update`-objects. The current lack
  of support for such objects means that dlisio may wrongfully present data in
  files with `Update`-objects.
* There is now a list of organization codes on readthedocs
* Fixes a bug in the Process-docs

## [0.1.15] - 2019.12.18
* Metadata objects are now parsed and loaded when needed, rather than all at
  once in `dlisio.load()`. This is not directly observable for the user, other
  than it improves performance for `dlisio.load()`. For files with a lot of
  metadata, the performance gain is huge.
* dlisio can now read even more curve-data. Specifically, where multiple FDATA
  (rows) are stored in the same IFLR.
* The array from `Frame.curves()` now includes FRAMENO as the first column.
  FRAMENO are the row numbers as represented in the file. It might happen that
  there are missing rows or that they are out-of-order in the file, that is now
  observable by inspecting FRAMENO.
* Better support for non-ascii strings. It is now possible to tell dlisio which
  string encodings to try if decoding with 'utf-8' fails. Supply a list of
  encodings to `set_encodings()` and dlisio will try them in order.
* `Frame.index` now returns the Channel mnemonic, not the `Channel`-object.
* `Channel.index` is removed.
* Validated types are now represented as tuples, not lists.
* Fixes a bug where microseconds in datetime objects where interpreted as
  milliseconds.
* Better error message when incomplete Channels objects cause parsing of curves
  to fail as a result.

## [0.1.14] - 2019.10.14
* dlisio has learned to read curves with variable length data types. Thus,
  every data-type that the standard allows for curves is now supported by
  dlisio.
* `Frame`- and `Channel`-objects now have an index-property. `index` returns the
  `Channel`-object that serves as the index-channel for the given Frame/Channel.

## [0.1.13] - 2019.10.3
* The sphinx documentation on
  [readthedocs](https://dlisio.readthedocs.io/en/stable/) has a few new section: About the
  project, an introduction to some dlis-concepts and a quick guide to help new
  users to get started with dlisio.
* API documentation has seen some improvements as well. The `dlis`-class
  documentation is revamped to better help users to work with logical files and
  accessing objects. `Frame` and `Channel` are more thoroughly documented, and
  more examples on how to work with curve data are provided.
* Direct access to a specific objects has been made more convenient with
  `dlis.object()`.
* `dlis.match()` is no longer case sensitive.
* `dlis.fileheader` now returns the `Fileheader`-object directly, not wrapped as
  dict_values.
* `dlis.objects` has been removed
* CircleCI is added to the ci-pipeline for building and testing on linux
* Python test suite has seen some refactoring
* It is now possible to build the python module with `setup.py`, provided the
  core library is already installed on the system.

## [0.1.12] - 2019.08.15
* Output a readable summary of any metadata-object, logical file or batch-object
  with `.describe()`.
* Access to curves directly through `Frame`- and `Channel`-objects.
* dlisio has learned to read the following metadata-objects: `Process`, `Path`,
  `Splice`, `Well reference point`, `Group`, `Message`, `Comment`.
* `dlis.match()` lets you search for objects with a regular expression.
* dlisio now reads even more files. Restrictions such as number-of-objects in an
  object_set and missing representation codes in templates have been lifted.
* The parsing routine has seen some improvements. This includes giving the user
  more freedom to customize object-parsing.
* Multidimensional metadata attributes are handled correctly.
* `BasicObject.update_stash` has been removed.
* `dlis.getobjects()` has been removed.
* `dlis.object_set` has been renamed to `dlis.indexedobjects`.
* `Computation.source` is now a scalar, not vector.
* `BasicObject`'s `type` and `attic` is now attributes, not properties.
* Objects are allowed to have empty ids (name/mnemonic).
* The API documentation has seen some minor updates.
* dlisio uses endianness.h rather than its own implementation.
* Some of the binary test files have been simplified.
* core functionality such as `findfdata`, `findsul`, `findvrl`, `findoffsets` and
  `stream.at` are more thoroughly tested.
* Parts of the Python test suite have been refactored.
* Fixed a bug where long obnames where allocated insufficient memory.
* Fixed a bug where multi-dimensional fdata where interpreted incorrectly.
* Fixed a bug that caused incorrectly partitioning from physical- to logical
  file(s).
* Fixed a bug that caused parsing of a encrypted logical record to fail.

## [0.1.11] - 2019.06.04
* Support for logical files - dlisio now partitions the loaded physical file
  into logical files. This has resulted in a behavioral change where
  `dlisio.load()` now returns a tuple-like object of n-logical files.

[0.1.16]: https://github.com/equinor/dlisio/compare/v0.1.15...v0.1.16
[0.1.15]: https://github.com/equinor/dlisio/compare/v0.1.14...v0.1.15
[0.1.14]: https://github.com/equinor/dlisio/compare/v0.1.13...v0.1.14
[0.1.13]: https://github.com/equinor/dlisio/compare/v0.1.12...v0.1.13
[0.1.12]: https://github.com/equinor/dlisio/compare/v0.1.11...v0.1.12
[0.1.11]: https://github.com/equinor/dlisio/compare/v0.1.10...v0.1.11
