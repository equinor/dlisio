Strings and encodings
=====================
.. autofunction:: dlisio.set_encodings
.. autofunction:: dlisio.get_encodings

Error handling
==============
.. autoclass:: dlisio.errors.ErrorHandler()
.. autoclass:: dlisio.errors.Actions()

Open and Load
=============
.. autofunction:: dlisio.load
.. autofunction:: dlisio.open

Physical File
=============
.. autoclass:: dlisio.physicalfile()

Logical Files
=============
.. autoclass:: dlisio.logicalfile()
    :members:
    :exclude-members: types, IndexedObjectDescriptor
    :member-order: bysource
    :undoc-members:

    .. autoattribute:: types
        :annotation: = {}

.. currentmodule:: dlisio.plumbing

Object types
============

Basic Object
------------
.. autoclass:: BasicObject()
    :members:
    :undoc-members:
    :member-order: bysource
    :exclude-members: describe_attr

Axis
----
.. autoclass:: Axis(BasicObject)
    :exclude-members: describe_attr

Calibration
-----------
.. autoclass:: Calibration(BasicObject)
    :exclude-members: describe_attr

Channel
-------
.. autoclass:: Channel(BasicObject)
    :exclude-members: describe_attr, load, fmtstr

Coefficent
----------
.. autoclass:: Coefficient(BasicObject)
    :exclude-members: describe_attr

Comment
-------
.. autoclass:: Comment(BasicObject)
    :exclude-members: describe_attr

Computation
-----------
.. autoclass:: Computation(BasicObject)
    :exclude-members: describe_attr

Equipment
---------
.. autoclass:: Equipment(BasicObject)
    :exclude-members: describe_attr

Fileheader
----------
.. autoclass:: Fileheader(BasicObject)
    :exclude-members: describe_attr

Frame
-----
.. autoclass:: Frame(BasicObject)
    :exclude-members: describe_attr, link, create, fmtstr, fmtstrchannel

Group
-----
.. autoclass:: Group(BasicObject)
    :exclude-members: describe_attr, link

Longname
--------
.. autoclass:: Longname(BasicObject)
    :exclude-members: describe_attr

Measurement
-----------
.. autoclass:: Measurement(BasicObject)
    :exclude-members: describe_attr

Message
-------
.. autoclass:: Message(BasicObject)
    :exclude-members: describe_attr

No Format
---------
.. autoclass:: Noformat(BasicObject)
    :exclude-members: describe_attr

Origin
------
.. autoclass:: Origin(BasicObject)
    :exclude-members: describe_attr

Parameter
---------
.. autoclass:: Parameter(BasicObject)
    :exclude-members: describe_attr

Path
----
.. autoclass:: Path(BasicObject)
    :exclude-members: describe_attr

Process
-------
.. autoclass:: Process(BasicObject)
    :exclude-members: describe_attr

Splice
------
.. autoclass:: Splice(BasicObject)
    :exclude-members: describe_attr

Tool
----
.. autoclass:: Tool(BasicObject)
    :exclude-members: describe_attr

Wellref
-------
.. autoclass:: Wellref(BasicObject)
    :exclude-members: describe_attr, load

Zone
----
.. autoclass:: Zone(BasicObject)
    :exclude-members: describe_attr

Unknown
-------
.. autoclass:: Unknown(BasicObject)
    :exclude-members: create
