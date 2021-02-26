from .. import core

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
    dlisio.dlis.load
    dlisio.lis.load
    """
    return core.open(str(path), offset)
