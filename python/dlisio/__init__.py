from . import core
from . import common
from . import lis
from . import dlis

import sys

# remove else once support for python 3.7 is over
if sys.version_info >= (3, 8):
    try:
        import importlib.metadata
        __version__ = importlib.metadata.version(__name__)
    except importlib.metadata.PackageNotFoundError:
        pass
else:
    try:
       import pkg_resources
       __version__ = pkg_resources.get_distribution(__name__).version
    except pkg_resources.DistributionNotFound:
        pass
