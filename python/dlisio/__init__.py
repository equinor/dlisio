from . import core
from . import plumbing
from . import errors
from .settings import get_encodings, set_encodings
from .file import physicalfile, logicalfile
from .load import load
from .open import open

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass
