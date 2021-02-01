from .. import core

class logical_file():
    """ Logical File (LF)

    A LIS file is typically segmented into multiple logical files. LF's are
    just a way to group information that logically belongs together. LF's are
    completely independent of each other and can generally be treated as if
    they were different files on disk. In fact - that's just what dlisio does.
    Each logical file gets its own io-device and is completely segmented from
    other LF's.
    """
    def __init__(self, io, index):
        self.io = io
        self.index = index

    def close(self):
        self.io.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        return 'logical_file'

    @property
    def header(self):
        """ Logical File Header

        """
        pass

    @property
    def trailer(self):
        """ Logical File Trailer

        Returns the Logical File Trailer - if present. Othervise returns None.

        Returns
        -------

        trailer : dlisio.core.log_file_trailer or None


        """
        pass


    def parse_record(self, recinfo):
        # This can be C++ function (although what about the return type?)
        rec = self.io.read_record(recinfo)

        rtype = recinfo.type
        if   rtype == core.rectype.format_spec: return core.parse_dfsr(rec)
        elif rtype == core.rectype.reelheader:  return core.parse_reelheader(rec)
        else:
            raise NotImplementedError("No parsing rule for  {}".format(rtype))


    @property
    def explicits(self):
        return self.index.explicits()

    def dfsr(self):
        # TODO duplication checking
        # TODO Maybe we want a factory function in c++ for extraction (and
        # parsing) all records of a given type. To avoid crossing the language
        # barrier so much
        parsed = []
        for recinfo in self.explicits:
            if recinfo.type != core.lis_rectype.format_spec: continue
            rec = self.io.read_record(recinfo)
            parsed.append( core.parse_dfsr(rec) )

        return parsed

class physical_reel(tuple):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        for f in self:
            f.close()

    def __repr__(self):
        return 'physical_reel(logical files: {})'.format(len(self))

