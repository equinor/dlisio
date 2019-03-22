Open and Load
=============
.. autofunction:: dlisio.load
.. autofunction:: dlisio.open

File Handle
===========
.. autoclass:: dlisio.dlis()
    :special-members: __enter__, __exit__
    :members:
    :member-order: groupwise
    :undoc-members:

Objectpool
==========
.. autoclass:: dlisio.Objectpool()
    :special-members: __repr__, __len__

Objects
=======

Basic object
------------
.. autoclass:: dlisio.BasicObject()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :member-order: groupwise

Calibration
-----------
.. autoclass:: dlisio.Calibration()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Channel
-------
.. autoclass:: dlisio.Channel()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Frame
-----
.. autoclass:: dlisio.Frame()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Fileheader
----------
.. autoclass:: dlisio.Fileheader()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Origin
------
.. autoclass:: dlisio.Origin()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Parameter
---------
.. autoclass:: dlisio.Parameter()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Tool
----
.. autoclass:: dlisio.Tool()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Unknown
-------
.. autoclass:: dlisio.Unknown()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:
