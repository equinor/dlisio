import logging

from .. import core
from .information_record import InformationRecord


class HeaderTrailer():
    """ Container for Header-Trailer pairs

    Both Reels and Tapes have a Header Logical Record (RHLR and THLR) - and
    optionally a Trailer Logical Record (RTLR / TTLR).

    The Trailer Records have an identical structure to their corresponding
    header, except for the prev_reel_name/prev_tape_name, which in the trailer
    is named next_reel_name/next_tape_name.
    """
    def __init__(self, header=None, trailer=None):
        self.rawheader  = header
        self.rawtrailer = trailer

    def header(self):
        """ Header Record

        Returns the Reel or Tape Header Logical Record (RHLR or THLR), depending
        on the context in which the current instance lives.

        Returns
        -------

        header : core.reel_header, core.tape_header or None
            Returns None if the Header Record is missing.
        """
        if self.rawheader is None:
            logging.warning("Missing Header Record - File structure is broken")
            return None

        return parse_record(self.rawheader)

    def trailer(self):
        """ Trailer Record

        Returns the Reel or Tape Trailer Logical Record (RTLR or TTLR),
        depending on the context in which the current instance lives.

        Returns
        -------

        trailer : core.reel_trailer, core.tape_trailer or None
            Returns None if the Trailer Record is missing.
        """
        if self.rawtrailer is None:
            logging.info("No (optional) Trailer Record present")
            return None

        return parse_record(self.rawtrailer)


class LogicalFile():
    """ Logical File (LF)

    This class is the main interface for working with a single LF. A LF is
    essentially a series of Logical Records (LR). There are many different LR
    types, each designed to carry a specific piece of information. For example
    a Logical File Header Record contains static information about the file,
    while the Data Format Specification Records contain information about
    curve-data, and how that should be parsed.

    This class provides an interface for easy interaction and extraction of the
    various Logical Records within the Logical File. It is completely
    independent of other LF's, and even has its own IO-device. It stores a
    pre-built index of all LR's for random access when reading from disk.

    Notes
    -----

    No parsed records are cached by this class. Thus it's advisable that the
    result of each record read is cached locally.

    Attributes
    ----------

    path : str
        Path to the file as passed to :func:`dlisio.lis.load`

    io : dlisio.core.lis_stream
       The underlying lis-aware IO-device that acts on the file. The iodevice
       implements primitive io-operations such as seek, read and tell, but also
       higher level abstractions such as read_record. For normal workflows it
       should not be necessary to interact directly with the io-device.

    index : dlisio.core.lis_record_index
       A dlisio-created index of all Logical Records (LR) in the current
       Logical File (LF). The index is created at load and gives dlisio random
       access to the LR's. The index can be iterated and records can be
       extracted using :attr:`dlisio.lis.LogicalFile.io`. For normal workflow
       it should not be necessary to interact directly with the index.

    reel : dlisio.lis.HeaderTrailer
        The reel that this Logical File (LF) belongs to.

        See :class:`dlisio.lis.PhysicalFile` for more on the relationship
        between LIS reels and LF's. See :class:`dlisio.core.reel_header` and
        :class:`dlisio.core.reel_trailer` for more on the Reel Logical Records
        (RHLR, RTLR).

    tape : dlisio.lis.HeaderTrailer
        The tape that this Logical File (LF) belongs to.

        See :class:`dlisio.lis.PhysicalFile` for more on the relationship
        between LIS tapes and LF's. See :class:`dlisio.core.tape_header` and
        :class:`dlisio.core.tape_trailer` for more on the Tape Logical Records
        (THLR, TTLR).

    """
    def __init__(self, path, io, index, reel, tape):
        self.path  = path
        self.io    = io
        self.index = index
        self.reel  = reel
        self.tape  = tape

    def close(self):
        """Close the file handle

        It is not necessary to call this method if you're using the `with`
        statement, which will close the file for you.
        """
        self.io.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        msg = 'LogicalFile(path="{}", io={}, index={})'
        return msg.format(self.path, self.io, self.index)

    def header(self):
        """ Logical File Header

        Reads and parses the Logical File Header from disk - if present.

        Returns
        -------

        header : dlisio.core.file_header or None
        """
        rectype = core.lis_rectype.file_header
        info = [x for x in self.explicits() if x.type == rectype]

        if len(info) > 1:
            msg =  'Multiple {} Logical Records, should only be one. '
            msg += 'Use parse_record to read them all'
            raise ValueError(msg.format(core.rectype_tostring(rectype)))

        if len(info) == 0:
            msg = "No {} Logical Record in {}"
            logging.warning(msg.format(core.rectype_tostring(rectype), self))
            return None

        rec = self.io.read_record(info[0])
        return parse_record(rec)

    def trailer(self):
        """ Logical File Trailer

        Reads and parses the Logical File Header from disk - if present.

        Returns
        -------

        trailer : dlisio.core.file_trailer or None
        """
        rectype = core.lis_rectype.file_trailer
        info = [x for x in self.explicits() if x.type == rectype]

        if len(info) > 1:
            msg =  'Multiple {} Records, should only be one. '
            msg += 'Use parse_record to read them all'
            raise ValueError(msg.format(core.rectype_tostring(rectype)))

        if len(info) == 0:
            msg = "No {} Logical Record in {}"
            logging.info(msg.format(core.rectype_tostring(rectype), self))
            return None

        rec = self.io.read_record(info[0])
        return parse_record(rec)

    def explicits(self):
        return self.index.explicits()

    def data_format_specs(self):
        """ Data Format Specification Records (DFSR)

        A DFSR contains all relevant information to extract a specific logset -
        a logset being a set of channels/curves all sampled along a common
        index.

        See also
        --------

        dlisio.lis.curves: Read all the curves from a given DFSR

        Returns
        -------

        records : list of dlisio.core.dfsr
        """
        # TODO duplication checking
        ex = self.explicits()
        dfs = core.lis_rectype.data_format_spec
        recs = [self.io.read_record(x) for x in ex if x.type == dfs]
        return [parse_record(x) for x in recs]

    def job_identification(self):
        """ Job Identification Logical Records

        Returns
        -------

        records : list of :class:`dlisio.lis.InformationRecord`
        """
        rectype = core.lis_rectype.job_identification
        ex = self.explicits()
        recs = [self.io.read_record(x) for x in ex if x.type == rectype]
        return [InformationRecord(parse_record(x)) for x in recs]

    def wellsite_data(self):
        """ Wellsite Data Logical Records

        Returns
        -------

        records : list of :class:`dlisio.lis.InformationRecord`
        """
        rectype = core.lis_rectype.wellsite_data
        ex = self.explicits()
        recs = [self.io.read_record(x) for x in ex if x.type == rectype]
        return [InformationRecord(parse_record(x)) for x in recs]

    def tool_string_info(self):
        """ Tool String Info Logical Records

        Returns
        -------

        records : list of :class:`dlisio.lis.InformationRecord`
        """
        rectype = core.lis_rectype.tool_string_info
        ex = self.explicits()
        recs = [self.io.read_record(x) for x in ex if x.type == rectype]
        return [InformationRecord(parse_record(x)) for x in recs]

class PhysicalFile(tuple):
    """ Physical File - A regular file on disk

    Think of a LIS file as a directory. The top directory is your regular file
    on disk. The regular file is divided into sub-structures (or subfolders if
    you will) called 'Reels'. Each Reel if further divided into 'Tapes', which
    again contains Logical Files::

        your_file.lis
        |
        |-> Reel 0
        |   |
        |   |-> Tape 0
        |   |   |
        |   |   |-> Logical File 0
        |   |   |-> Logical File 1
        |   |
        |   |-> Tape 1
        |   |   |
        |   |   |-> Logical File 2
        |
        |-> Reel 1
            |
            |-> Tape 0
                |
                |-> Logical File 3

    Each Logical File can be thought of as an independent regular file,
    containing log data.

    Each Reel and Tape has its own corresponding Header and Trailer. These
    contain general information about the Reel or Tape.

    When reading the LIS file with :func:`dlisio.lis.load`, dlisio will flatten
    the above tree structure and simply return a tuple-like object
    (:class:`PhysicalFile`) of all the Logical Files. The Reel and Tape in
    which a Logical File belongs to can be queried directly from the Logical
    File.

    Notes
    -----

    More often than not, the tree structure of a LIS file is trivial,
    containing just a couple of logical files - all belonging to the same Tape
    and Reel.

    Notes
    -----

    The LIS79 specification opens for the possibility of a Reel spanning across
    multiples regular files. dlisio does not currently have cross-file support.
    Each regular file can still be read as a stand-alone LIS-file.

    See Also
    --------

    dlisio.lis.load : Open and Index a LIS-file
    dlisio.lis.LogicalFile : A wrapper for a single Logical File
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        for f in self:
            f.close()

    def __repr__(self):
        return 'PhysicalFile(logical files: {})'.format(len(self))


def parse_record(rec):
    """ Parse Explicit (or Fixed) record

    Checks the type-of-record and dispatches to the correct parsing routine.

    Parameters
    ----------

    rec : dlisio.core.lis_record

    Returns
    -------

    parsed_record
        The type of the returned record depends on rec.info.type of the raw
        record.

    Raises
    ------

    NotImplementedError
        If no parsing routine is implemented for the given record
    """
    rtype = rec.info.type
    types = core.lis_rectype
    if rtype   == types.data_format_spec:   return core.parse_dfsr(rec)
    elif rtype == types.file_header:        return core.parse_file_header(rec)
    elif rtype == types.file_trailer:       return core.parse_file_trailer(rec)
    elif rtype == types.reel_header:        return core.parse_reel_header(rec)
    elif rtype == types.reel_trailer:       return core.parse_reel_trailer(rec)
    elif rtype == types.tape_header:        return core.parse_tape_header(rec)
    elif rtype == types.tape_trailer:       return core.parse_tape_trailer(rec)
    elif rtype == types.wellsite_data:      return core.parse_info_record(rec)
    elif rtype == types.tool_string_info:   return core.parse_info_record(rec)
    elif rtype == types.job_identification: return core.parse_info_record(rec)
    else:
        msg = "No parsing rule for {} Records"
        raise NotImplementedError(msg.format(core.rectype_tostring(rtype)))
