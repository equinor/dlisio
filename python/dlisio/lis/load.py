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
    f = core.open(path, 0)
    tm = core.read_tapemark(f)
    f.close()

    offset = 0
    tapeimage = core.valid_tapemark(tm)
    if tapeimage and tm.type == 1: offset += 12

    files = []
    while True:
        # Open a new file-handle until we hit EOF
        try:
            f = core.openlis(path, offset, tapeimage)
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
