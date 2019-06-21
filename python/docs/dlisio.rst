Open and Load
=============
.. autofunction:: dlisio.load
.. autofunction:: dlisio.open

File Handle
===========
.. autoclass:: dlisio.dlis()
    :members:
    :exclude-members: types
    :member-order: bysource
    :undoc-members:

    .. autoinstanceattribute:: types
        :annotation: = {}

.. currentmodule:: dlisio.plumbing

Basic Object
============
.. autoclass:: BasicObject()
    :members:
    :undoc-members:
    :member-order: bysource

RP66 objects (native dlis)
==========================

Axis
----
.. autoclass:: Axis(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Calibration
-----------
.. autoclass:: Calibration(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Channel
-------
.. autoclass:: Channel()
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Coefficent
----------
.. autoclass:: Coefficient(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Computation
-----------
.. autoclass:: Computation(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Frame
-----
.. autoclass:: Frame(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Fileheader
----------
.. autoclass:: Fileheader(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Group
-----
.. autoclass:: Group(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Longname
--------
.. autoclass:: Longname(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Measurement
-----------
.. autoclass:: Measurement(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Message
-------
.. autoclass:: Message(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Origin
------
.. autoclass:: Origin(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Parameter
---------
.. autoclass:: Parameter(BasicObject)
    :members:
    :member-order: bysource
    :inherited-members:
    :exclude-members: stripspaces

Path
----
.. autoclass:: Path(BasicObject)
    :members:
    :member-order: bysource
    :inherited-members:
    :exclude-members: stripspaces

Process
-------
.. autoclass:: Process(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Tool
----
.. autoclass:: Tool(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Equipment
---------
.. autoclass:: Equipment(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Zone
----
.. autoclass:: Zone(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Splice
------
.. autoclass:: Splice(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Wellref
-------
.. autoclass:: Wellref(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:

Unknown
-------
.. autoclass:: Unknown(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces
    :inherited-members:
