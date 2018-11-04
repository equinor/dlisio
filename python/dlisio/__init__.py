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
        self.sul, self.bookmarks, self.explicits, self.implicits = self.fp.mkindex()

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
        _, channels = self.channels_matching(key)

        curves = {}
        for chs in channels.values():
            channel = chs[-1]
            root = channel['root']
            elems = channel['len'][0]
            dtype = channel['repr'][0]

            implicits = self.implicits[root]

            pre = [(c['len'][0], c['repr'][0]) for c in chs[:-1]]

            a = []
            for implicit in implicits:
                a.append(self.fp.iflr(implicit, pre, elems, dtype))

            curves[root] = np.array(a)

        return curves

    def channel_metadata(self, objname):
        out = {}
        for ex in self.explicits:
            if ex['type'] != 'CHANNEL':
                continue

            if objname not in ex['objects']:
                continue

            for prop in ex['objects'][objname]:
                if prop['label'] == 'REPRESENTATION-CODE':
                    out['repr'] = prop['value']

                if prop['label'] == 'ELEMENT-LIMIT':
                    out['len'] = prop['value']

                if prop['label'] == 'DIMENSION':
                    out['dim'] = prop['value']
        return out

    def channels_matching(self, key):
        positions = {}
        for exi, ex in enumerate(self.explicits):
            if ex['type'] != 'FRAME':
                continue
            for name, properties in ex['objects'].items():
                for propi, prop in enumerate(properties):
                    if prop['label'] != 'CHANNELS':
                        continue
                    for channeli, (_, _, channel) in enumerate(prop['value']):
                        if channel != key:
                            continue
                        positions[name] = [exi, 'objects', name, propi, 'value', channeli]

        if len(positions) == 0:
            raise ValueError('found no frame with the CHANNEL {}'.format(key))

        attr = {}
        for root, directory in positions.items():
            ch = self.explicits
            for d in directory[:-1]:
                ch = ch[d]

            channel = ch[directory[-1]]
            attr[channel] = []

            # gather all preceeding channels in the frame, with their metadata
            # (representation code, elem-count) so that they can be parsed to
            # read out the appropriate curve
            #
            # The requested channel is at [-1]
            for index, c in enumerate(ch[:directory[-1]+1]):
                d = { 'index': index, 'root': root }
                d.update(self.channel_metadata(c))
                attr[channel].append(d)

        return positions, attr
