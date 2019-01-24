import numpy as np
from . import core


try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

def load(path):
    return dlis(path)


class channel(object):
    def __init__(self, ch):
        self.name          = ch.name
        self.long_name     = ch.long_name
        self.properties    = ch.properties
        self.reprc         = ch.reprc
        self.units         = ch.units
        self.dimension     = ch.dimension
        self.axis          = ch.axis
        self.element_limit = ch.element_limit
        self.source        = ch.source

    def __repr__(self):
        return "dlisio.core.channel({})".format(self.name)

    def __str__(self):
        s = "channel object\n"
        s += "name\t\t: {}\n".format(self.name)
        s += "long name\t: {}\n".format(self.long_name)
        s += "properties\t: {}\n".format(self.properties)
        s += "reprc\t: {}\n".format(self.reprc)
        s += "units\t: {}\n".format(self.units)
        s += "dimension\t: {}\n".format(self.dimension)
        s += "axis\t\t: {}\n".format(self.axis)
        s += "elem-limit\t: {}\n".format(self.element_limit)
        s += "source\t: {}\n".format(self.source)
        return s


class frame(object):
    def __init__(self, fr):
        self.name        = fr.name
        self.description = fr.description
        self.channels    = fr.channels
        self.index_type  = fr.index_type
        self.direction   = fr.direction
        self.spacing     = fr.spacing
        self.encrypted   = fr.encrypted
        self.index_min   = fr.index_min
        self.index_max   = fr.index_max

    def __repr__(self):
        return "dlisio.core.frame({})".format(self.name)

    def __str__(self):
        s = "frame object\n"
        s += "name\t\t: {}\n".format(self.name)
        s += "description\t: {}\n".format(self.description)
        s += "channels\t: {}\n".format(self.channels[0])
        for ch in self.channels[1:]:
            s += "\t\t  {}\n".format(ch)
        s += "index-type\t: {}\n".format(self.index_type)
        s += "direction\t: {}\n".format(self.direction)
        s += "spacing\t: {}\n".format(self.spacing)
        s += "encrypted\t: {}\n".format(self.encrypted)
        s += "index_min\t: {}\n".format(self.index_min)
        s += "index_max\t: {}\n".format(self.index_max)
        return s

    def haschannel(self, id=None, origin=None, copy=None):
        """Channel matching

        Returns True if at least one channel in frame.channels match all
        spesified parameters. Otherwise return False

        Parameters
        ----------
        id     : string-like
        origin : int
        copy   : int

        Returns
        -------
        bool
        """

        def match(field, ch, key):
            if field == "i" and ch.id         == key: return True
            if field == "o" and ch.origin     == key: return True
            if field == "c" and ch.copynumber == key: return True
            return False

        for ch in self.channels:
            if id is not None:
                if not match("i", ch, id): continue
            if origin is not None:
                if not match("o", ch, origin): continue
            if copy is not None:
                if not match("c", ch, copy): continue
            return True

        return False


class unknown_object(object):
    def __init__(self, obj):
        self.name = obj.name
        self.attr = { key : obj[key] for key in obj.keys() }

    def __getitem__(self, key):
        return self.attr[key]

    def __repr__(self):
        return "dlisio.core.unknown-object({})".format(self.name)

    def __str__(self):
        s  = "unknown object:\n"
        for _, value in self.attr.items():
            s += "{} \n".format(value)
        return s


class dlis(object):
    def __init__(self, path):
        self.fp = core.file(path)
        self.sul = self.fp.sul()
        self.bookmarks, self.explicits, self.implicits = self.fp.mkindex()

        self._channels    = []
        self._frames      = []
        self._unknown_obj = []
        self._fileheader  = None

        for ex in self.explicits:
            for obj in ex.objects:
                if ex.type == 'CHANNEL':
                    self._channels.append(channel(obj))
                elif ex.type == 'FRAME':
                    self._frames.append(frame(obj))
                elif ex.type == 'FILE-HEADER':
                    self._fileheader = obj
                else:
                    self._unknown_obj.append(unknown_object(obj))

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

    def channels_matching(self, key):
        frames = {}
        for frame in self.frames:
            for channeli, channel in enumerate(frame.channels, 1):
                if channel.id != key: continue
                frames[frame] = {
                        'names': frame.channels[:channeli],
                        'channels': [],
                    }
                break


        if len(frames) == 0:
            raise ValueError('found no frame with the CHANNEL {}'.format(key))

        for ch in self.channels:
            for frame, data in frames.items():
                if ch.name in data['names']:
                    data['channels'].append(ch)
        return frames

    @property
    def channels(self):
        return self._channels

    @property
    def frames(self):
        return self._frames

    @property
    def unknown_obj(self):
        return self._unknown_obj

    @property
    def fileheader(self):
        return self._fileheader
