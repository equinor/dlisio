# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
but most notably, without sectioning changes into type-of-change.

## [0.1.14] - 2019.10.14
* dlisio have learned to read curves with variable length data types. Thus,
  every data-type that the standard allows for curves are now supported by
  dlisio.
* Frame and Channel-objects now has a index-property. index returns the channel
  object that serves as the index-channel for the given Frame-/Channel.

## [0.1.13] - 2019.10.3
* The sphinx documentation on readthedocs has a few new section: About the
  project, an introduction to some dlis-concepts and a quick guide to help new
  users to get started with dlisio.
* API documentation has seen some improvements as well. The dlis-class
  documentation is revamped to better help users to work with logical files and
  accessing objects. Frame and Channel are more thoroughly documented, and
  provides more examples on how to work with curve data.
* Direct access of a specific objects has been made more convenient with
  dlis.object()
* dlis.match no longer casesensitive
* The fileheader interface has changed. The fileheader is now directly
  accessible through dlis.fileheader
* dlis.objects has been removed
* CircleCI is added to the ci-pipeline for building and testing on linux
* Python test suite have seen some refactoring
* It is now possible to build the python module with setup.py, provided the
  core library is already installed on the system.

## [0.1.12] - 2019.08.15
* Output a readable summary of any metadata-object, logical file or batch-object
  with describe
* Access to curves directly through Frame- and Channel-objects
* dlisio has learned to read the following metadata-objects: Process, Path, Splice, Well
  Reference Point, Group, Message, Comment
* Match objects with a regular expression
* dlisio now read even more files. Restrictions such as number-of-objects in an
  object_set and missing representation codes in templates have been lifted.
* The parsing routine have seen some improvments. This includes giving the user
  more freedom to customize object-parsing
* Multidimensional metadata attributes are handled correctly
* BasicObject's updata_stash has been removed
* dlis's getobjects() has been removed
* dlis.object_set has been renamed to dlis.indexedobjects
* Computation.source is now a scalar, not vector
* BasicObject's type and attic is now attributes, not properties
* Objects are allowed to have empty ids (name/mnemonic)
* The API documentation have seen some minor updates
* dlisio uses endianness.h rather than its own implementation
* Some of the binary test files has been simplified
* core functionality such as findfdata, findsul, findvrl, findoffsets and
  stream.at are more thoroughly tested
* Parts of the Python test suite have been refactored
* Fixed a bug where long obnames where allocated insufficient memory
* Fixed a bug where multi-dimensional fdata where interpreted incorrectly
* Fixed a bug that caused incorrectly partitioning from physical- to logical
  file(s)
* Fixed a bug that caused parsing of a encrypted logical record to fail

## [0.1.11] - 2019.06.04
* Support for logical files - dlisio now partitions the loaded physical file
  into logical files. This have resulted in a behavioral change where load now
  returns a tuple-like object of n-logical files.

[0.1.14]: https://github.com/equinor/dlisio/compare/v0.1.13...v0.1.14
[0.1.13]: https://github.com/equinor/dlisio/compare/v0.1.12...v0.1.13
[0.1.12]: https://github.com/equinor/dlisio/compare/v0.1.11...v0.1.12
[0.1.11]: https://github.com/equinor/dlisio/compare/v0.1.10...v0.1.11
