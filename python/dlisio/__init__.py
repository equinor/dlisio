from . import core
from . import plumbing
from .settings import get_encodings, set_encodings
from .file import physicalfile, logicalfile

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass


def open(path):
    """ Open a file

    Open a low-level file handle. This is not intended for end-users - rather,
    it's an escape hatch for very broken files that dlisio cannot handle.

    Parameters
    ----------
    path : str_like

    Returns
    -------
    stream : dlisio.core.stream

    See Also
    --------
    dlisio.load
    """
    return core.open(str(path))

def load(path):
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
    sulsize = 80
    tifsize = 12
    lfs = []

    def rewind(offset, tif):
        """Rewind offset to make sure not to miss VRL when calling findvrl"""
        offset -= 4
        if tif: offset -= 12
        return offset

    path = str(path)
    stream = open(path)
    try:
        offset = core.findsul(stream)
        sul = stream.get(bytearray(sulsize), offset, sulsize)
        offset += sulsize
    except:
        offset = 0
        sul = None
    try:
        tapemarks = core.hastapemark(stream)
        offset = core.findvrl(stream, offset)

        # Layered File Protocol does not currently offer support for re-opening
        # files at the current position, nor is it able to precisly report the
        # underlying tell. Therefore, dlisio has to manually search for the
        # VRL to determine the right offset in which to open the new filehandle
        # at.
        #
        # Logical files are partitioned by core.findoffsets and it's required
        # [1] that new logical files always start on a new Visible Record.
        # Hence, dlisio takes the (approximate) tell at the end of each Logical
        # File and searches for the VRL to get the exact tell.
        #
        # [1] rp66v1, 2.3.6 Record Structure Requirements:
        #     > ... Visible Records cannot intersect more than one Logical File.
        while True:
            if tapemarks: offset -= tifsize
            stream.seek(offset)
            if tapemarks: stream = core.open_tif(stream)
            stream = core.open_rp66(stream)

            explicits, implicits = core.findoffsets(stream)
            hint = rewind(stream.absolute_tell, tapemarks)

            recs  = core.extract(stream, explicits)
            sets  = core.parse_objects(recs)
            pool  = core.pool(sets)
            fdata = core.findfdata(stream, implicits)

            lf = logicalfile(stream, pool, fdata, sul)
            lfs.append(lf)

            try:
                stream = core.open(path)
                offset = core.findvrl(stream, hint)
            except RuntimeError:
                if stream.eof():
                    stream.close()
                    break
                raise

        return physicalfile(lfs)
    except:
        stream.close()
        for f in lfs:
            f.close()
        raise
