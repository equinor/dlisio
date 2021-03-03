from collections import OrderedDict

from .basicobject import BasicObject
from . import utils

class Fileheader(BasicObject):
    """
    The Fileheader is an identifier for the Logical File. Below follows a description of the
    relationship between a DLIS-file, Logical File, File Set, and Storeage Set:

    **DLIS-file** - single dlis-file may or may not consists of multiple logical
    files::

         ---------------------------------------
        | Logical File 1 | ... | Logical File n |
         ---------------------------------------


    **Logical File** - Each Logical File has exactly one Fileheader, but can
    have mutiple origins::

         ---------------------------------------------
        | Fileheader | Origin | Frame | Channel | ... |
         ---------------------------------------------

    **File Set** - A File set consists of multiple Logical Files which may
    spand across multiple DLIS-files. Logical Files are grouped into File Sets
    by producer defined criterias::

         ---------------------------------------
        | Logical File 1 | ... | Logical File n |
         ---------------------------------------

    **Storage Set** - A Storage Set consist of multiple DLIS-files. A Storage Set may or may
    not coincide with a File Set::

         ---------------------------------
        | DLIS-file 1 | ... | DLIS-File n |
         ---------------------------------

    Attributes
    ----------

    sequencenr : str
        Sequential position of the logical file in a storage set

    id : str
        Descriptive identification of the logical file


    See also
    --------

    BasicObject : The basic object that Fileheader is derived from

    Notes
    -----

    The Fileheader object reflects the logical record type FILE-HEADER, defined
    in rp66. FILE-HEADER records are listed in Appendix A.2 - Logical Record
    Types and described in Chapter 5.1 - Static and Frame Data, File Header
    Logical Record (FHLR).
    """
    attributes = {
        'SEQUENCE-NUMBER': utils.scalar,
        'ID'             : utils.scalar,
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def sequencenr(self):
        return self['SEQUENCE-NUMBER']

    @property
    def id(self):
        return self['ID']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Description'] = self.id
        d['Position in storage set'] = self.sequencenr

        utils.describe_dict(buf, d, width, indent, exclude)
