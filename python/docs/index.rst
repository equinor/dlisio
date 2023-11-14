.. image:: ../../dlisio-icon.svg
   :width: 400
   :alt: dlisio icon
   :align: center

Welcome to dlisio. dlisio is a python package for reading Digital Log
Interchange Standard (DLIS) v1. Version 2 exists, and has been around for quite
a while, but it is our understanding that most dlis files out there are still
version 1. Hence dlisio's focus is put on version 1 [1]_, for now.

As of version 0.3.0, dlisio is extended to also read Log Information Standard 79
(LIS79) [2]_. An extended version of the LIS79 standard called LIS84/Enhanced LIS
exists, but this version is currently not supported by dlisio.

Before you get started we recommended that you familiarize yourself with some
basic concepts of the DLIS- and LIS file formats. These are non-trivial formats
and some knowledge about them is required for effective work. A good place to
start is the user guides: :ref:`DLIS User Guide` and :ref:`LIS User Guide`.

.. warning::
    DLIS and LIS files are often "wrapped" in "container"-formats. Essentially
    this is just extra information needed for the file to be correctly read by
    a tape-reader and does not add anything to the well-logs themselves. Maybe
    the most common one is the TapeImageFormat (TIF). TIF is automatically
    detected by dlisio and both DLIS and LIS files wrapped in TIF can be read
    without any special care from the user. There are other container formats
    or TIF-modifications with unknown origins that dlisio does not support.
    **DLIS and LIS files using these formats or modifications will fail to
    read.**

.. [1] API RP66 v1, https://energistics.org/sites/default/files/RP66/V1/Toc/main.html
.. [2] LIS79, https://www.energistics.org/sites/default/files/2022-10/lis-79.pdf

Installation
============

dlisio can be installed with `pip <https://pip.pypa.io>`_

.. code-block:: bash

    $ python3 -m pip install dlisio

Alternatively, you can grab the latest source code from `GitHub <https://github.com/equinor/dlisio>`_.

About the project
=================

dlisio attempts to abstract away a lot of the pain of LIS and DLIS and give
access to the data in a simple and easy-to-use manner. It gives the user the
ability to work with these files without having to know *all* the details of the
standard itself. Its main focus is making the data accessible while putting
little assumptions on how the data is to be used.

dlisio is written and maintained by Equinor ASA as a free, simple, easy-to-use
library to read well logs that can be tailored to our needs, and as a
contribution to the open-source community.

dlisio is divided into 3 subpackages:

- :mod:`dlisio.dlis`, :ref:`rp66`
- :mod:`dlisio.lis` , :ref:`LIS`
- :mod:`dlisio.common`, :ref:`Common API Reference`

Table of Contents
=================

.. toctree::
   :maxdepth: 1

   changelog

.. toctree::
   :caption: Digital Log Interchange Standard
   :name: rp66
   :maxdepth: 3

   dlis/specification
   dlis/userguide
   dlis/metadata
   dlis/curves
   dlis/api
   dlis/errors
   dlis/vendors

.. toctree::
   :caption: Log Interchange Standard
   :name: LIS

   lis/specification
   lis/userguide
   lis/api

.. toctree::
   :caption: Miscellaneous
   :name: misc
   :maxdepth: 3

   common-api
   logging

Indices and tables
==================

* :ref:`genindex`
