from . import core


try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

def load(path):
    return dlis(path)

class dlis(object):
    def __init__(self, path):
        self.fp = core.file(path)
        self.sul, self.bookmarks = self.fp.mkindex()

    def raw_record(self, i):
        """Get a raw record (as bytes)

        Read the logical record i, but make no attempt to parse it. Use this if
        the file for some reason is not read correctly, to either debug or
        recover.

        Parameters
        ----------
        i : int

        Returns
        -------
        record : bytes

        Notes
        -----
        Under normal operation, this method is not necessary at all. It's meant
        as an escape hatch for inspection or custom record parsing, should
        something else be very wrong. If you find you need to use this function
        a lot, please report it as an issue.
        """
        return self.fp.raw_record(self.bookmarks[i])

    def close(self):
        """Close the file

        This method is mostly useful for testing.

        It is not necessary to call this method if you're using the `with`
        statement, which will close the file for you. Calling methods on a
        previously-closed file will raise `IOError`.
        """

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.fp.close()
