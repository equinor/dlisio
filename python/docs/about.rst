About the project
=================

Welcome to dlisio. dlisio is a python package for reading Digital Log
Interchange Standard (DLIS) v1. Version 2 exists, and has been around for
quite a while, but it is our understanding that most dlis files out there are
still version 1. Hence dlisio's focus is put on version 1 [1]_, for now.

dlisio attempts to abstract away a lot of the pain of dlis and gives
access to the data in a simple and easy-to-use manner. It gives the user the
ability to work with dlis-files without having to know the details of the
standard itself. Its main focus is making the data accessible while putting
little assumptions on how the data is to be used.

dlisio is written and maintained by Equinor ASA as a free, simple, easy-to-use
library to read well logs that can be tailored to our needs, and as a
contribution to the open-source community.

Please note that dlisio is still in alpha, so expect breaking changes between
versions.

.. [1] API RP66 v1, http://w3.energistics.org/RP66/V1/Toc/main.html


Installation
============

dlisio can be installed with `pip <https://pip.pypa.io>`_

.. code-block:: bash

    $ python3 -m pip install dlisio


Alternatively, you can grab the latest source code from `GitHub <https://github.com/equinor/dlisio>`_.
