import os

from . import core
from .file import physicalfile, logicalfile
from .errors import ErrorHandler

def open(path, offset = 0):
    """ Open a file

    Open a low-level file handle. This is not intended for end-users - rather,
    it's an escape hatch for very broken files that dlisio cannot handle.

    Parameters
    ----------
    path : str_like
    offset: int
        Physical file offset at which handle must be opened

    Returns
    -------
    stream : dlisio.core.stream

    See Also
    --------
    dlisio.load
    """
    return core.open(str(path), offset)

def load(path, error_handler = None):
    """ Loads a file and returns one filehandle pr logical file.

    The dlis standard have a concept of logical files. A logical file is a
    group of related logical records, i.e. curves and metadata and is
    independent from any other logical file. Each physical file (.dlis) can
    contain 1 to n logical files. Layouts of physical- and logical files:

    Physical file::

         --------------------------------------------------------
        | Logical File 1 | Logical File 2 | ... | Logical File n |
         --------------------------------------------------------

    Logical File::

         ---------------------------------------------------------
        | Fileheader |  Origin  |  Frame  |  Channel  | curvedata |
         ---------------------------------------------------------

    This means that dlisio.load() will return 1 to n logical files.

    Parameters
    ----------

    path : str_like

    error_handler : dlisio.errors.ErrorHandler, optional
            Error handling rules. Default rules will apply if none supplied.
            Handler will be added to all the logical files, so users may modify
            the behavior at any time.

    Examples
    --------

    Read the fileheader of each logical file

    >>> with dlisio.load(filename) as files:
    ...     for f in files:
    ...         header = f.fileheader

    Automatically unpack the first logical file and store the remaining logical
    files in tail

    >>> with dlisio.load(filename) as (f, *tail):
    ...     header = f.fileheader
    ...     for g in tail:
    ...         header = g.fileheader

    Note that the parentheses are needed when unpacking directly in the with-
    statement.  The asterisk allows an arbitrary number of extra logical files
    to be stored in tail. Use len(tail) to check how many extra logical files
    there are.

    Returns
    -------

    dlis : dlisio.physicalfile(dlisio.logicalfile)
    """
    if not error_handler:
        error_handler = ErrorHandler()

    path = str(path)
    if not os.path.isfile(path):
        raise OSError("'{}' is not an existing regular file".format(path))

    stream = open(path)
    tm = core.read_tapemark(stream)
    is_tif = core.valid_tapemark(tm)
    stream.close()

    indexer = FileIndexer(path, is_tif, error_handler)
    try:
        while (not indexer.end_of_data()):
            indexer.open_stream()

            if indexer.logical_eof():
                # When working with TapeImageFormat files, lfp will report EOF
                # when encountering a TM of type 1. We therefore need to close
                # the current stream and open a new one at the next TM.
                indexer.close_stream()
                continue

            if indexer.find_sul():
                indexer.read_sul()

            if indexer.logical_eof():
                indexer.close_stream()
                continue

            indexer.apply_rp66_protocol()
            indexer.parse_logical_file()
    except:
        indexer.close()
        raise

    return physicalfile(indexer.logical_files)


class FileIndexer:
    """ Logical Files Indexer

    Contains all the internal information required to correctly parse logical
    files.
    """
    def __init__(self, path, is_tif, error_handler):
        self.error_handler = error_handler
        self.is_tif = is_tif
        self.path = path

        self.logical_files = []
        self.sul = None
        self.stream = None

        self.open_next_at_tell = 0
        self.data_end = False

    def open_stream(self):
        """ Opens new logical stream

        Opens cfile/aligned TIF stream. It's important that both streams are
        opened at the same offset as it allows us to handle TIFed files the
        same way as non-TIFed.

        In case of TIFed files stream must always be opened at the TM.
        """
        self.stream = open(self.path, self.open_next_at_tell)
        if self.is_tif:
            self.stream = core.open_tif(self.stream)

    def close_stream(self):
        """ Closes current logical stream
        """
        if self.stream:
            self.stream.close()
        self.stream = None

    def apply_rp66_protocol(self):
        """ Opens RP66 protocol (Visible Envelope part)

        Positions on next VR and opens rp66 protocol from that VR.
        """
        core.findvrl(self.stream, self.error_handler)
        self.stream = core.open_rp66(self.stream)

    def index_logical_file(self):
        """ Finds LR offsets required to parse current file and LF offsets
        needed to open the next one

        Due to the essence of core.findoffsets function both these things are
        done at the same time.
        Code may become more straightforward if findoffsets are ever refactored
        to deal with this internally and explicitly return the final tell.

        Warning: lfp does *not* make physical tell reliable.
            We rely on it anyway.
        """
        explicits, implicits, broken = core.findoffsets(
            self.stream, self.error_handler)
        if len(broken):
            self.data_end = True

        self.open_next_at_tell = self.stream.ptell
        if not self.stream.eof():
            # rewind only when EOF was detected by reading next LF record
            # substract VR header size for all the files
            # substract additional 12 for TIFed files to be positioned before TM
            self.open_next_at_tell -= 4
            if self.is_tif:
                self.open_next_at_tell -= 12

        return explicits, implicits

    def parse_logical_file(self):
        """ Parses new logical file

        In the process gathers data about the next logical file
        """
        explicits, implicits = self.index_logical_file()
        recs = core.extract(self.stream, explicits, self.error_handler)
        sets = core.parse_objects(recs, self.error_handler)
        pool = core.pool(sets)
        fdata = core.findfdata(self.stream, implicits, self.error_handler)

        lf = logicalfile(self.stream, pool, fdata, self.sul, self.error_handler)
        self.logical_files.append(lf)

    def end_of_data(self):
        """ Tests for end of data which indexer is able to process

        Returns true only if the physical file reported EOF or data itself is
        broken such that no new logical file can be opened.
        """
        return self.data_end

    def close(self):
        """ Closes parser

        Closes current stream along with streams of all processed logical files
        """
        self.close_stream()
        for f in self.logical_files:
            f.close()

    def logical_eof(self):
        """ Tests for logical EOF

        Decides if currently opened logical stream has data inside.
        In the process updates parsers knowledge about data eof and next logical
        file offset.

        This method must be called whenever TIF file marks are expected.
        At the moment we know that TIF EOF marks can happen before SUL, before
        LF or before physical EOF.
        If EOF is reported, then current stream does not contain a valid logical
        file, so it must be closed. New stream must be opened from the next TM.
        """
        ltell = self.stream.ltell
        try:
            self.stream.get(bytearray(1), ltell, 1)
        except Exception as e:
            self.error_handler.log(
                core.error_severity.critical,
                "dlis::load: Testing logical eof",
                e,
                "",
                "Load is suspended",
                "Physical tell: {} (dec)".format(self.stream.ptell))
            self.data_end = True
            return True

        if self.stream.peof():
            self.data_end = True
            return True

        if self.stream.eof():
            self.open_next_at_tell = self.stream.ptell
            return True

        self.stream.seek(ltell)
        return False

    def find_sul(self):
        """ Finds next SUL

        Expected to be called from the start of the stream.
        If SUL is found, positions on it and returns True.
        If SUL is not found, leaves position untouched and returns False.

        Reports specification violations if detected.
        """
        expected = not self.sul and (len(self.logical_files) == 0)
        try:
            core.findsul(self.stream, self.error_handler, expected)
            return True
        except RuntimeError as e:
            self.stream.seek(0)
            return False

    def read_sul(self):
        """ Reads SUL
        """
        sulsize = 80
        sulbytes = bytearray(sulsize)
        read = self.stream.get(
            sulbytes, self.stream.ltell, sulsize)

        if read != sulsize:
            self.error_handler.log(
                core.error_severity.major,
                "dlis::load: Reading SUL",
                "SUL is expected to be 80 bytes, but was {}".format(read),
                "2.3.2 Storage Unit Label (SUL): The first 80 bytes of the "
                    "Visible Envelope ... constitute a Storage Unit Label.",
                "Bytes are stored as SUL",
                "")
            sulbytes = sulbytes[0:read]

        self.sul = sulbytes
