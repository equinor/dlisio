from .basicobject import BasicObject


class Unknown(BasicObject):
    """
    The unknown object is intended as a fall-back object if the
    object-type is not recognized by dlisio, e.g. vendor spesific object types

    See also
    --------

    BasicObject : The basic object that Unknown is derived from

    """
    def __init__(self, obj = None, name = None, type = None, lf = None):
        if type is None:
            type = 'UNKNOWN'
        super().__init__(obj, name = name, type = type, lf = lf)
