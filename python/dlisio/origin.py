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
    def __init__(self, obj = None):
        super().__init__(obj, "ORIGIN")
        self._file_id           = None
        self._file_set_name     = None
        self._file_set_nr       = None
        self._file_nr           = None
        self._file_type         = None
        self._product           = None
        self._version           = None
        self._programs          = []
        self._creation_time     = None
        self._order_nr          = None
        self._descent_nr        = []
        self._run_nr            = []
        self._well_id           = None
        self._well_name         = None
        self._field_name        = None
        self._producer_code     = None
        self._producer_name     = None
        self._company           = None
        self._namespace_name    = None
        self._namespace_version = None

    @staticmethod
    def load(obj):
        self = Origin(obj)

        for attr in obj.values():
            if attr.value is None: continue
            if attr.label == "FILE-ID":
                self._file_id = attr.value[0]
            if attr.label == "FILE-SET-NAME":
                self._file_set_name = attr.value[0]
            if attr.label == "FILE-SET-NUMBER":
                self._file_set_nr = attr.value[0]
            if attr.label == "FILE-NUMBER":
                self._file_nr = attr.value[0]
            if attr.label == "FILE-TYPE":
                self._file_type = attr.value[0]
            if attr.label == "PRODUCT":
                self._product = attr.value[0]
            if attr.label == "VERSION":
                self._version = attr.value[0]
            if attr.label == "PROGRAMS":
                self._programs = attr.value
            if attr.label == "CREATION-TIME":
                self._creation_time = attr.value[0]
            if attr.label == "ORDER-NUMBER":
                self._order_nr = attr.value[0]
            if attr.label == "DESCENT-NUMBER":
                self._descent_nr = attr.value
            if attr.label == "RUN-NUMBER":
                self._run_nr = attr.value
            if attr.label == "WELL-ID":
                self._well_id = attr.value[0]
            if attr.label == "WELL-NAME":
                self._well_name = attr.value[0]
            if attr.label == "FIELD-NAME":
                self._field_name = attr.value[0]
            if attr.label == "PRODUCER-CODE":
                self._producer_code = attr.value[0]
            if attr.label == "PRODUCER-NAME":
                self._producer_name = attr.value[0]
            if attr.label == "COMPANY":
                self._company = attr.value[0]
            if attr.label == "NAME-SPACE-NAME":
                self._namespace_name = attr.value[0]
            if attr.label == "NAME-SPACE-VERSION":
                self._namespace_version = attr.value[0]

        self.stripspaces()
        return self

    @property
    def file_id(self):
        """File-identifier

        An exact copy of Fileheader.id

        Returns
        -------

        file_id : str
        """
        return self._file_id

    @property
    def file_set_name(self):
        """File set name

        The name of the File Set that the Logical File is a part of, if
        any. File Set Names are not required to be unique.

        Returns
        -------

        file_set_name : str
        """
        return self._file_set_name

    @property
    def file_set_nr(self):
        """File set number

        The number of the File Set that the logical file is a part of, if any. The
        file set number is often set to a psudo-random number to distinguish
        different File Sets. However, it is not required to be unique.

        Returns
        -------

        file_set_nr : int
        """
        return self._file_set_nr

    @property
    def file_nr(self):
        """File number

        The file number of each Logical File. The number is relative to the
        File Set that the Logical File belongs to in the sense that file
        numbers increase in the order of which the Logical Files in the File
        Set is created. It is not a requirement that the file number increase
        sequentially.

        Note that there is no defined relationship between the file number of
        Logical Files within a Storage Set.

        Returns
        -------

        file_nr : int
        """
        return self._file_nr

    @property
    def file_type(self):
        """File type

        A producer spesified File-Type that signifies the content of the
        DLIS-file or the circumstances under which the DLIS-file was created.

        Returns
        -------

        file_type : str
        """
        return self._file_type

    @property
    def product(self):
        """Product

        Name of the software product that produced the DLIS-file.

        Returns
        -------

        product : str
        """
        return self._product

    @property
    def version(self):
        """Version

        The version of the software product that created the DLIS-file.

        Returns
        -------

        version : str
        """
        return self._version

    @property
    def programs(self):
        """Programs

        List of programs and services that was a part of the software that
        created the DLIS-file.

        Returns
        -------

        programs : list of str
        """
        return self._programs

    @property
    def creation_time(self):
        """Creation time

        The date and time at which the DLIS-File was created.

        Returns
        -------

        creation_time : datetime.datetime
        """
        return self._creation_time

    @property
    def order_nr(self):
        """Service order number

        An unique accounting number assosiated with the creation of the
        DLIS-File.

        Returns
        -------

        order_nr : str
        """
        return self._order_nr

    @property
    def descent_nr(self):
        """Descent number

        A producer spesified number. The meaning of this number must be
        obtained directly from the producer.

        Returns
        -------

        descent_nr : unknown
        """
        return self._descent_nr

    @property
    def run_nr(self):
        """Run number

        A company spesified number. The meaning of this number must be obtained
        directly from the company.

        Returns
        -------

        descent_nr : unknown
        """
        return self._run_nr

    @property
    def well_id(self):
        """Well id

        Identifier for the well in which the measurments was taken. When
        applicable, the API (American Petroleum Institute) Well number should
        be used.

        Returns
        -------

        well_id : str
        """
        return self._well_id

    @property
    def well_name(self):
        """Well name

        Name of the well in which the measurements was taken.

        Returns
        -------

        well_name : str
        """
        return self._well_name

    @property
    def field_name(self):
        """Field name

        The name of the field where the well belongs. If there is no
        field-name, it should default to WILDCAT.

        Returns
        -------

        field : str
        """
        return self._field_name

    @property
    def producer_code(self):
        """Producer code

        The producer's identifying code.

        Returns
        -------

        producer_code : int
        """
        return self._producer_code

    @property
    def producer_name(self):
        """Producer name

        The producer's name.

        Returns
        -------

        producer_name : str
        """
        return self._producer_name

    @property
    def company(self):
        """Company

        The name of the client company which the log was produced for.

        Returns
        -------

        company : str
        """
        return self._company

    @property
    def namespace_name(self):
        """Namespace name

        A producer-defined namespace for which the object names for this origin
        are defined under.

        Returns
        -------

        namespace_name : str
        """
        return self._namespace_name

    @property
    def namespace_version(self):
        """Namespace version

        The version of the namespace.

        Returns
        -------

        namespace_version : str
        """
        return self._namespace_version
