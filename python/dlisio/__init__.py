__version__ = '0.0.0'

from . import core

def load(path):
    return dlis(path)

class dlis(object):
    def __init__(self, path):
        self.fp = core.file(path)
        self.sul = self.fp.sul()

        self.bookmarks = []
        self.formatting = []
        off = 0
        while not self.fp.eof():
            pos, off, explicit = self.fp.mark(off)

            self.formatting.append(explicit)
            self.bookmarks.append(pos)

    def __getitem__(self, i):
        return self.fp.getrecord(self.bookmarks[i])

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
