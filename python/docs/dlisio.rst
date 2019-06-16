Open and Load
=============
.. autofunction:: dlisio.load
.. autofunction:: dlisio.open

File Handle
===========
.. autoclass:: dlisio.dlis()
    :members:
    :member-order: bysource
    :undoc-members:

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
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Calibration
-----------
.. autoclass:: Calibration(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Channel
-------
.. autoclass:: Channel()
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Coefficent
----------
.. autoclass:: Coefficient(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Computation
-----------
.. autoclass:: Computation(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Frame
-----
.. autoclass:: Frame(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Fileheader
----------
.. autoclass:: Fileheader(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Longname
--------
.. autoclass:: Longname(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Measurement
-----------
.. autoclass:: Measurement(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Origin
------
.. autoclass:: Origin(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Parameter
---------
.. autoclass:: Parameter(BasicObject)
    :members:
    :member-order: bysource
    :inherited-members:
    :exclude-members: stripspaces, update_stash

Tool
----
.. autoclass:: Tool(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Equipment
---------
.. autoclass:: Equipment(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Zone
----
.. autoclass:: Zone(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:

Unknown
-------
.. autoclass:: Unknown(BasicObject)
    :members:
    :member-order: bysource
    :exclude-members: stripspaces, update_stash
    :inherited-members:
