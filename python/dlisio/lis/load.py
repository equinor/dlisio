import logging

from .. import core
from .file import logical_file, physical_reel

def load(path):
    """ Loads and indexes a file

    A LIS file is typically segmented into multiple Logical Files (LF). LF's
    are just a way to group information that logically belongs together. LF's
    are completely independent of each other and can generally be treated as if
    they were different files on disk. In fact - that's just what load does.
    Each logical file gets its own io-device and is completely segmented from
    other LF's.

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

    lis : dlisio.lis.physical_reel
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
    # Opening a lfp tapeimage protocol at a type 1 tapemarks cause an instant
    # EOF. Hence we have to find the offset of the first type 0 tapemark, which
    # will be the start of our logical file.
    if is_tif:
        while tm.type != 0:
            tm = read_as_tapemark(f)
        offset = f.ptell - 12

    f.close()

    files = []
    while True:
        # Open a new file-handle until we hit EOF
        try:
            f = core.openlis(path, offset, is_tif)
        except EOFError:
            break
        index = f.index_records()
        files.append( logical_file(path, f, index) )

        if f.istruncated():
            msg = 'logical file nr {} is truncated'
            logging.info(msg.format(len(files)))
            break

        offset = f.poffset() + f.psize()

    return physical_reel(files)
