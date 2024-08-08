from . import core
from . import common
from . import lis
from . import dlis

try:
    import importlib.metadata
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    pass
