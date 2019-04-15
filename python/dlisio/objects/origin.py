from .basicobject import BasicObject


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

    @staticmethod
    def load(obj, name = None):
        self = Origin(obj, name = name)

        for label, value in obj.items():
            if value is None: continue

            if label == "FILE-ID":
                self.file_id = value[0]
            if label == "FILE-SET-NAME":
                self.file_set_name = value[0]
            if label == "FILE-SET-NUMBER":
                self.file_set_nr = value[0]
            if label == "FILE-NUMBER":
                self.file_nr = value[0]
            if label == "FILE-TYPE":
                self.file_type = value[0]
            if label == "PRODUCT":
                self.product = value[0]
            if label == "VERSION":
                self.version = value[0]
            if label == "PROGRAMS":
                self.programs = value
            if label == "CREATION-TIME":
                self.creation_time = value[0]
            if label == "ORDER-NUMBER":
                self.order_nr = value[0]
            if label == "DESCENT-NUMBER":
                self.descent_nr = value
            if label == "RUN-NUMBER":
                self.run_nr = value
            if label == "WELL-ID":
                self.well_id = value[0]
            if label == "WELL-NAME":
                self.well_name = value[0]
            if label == "FIELD-NAME":
                self.field_name = value[0]
            if label == "PRODUCER-CODE":
                self.producer_code = value[0]
            if label == "PRODUCER-NAME":
                self.producer_name = value[0]
            if label == "COMPANY":
                self.company = value[0]
            if label == "NAME-SPACE-NAME":
                self.namespace_name = value[0]
            if label == "NAME-SPACE-VERSION":
                self.namespace_version = value[0]

        self.stripspaces()
        return self
