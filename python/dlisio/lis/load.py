import logging

from .. import core
from .file import logical_file, physical_reel

def load(path):
    """ Loads a file and returns one filehead

    Parameters
    ----------

    path : str_like
        path to lis-file


    Returns
    -------

    lis : dlisio.lis.physicalfile

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
        files.append( logical_file(f, index) )

        if f.istruncated():
            msg = 'logical file nr {} is truncated'
            logging.info(msg.format(len(files)))
            break

        offset += f.psize()



    return physical_reel(files)
