import numpy as np
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
        self.sul = self.fp.sul()
        self.bookmarks, self.explicits, self.implicits = self.fp.mkindex()

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

    def getcurves(self, key):
        curves = {}
        for frame, data in self.channels_matching(key).items():
            root = frame.name
            root = (root.origin, root.copynumber, root.id)

            channel = data['channels'].pop()
            count = np.prod(channel.dimension)
            dtype = channel.reprc

            implicits = self.implicits[root]
            pre = [(np.prod(c.dimension), c.reprc) for c in data['channels']]

            a = []
            for implicit in implicits:
                a.append(self.fp.iflr(implicit, pre, count, dtype))

            curves[root] = np.array(a)

        return curves

    def channel_metadata(self, objname):
        for ex in self.explicits:
            if ex.type != 'CHANNEL':
                continue

            for o in ex.objects:
                if o.name == objname:
                    return o

        raise ValueError('Could not find object {}'.format(objname))

    def channels_matching(self, key):
        frames = {}
        for ex in self.explicits:
            if ex.type != 'FRAME':
                continue

            for frame in ex.objects:
                for channeli, channel in enumerate(frame.channels, 1):
                    if channel.id != key: continue
                    frames[frame] = {
                            'names': frame.channels[:channeli],
                            'channels': [],
                        }
                    break


        if len(frames) == 0:
            raise ValueError('found no frame with the CHANNEL {}'.format(key))

        for ex in self.explicits:
            if ex.type != 'CHANNEL': continue

            for ch in ex.objects:
                for frame, data in frames.items():
                    if ch.name in data['names']:
                        data['channels'].append(ch)
        return frames

