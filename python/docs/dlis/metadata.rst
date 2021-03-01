.. currentmodule:: dlisio.plumbing

DLIS Metadata
=============

Together with the actual logs, there is often an abundance of metadata related
to the acquisition of the logs. In a DLIS-file metadata is structured into
different :code:`dict`-like objects that describe certain pieces of
information.  RP66v1 defines over 20 object-types. In practice, only a handful
see widespread use. Please refer to the :ref:`DLIS API Reference` to get a full
[1]_ overview of the different object-types. Here are some examples of the
frequently used ones:

:class:`Origin`: Contains general information about the file, and the
circumstances in which it was produced.

:class:`Channel`: Description of a specific curve in the logical file.

:class:`Frame`: A grouping of channels that all share the same index, typically
a logpass. The actual curve-data are accessed through Frames.

:class:`Tool`: Describes a physical tool that was used for the acquisition of
the logs.

:class:`Parameter`: Contains some parameter value and a description of it.

.. currentmodule:: dlisio
.. [1] There is currently a handful of object-types (mostly from Chaper 7:
       semantics: dictionaries of RP66v1) that dlisio does not implement full
       support for. I.e. they are not translated into their own python class,
       but rather use the more generic and rough interface of
       :class:`plumbing.BasicObject`. These rarely see the light of day, but if
       present they can be accessed through :attr:`logicalfile.unknowns`.

Identifying specific objects
----------------------------

.. currentmodule:: dlisio.plumbing.BasicObject

Common for *all* objects are the four fields: :attr:`type`, :attr:`name`
(mnemonic), :attr:`origin` and :attr:`copynumber`.  Together, these form a
unique identifier for the object. RP66v1 states that no two objects from the
*same logical file* can have the same value for all four fields.

.. currentmodule:: dlisio.plumbing

**origin**: The origin field states which origin the object is a part of.
Its interger value implicitly refers to the :class:`Origin`-object that has the
same value in its origin field.

**copynumber**: The copynumber is used to distinguish two objects that otherwise
have an identical signature. E.g. if there are two :class:`Channel` objects
with the same name/mnemonic and both belong to the same origin.

.. currentmodule:: dlisio

To access a specific object use :func:`logicalfile.object`. Or search for objects
matching a regular expression with :func:`logicalfile.find`

.. code-block:: python

   >>> channel = f.object('CHANNEL', 'GR', origin=1, copynumber=0)
   >>> channel.long_name
   'Gamma Ray'

   >>> f.find('CHANNEL', '.*GR.*')
   [Channel(GR), Channel(RGR)]

.. note::
   Note that :func:`logicalfile.object` allows you to ommit the origin and/or
   copynumber, but will raise if it's unable to uniquely identify the object.
   The documentation for :func:`logicalfile.object` and
   :func:`logicalfile.find` offers more examples.

Relationship between metadata objects
-------------------------------------

.. currentmodule:: dlisio.plumbing

A key feature of RP66v1 is that objects refer to each other.  Object-to-object
referencing is used to establish a relationship between two objects. This
relationship can serve as an implicit context to the object. Many objects rely
on this context and make little sense without it.

Object-references are conveyed through the object's attributes. A concrete
example is :attr:`Tool.channels`, which references all the channels that are
produced directly by that tool. dlisio automatically resolves object references
to make it easy to work with programmatically:

.. code-block:: python

   >>> tool = f.object('TOOL', 'USIT')
   >>> tool.channels
   [TDEP, BI, CBL, CBLF, CBSL, ..., CMCG, WF1, WF1N, WF2, WF2N]

   >>> channel = tool.channels[1]
   >>> channel.long_name
   'Bond Index'

Multiple origins
----------------

RP66v1 allows for a single logical file to have multiple
:class:`Origin`-objects. Origin describes the source of the data, such as
which field and well it's from. It's therefore theoretically possible that the
data contained in a logical file stem from different sources when there are
more than one :class:`Origin`-objects. Such files obviously need special care.
More precisely, the origin field of each object that is accessed needs to be
examined in order to determine which origin it belongs to.

The majority of files do *not* contain multiple origins, which makes it safe to
ignore the origin field. However, it is considered a good practice to check the
origin count when opening a new file, e.g. by issuing a warning if there are
more than one:

.. code-block:: python

   import dlisio
   import logging

   with dlisio.load(path) as (f, *tail):
      if len(f.origins) > 1: logging.warning('File contains multiple origins')

Vendor-specific metadata
------------------------

In addition to the many object-structures defined by RP66v1 itself, vendors are
free to specify their own metadata objects. However, with often cryptic naming
and minimal explanation, such objects can be challenging to decipher without
any external explanation of the intent of these objects.

The vendor-specific objects are reachable through :code:`f.unknowns`:

.. code-block:: python

   with dlisio.load(path) as (f, *tail):
      f.unknowns
