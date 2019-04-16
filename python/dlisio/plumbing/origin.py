from .basicobject import BasicObject
from .valuetypes import scalar, vector

class Origin(BasicObject):
    """ Describes the creation of the logical file.

    Origin objects is an unique indentifier for a Logical File and it
    describes the circumstances under which the file was created. The Origin
    object also spesify the Logical File's relation to a DLIS-file and to
    which Logical Set it belongs.

    A logical file may have several Origin objects, whereas the first Origin
    object is the Defining object. No two logical files should have identical
    Defining Origins.

    Notes
    -----

    The Origin object reflects the logical record type ORIGIN, defined in rp66.
    ORIGIN records are listed in Appendix A.2 - Logical Record Types and
    described in detail in Chapter 5.1 - Static and Frame Data, Origin objects.

    See also
    --------

    dlisio.Fileheader : Fileheader
    """
    attributes = {
        'FILE-ID'           : scalar('file_id'),
        'FILE-SET-NAME'     : scalar('file_set_name'),
        'FILE-SET-NUMBER'   : scalar('file_set_nr'),
        'FILE-NUMBER'       : scalar('file_nr'),
        'FILE-TYPE'         : scalar('file_type'),
        'PRODUCT'           : scalar('product'),
        'VERSION'           : scalar('version'),
        'PROGRAMS'          : vector('programs'),
        'CREATION-TIME'     : scalar('creation_time'),
        'ORDER-NUMBER'      : scalar('order_nr'),
        'DESCENT-NUMBER'    : vector('descent_nr'),
        'RUN-NUMBER'        : vector('run_nr'),
        'WELL-ID'           : scalar('well_id'),
        'WELL-NAME'         : scalar('well_name'),
        'FIELD-NAME'        : scalar('field_name'),
        'PRODUCER-CODE'     : scalar('producer_code'),
        'PRODUCER-NAME'     : scalar('producer_name'),
        'COMPANY'           : scalar('company'),
        'NAME-SPACE-NAME'   : scalar('namespace_name'),
        'NAME-SPACE-VERSION': scalar('namespace_version')
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'ORIGIN')

        #: An exact copy of Fileheader.id
        self.file_id           = None

        #: The name of the File Set that the Logical File is a part of
        self.file_set_name     = None

        #: The number of the File Set that the Logical File is a part of
        self.file_set_nr       = None

        #: The file number of the Logical File within a File Set
        self.file_nr           = None

        #: A producer spesified File-Type that signifies the content of the
        #: DLIS-file
        self.file_type         = None

        #: Name of the software product that produced the DLIS-file
        self.product           = None

        #: The version of the software product that created the DLIS-file
        self.version           = None

        #: Other programs and services that was a part of the software that
        #: created the DLIS-file
        self.programs          = []

        #: Date and time at which the DLIS-File was created
        self.creation_time     = None

        #: An unique accounting number assosiated with the creation of the
        #: DLIS-File
        self.order_nr          = None

        #: The meaning of this number must be obtained directly from the
        #: producer
        self.descent_nr        = []

        #: The meaning of this number must be obtained directly from the
        #: company
        self.run_nr            = []

        #: Id of the well at which the measurements where acquired
        self.well_id           = None

        #: Name of the well at which the measurements where acquired
        self.well_name         = None

        #: The field to which the well belongs
        self.field_name        = None

        #: The producer's identifying code
        self.producer_code     = None

        #: The producer's name
        self.producer_name     = None

        #: The name of the client company which the log was produced for
        self.company           = None

        #: A producer-defined namespace for which the object names for this
        #: origin are defined under
        self.namespace_name    = None

        #: The version of the namespace.
        self.namespace_version = None
