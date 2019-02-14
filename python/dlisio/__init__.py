import numpy as np
from . import core

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

class dlis(object):
    def __init__(self, stream, explicits):
        self.file = stream
        self.explicit_indices = explicits

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.file.close()

    def storage_label(self):
        blob = self.file.get(bytearray(80), 0, 80)
        return core.storage_label(blob)

    def objectsets(self, reload = False):
        if self.object_sets is None:
            self.object_sets = self.file.extract(self.explicit_indices)

        return core.parse_objects(self.object_sets)

def open(path):
    tells, residuals, explicits = core.findoffsets(path)
    explicits = [i for i, explicit in enumerate(explicits) if explicit != 0]

    stream = core.stream(path)

    try:
        stream.reindex(tells, residuals)
        f = dlis(stream, explicits)
    except:
        stream.close()
        raise

    return f
