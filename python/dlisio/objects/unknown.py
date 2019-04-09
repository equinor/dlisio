from .basicobject import BasicObject


class Unknown(BasicObject):
    """
    The unknown object implements a dict interface and is intended as a
    fall-back object if the object-type is not recognized by dlisio, e.g.
    vendor spesific object types
    """
    def __init__(self, obj = None, type = None):
        if type is None:
            type = 'UNKNOWN'
        super().__init__(obj, type)
        self.attributes = None

    @staticmethod
    def load(obj, type = None):
        self = Unknown(obj, type = type)
        self.attributes = {a.label.lower() : a.value for a in obj.values()}
        self.stripspaces()
        return self

    def __getattr__(self, key):
        return self.attributes[key]

    def __str__(self):
        s  = "dlisio.unknown:\n"
        s += "\tname: {}\n".format(self.name)
        s += "\ttype: {}\n".format(self.type)
        for key, value in self.attributes.items():
            s += "\t{}: {}\n".format(key, value)
        s += "\tattic: {}\n".format(self.type)
        return s
