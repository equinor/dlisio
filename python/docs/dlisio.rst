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

Objects
=======

Basic object
------------
.. autoclass:: dlisio.objects.BasicObject()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :member-order: groupwise

Calibration
-----------
.. autoclass:: dlisio.objects.Calibration()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Channel
-------
.. autoclass:: dlisio.objects.Channel()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Frame
-----
.. autoclass:: dlisio.objects.Frame()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Fileheader
----------
.. autoclass:: dlisio.objects.Fileheader()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Origin
------
.. autoclass:: dlisio.objects.Origin()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Parameter
---------
.. autoclass:: dlisio.objects.Parameter()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Tool
----
.. autoclass:: dlisio.objects.Tool()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:

Unknown
-------
.. autoclass:: dlisio.objects.Unknown()
    :special-members: __repr__, __str__
    :members:
    :undoc-members:
    :exclude-members: stripspaces, contains
    :member-order: groupwise
    :inherited-members:
