from .. import core
from .. import common
from .file import LogicalFile, PhysicalFile, HeaderTrailer

def load(path, error_handler = None):
    """ Loads and indexes a LIS file

    Load does more than just opening the file. A LIS file has no random access
    in itself, so load scans the entire file and creates its own index to
    enumlate random access. The file is also segmented into Logical Files, see
    :class:`PhysicalFile` and :class:`LogicalFile`.

    ** Incorrectly written files **

    It is not uncommon that LIS files are written incorrectly, meaning they are
    violating the LIS79 specification. Typically it's only a very small portion
    of the file that is incorrect, often down to a couple of bytes.
    Unfortunately, because of how the internal structure of LIS files is
    defined, the bytes following the incorrect part become unreadable too. In
    most cases there is little dlisio can do about this as it's unclear what
    the original intention was.

    However, it may be possible to read the file up until the incorrect part
    occurs. load has an escape hatch for this, which essentially returns
    everything that it believes to be successfully indexed prior to the
    point-of-failure. The caveat being that there is no guarantee that the
    file is interpreted correctly by dlisio at this point. This escape hatch is
    controlled by the parameter ``error_handler``. Please refer to the examples
    section for more details of it's use.

    Notes
    -----

    It's not uncommon that LIS files are stored with different file extensions
    than `.LIS`. For example `.LTI` or `.TIF`. Load does not care about file
    extension at all. As long as the content adheres to the Log Interchange
    Standard, load will read it as such.

    Parameters
    ----------

    path : str_like
        path to lis-file

    error_handler : dlisio.common.ErrorHandler, optional
        Defines how load will behave when encountering any errors while
        indexing the file.

    Returns
    -------

    lis : dlisio.lis.PhysicalFile

    Examples
    --------

    Opening a file is straightforward. :func:`dlisio.lis.load` is designed to
    work like python's own ``open()``. That is, it can be used both with- and
    without python's ```with``-statments:

    >>> from dlisio import lis
    >>> with lis.load(filepath) as files:
    ...     pass

    If ``load`` raises a RuntimeError this is likely due to the file being
    incorrectly written. You can instruct dlisio to return to you what it did
    manage to index before it failed:

    >>> from dlisio.common import ErrorHandler, Actions
    >>> handler = ErrorHandler(critical=Actions.LOG_ERROR)
    >>> with lis.load(filepath, handler) as files:
    ...     pass

    What this effectively does is to turn the ``RuntimeError`` into a
    ``logging.error`` and load now returns a partially indexed file. dlisio
    does not guarantee that what's being returned is correct at this point, and
    you should verify for yourself that the data it serves you looks sane.
    """
    if not error_handler:
        error_handler = common.ErrorHandler()

    indexer = FileIndexer(path, error_handler)
    while not indexer.complete:
        try:
            indexer.index_logical_file()
        except:
            indexer.close()
            raise

    return PhysicalFile(indexer.logical_files)

class FileIndexer:
    """ Logical Files Indexer

    Contains all the internal information required to correctly parse logical
    files.
    """
    def __init__(self, path, error_handler):
        self.error_handler = error_handler
        self.path = path
        self.complete = False

        self.logical_files = []
        self.reel = HeaderTrailer()
        self.tape = HeaderTrailer()

        self.check_for_tapemarks()

    def check_for_tapemarks(self):
        """ Checks whether file is TIFed and adjusts initial offset accordingly
        """
        initial_offset = 0
        f = core.open(self.path, initial_offset)

        def read_as_tapemark(f):
            try:
                return core.read_tapemark(f)
            except:
                f.close()
                msg = 'Cannot read {} first bytes of file: {}'
                raise IOError(msg.format(initial_offset + 12, self.path))

        # Read the first 12 bytes of the file assuming TapeImageFormat.
        # Verify assumption before moving on.
        tm = read_as_tapemark(f)
        self.is_tif = core.valid_tapemark(tm)

        # Some TapeImageFormat files start with tapemark(s) of type 1
        # (EOF-tapemark).
        # Opening a lfp tapeimage protocol at a type 1 tapemarks causes an
        # instant EOF. Hence we have to find the offset of the first type 0
        # tapemark, which will be the start of our logical file.
        if self.is_tif:
            while tm.type != 0:
                tm = read_as_tapemark(f)
            initial_offset = f.ptell - 12

        self.offset = initial_offset
        f.close()

    def index_logical_file(self):
        """ Open a file and index it.
        """
        try:
            file = core.openlis(self.path, self.offset, self.is_tif)
        except EOFError:
            self.complete = True
            return
        except OSError as e:
            issue = {
                'severity' : core.error_severity.critical,
                'context'  : "dlisio.lis.load: file {}".format(self.path),
                'problem'  : e,
                'action'   : "Indexing stopped at physical tell {} (dec)"
                    .format(self.offset),
            }
            self.error_handler.log(**issue)
            self.complete = True
            return

        index = file.index_records()

        # Update the offset at which stopped indexing. Due to inconsistent use
        # of tapemarks in files, we have to manually update the offset.

        # TODO: this logic should see further improvements to be more robust
        #       against different file configurations/layouts.
        self.offset = file.ptell()
        if self.is_tif and not file.eof():
            self.offset = self.offset - 12

        # Special handling of Records that serve as delimiters.
        #
        # All delimiter records are indexed separately by index_records. If
        # applicable the raw record is extracted and correctly stored. In any
        # case the filehandle is closed before we continue indexing the file.
        first = index.explicits()[0] if len(index.explicits()) else None
        if is_delimiter(first):
            if index.size() != 1:
                # this never should happen. Basically assert
                issue = {
                    'severity': core.error_severity.critical,
                    'context' : "dlisio.lis.load: file {}, record {}"
                        .format(self.path, first),
                    'problem' : "Delimiter file size is {} != 1"
                        .format(index.size()),
                    'action'  : "Indexing stopped at physical tell {} (dec)"
                        .format(self.offset),
                }
                self.error_handler.log(**issue)
                self.complete = True
                file.close()
                return

            try:
                record = file.read_record(first)
            except Exception as e:
                # This is very unlikely to happen as index_records has already
                # done the sanity checking needed for successfully reading the
                # record.
                # However read_records can in theory still fail on blocked IO
                # and other non-LIS related issues.
                issue = {
                    'severity': core.error_severity.critical,
                    'context' : "dlisio.lis.load: file {}, record {}"
                        .format(self.path, first),
                    'problem' : e,
                    'action'  : "Indexing stopped at physical tell {} (dec)"
                        .format(self.offset),
                }
                self.error_handler.log(**issue)
                self.complete = True
                return
            finally:
                file.close()

            self.adjust_reel_tape(first, record)
        else:
            if index.size():
                logfile = LogicalFile(
                    self.path, file, index, self.reel, self.tape)
                self.logical_files.append(logfile)
            else:
                file.close()

        if index.isincomplete():
            issue = {
                'severity': core.error_severity.critical,
                'context' : "dlisio.lis.load: file {}".format(self.path),
                'problem' : index.errmsg(),
                'action'  : "Indexing stopped at physical tell {} (dec)"
                    .format(self.offset),
            }
            self.error_handler.log(**issue)
            self.complete = True


    def adjust_reel_tape(self, first, record):
        if first.type == core.lis_rectype.reel_header:
            self.reel = HeaderTrailer(record)

        elif first.type == core.lis_rectype.reel_trailer:
            # The reel is already assigned to the LF's at this point, so
            # just assign the trailer to that instance before initiating a
            # new instance for the next reel.
            self.reel.rawtrailer = record
            self.reel = HeaderTrailer()

        elif first.type == core.lis_rectype.tape_header:
            self.tape = HeaderTrailer(record)

        elif first.type == core.lis_rectype.tape_trailer:
            # The tape is already assigned to the LF's at this point, so
            # just assign the trailer to that instance before initiating a
            # new instance for the next tape.
            self.tape.rawtrailer = record
            self.tape = HeaderTrailer()

    def close(self):
        """ Closes parser

        Closes all processed logical files
        """
        for f in self.logical_files:
            f.close()


def is_delimiter(recinfo):
    if recinfo is None: return False

    if recinfo.type == core.lis_rectype.reel_header:  return True
    if recinfo.type == core.lis_rectype.reel_trailer: return True
    if recinfo.type == core.lis_rectype.tape_header:  return True
    if recinfo.type == core.lis_rectype.tape_trailer: return True
    if recinfo.type == core.lis_rectype.logical_eof:  return True
    return False
