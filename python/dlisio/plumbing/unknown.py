from .basicobject import BasicObject


class Unknown(BasicObject):
    """
    The unknown object is intended as a fall-back object if the
    object-type is not recognized by dlisio, e.g. vendor spesific object types

    See also
    --------

    BasicObject : The basic object that Unknown is derived from

    """
    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)
