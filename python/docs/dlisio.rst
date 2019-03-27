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
.. autoclass:: dlisio.basicobject.BasicObject()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :member-order: groupwise

Calibration
-----------
.. autoclass:: dlisio.calibration.Calibration()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Channel
-------
.. autoclass:: dlisio.channel.Channel()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Frame
-----
.. autoclass:: dlisio.frame.Frame()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Fileheader
----------
.. autoclass:: dlisio.fileheader.Fileheader()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Origin
------
.. autoclass:: dlisio.origin.Origin()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Parameter
---------
.. autoclass:: dlisio.parameter.Parameter()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Tool
----
.. autoclass:: dlisio.tool.Tool()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Unknown
-------
.. autoclass:: dlisio.unknown.Unknown()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:
