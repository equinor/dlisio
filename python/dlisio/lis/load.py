import logging

from .. import core
from .file import LogicalFile, PhysicalFile, HeaderTrailer, parse_record

def load(path):
    """ Loads and indexes a LIS file

    Load does more than just opening the file. A LIS file has no random access
    in itself, so load scans the entire file and creates its own index to
    enumlate random access. The file is also segmented into Logical Files, see
    :class:`PhysicalFile` and :class:`LogicalFile`.

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

    Returns
    -------

    lis : dlisio.lis.PhysicalFile
    """
    def read_as_tapemark(f):
        try:
            return core.read_tapemark(f)
        except:
            f.close()
            msg = 'Cannot read {} first bytes of file: {}'
            raise IOError(msg.format(offset + 12, path))

    offset = 0
    f = core.open(path, offset)

    # Read the first 12 bytes of the file assuming TapeImageFormat.
    # Verify assumption before moving on.
    tm = read_as_tapemark(f)
    is_tif = core.valid_tapemark(tm)

    # Some TapeImageFormat files start with tapemark(s) of type 1 (EOF-tapemark)
    # Opening a lfp tapeimage protocol at a type 1 tapemarks causes an instant
    # EOF. Hence we have to find the offset of the first type 0 tapemark, which
    # will be the start of our logical file.
    if is_tif:
        while tm.type != 0:
            tm = read_as_tapemark(f)
        offset = f.ptell - 12

    f.close()

    logical_files = []
    reel = HeaderTrailer()
    tape = HeaderTrailer()

    while True:
        # Open a new file-handle until we hit EOF
        try:
            f = core.openlis(path, offset, is_tif)
        except EOFError:
            break
        except OSError as e:
            msg =  'dlisio.lis.load: stopped indexing at tell {}\n'
            msg += 'Reason: {}\nFilepath: {}'
            logging.error(msg.format(offset, e, path))
            break

        index = f.index_records()
        truncated = f.istruncated()

        # If not a single record could be indexed, close the file and stop here
        if index.size() == 0 and truncated:
            f.close()
            break

        # Update the offset at which stopped indexing. Due to inconsistent use
        # of tapemarks in files, we have to manually update the offset.

        # TODO: this logic should see further improvements to be more robust
        #       against different file configurations/layouts.
        offset = f.ptell()
        if is_tif and not f.eof(): offset = offset - 12

        # Special handling of Records that serve as delimiters.
        #
        # All delimiter records are indexed separately by index_records. If
        # applicable the raw record is extracted and correctly stored. In any
        # case the filehandle is closed before we continue indexing the file.
        first = index.explicits()[0] if len(index.explicits()) else None
        if is_delimiter(first):
            try:
                record = f.read_record(first)
                f.close()
            except Exception as e:
                # This is very unlikely to happen as index_records has already
                # done the sanity checking needed for succesfully reading the
                # record.
                # However read_records can in theory still fail on blocked IO
                # and other non-LIS related issues.
                msg =  'dlisio.lis.load: Could not read record {}, indexing stopped\n'
                msg += 'Reason: {}\nFilepath: {}'
                logging.error(msg.format(first, e, path))
                f.close()
                break

            if first.type == core.lis_rectype.reel_header:
                reel = HeaderTrailer(record)

            elif first.type == core.lis_rectype.reel_trailer:
                # The reel is already assigned to the LF's at this point, so
                # just assign the trailer to that instance before initiating a
                # new instance for the next reel.
                reel.rawtrailer = record
                reel = HeaderTrailer()

            elif first.type == core.lis_rectype.tape_header:
                tape = HeaderTrailer(record)

            elif first.type == core.lis_rectype.tape_trailer:
                # The tape is already assigned to the LF's at this point, so
                # just assign the trailer to that instance before initiating a
                # new instance for the next tape.
                tape.rawtrailer = record
                tape = HeaderTrailer()

        else:
            logfile = LogicalFile(path, f, index, reel, tape)
            logical_files.append(logfile)

        if truncated: break

    if truncated:
        msg =  'dlisio.lis.load: Stopped indexing around tell {}\n'
        msg += 'Reason: File likely truncated\nFilepath: {}'
        logging.error(msg.format(offset, path))

    return PhysicalFile(logical_files)


def is_delimiter(recinfo):
    if recinfo is None: return False

    if recinfo.type == core.lis_rectype.reel_header:  return True
    if recinfo.type == core.lis_rectype.reel_trailer: return True
    if recinfo.type == core.lis_rectype.tape_header:  return True
    if recinfo.type == core.lis_rectype.tape_trailer: return True
    if recinfo.type == core.lis_rectype.logical_eof:  return True
    return False
