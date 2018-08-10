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
