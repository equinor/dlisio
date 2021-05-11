from .. import core

class DataFormatSpec():
    """Data Format Specification Record (DFSR)

    This is dlisio's main interface for accessing Data Format Specification
    Records. A DFSR describes some arbitrary set of channels/curves that are
    recorded together along some common index.

    The DFSR contains two main categories of data: Entry Blocks & Spec
    Blocks.

    **Entry Blocks (EB)**

    EBs are a set of well-defined properties that applies to the DFSR.
    These are implemented as properties on this class. E.g.
    :attr:`dlisio.lis.DataFormatSpec.depth_units` and
    :attr:`dlisio.lis.DataFormatSpec.direction`.

    **Spec Blocks (SB)**

    SB's contain information about a single channel/curve in this DFSR such as
    mnemonics, units and dimensions of the curves. These can be accessed
    through :attr:`dlisio.lis.DataFormatSpec.specs`.

    Notes
    -----

    For those familiar with DLIS, DFSRs are analogous to DLIS frames
    :class:`dlisio.dlis.Frame`.

    See also
    --------

    dlisio.lis.curves : Read the curves described by a DataFormatSpec

    """

    def __init__(self, attic):
        self.attic = attic
        self.default_index_mnem = 'DEPT'

    def __repr__(self):
        return 'DataFormatSpec()'

    @property
    def info(self):
        return self.attic.info

    @property
    def index_mnem(self):
        """ Mnemonic of the index

        Returns
        -------

        mnemonic : str
        """
        nspecs = len(self.specs)
        if self.depth_mode == 0 and nspecs == 0: return None
        if self.depth_mode == 0 and nspecs >  0: return self.specs[0].mnemonic
        if self.depth_mode == 1:                 return self.default_index_mnem

    @property
    def index_units(self):
        """ Units of the index

        Returns
        -------

        units : str
        """
        nspecs = len(self.specs)
        if self.depth_mode == 0 and nspecs == 0: return None
        if self.depth_mode == 0 and nspecs >  0: return self.specs[0].units
        if self.depth_mode == 1:                 return self.depth_units

    def sample_rates(self):
        """ Return all sample rates used by (non-index) Channels in this DFSR

        Returns
        -------

        rates : set of ints
        """
        first = 1 if self.depth_mode == 0 else 0
        return { x.samples for x in self.specs[first:] }

    @property
    def specs(self):
        """ Spec Blocks (SB)

        Gives access to the underlying Spec Blocks. A Spec Block is the LIS79
        structure that defines channels/curves. Each Spec Block defines one
        channel and its properties.

        LIS79 defines 2 different Spec Block types, namely subtype 0 and 1.
        These mostly share the same attributes, but there are a couple of
        attributes that differ between the 2 subtypes. :attr:`spec_block_type`
        defines which of the 2 subtypes is being used in the DFSR.

        See also
        --------

        dlisio.core.spec_block_0 : Speck Block - subtype 0
        dlisio.core.spec_block_1 : Speck Block - subtype 1
        """
        return self.attic.specs

    @property
    def entries(self):
        """ Entry Blocks (EB)

        Gives access to the underlying Entry Blocks. The average user is
        advised to interact with the Entry Blocks through the properties of
        this class. E.g. absent_value, depth_units etc..
        """
        return self.attic.entries

    @property
    def absent_value(self):
        """Absent Value

        A default value that is used in the frame to indicate that the entry
        has no valid data and should be ignored.
        """
        eb = core.lis_ebtype.absent_value
        return self.entry_value(eb, default=-999.25)

    @property
    def depth_mode(self):
        """Depth Recording Mode

        The mode in which the depth is recorded in the file. This is mainly an
        implementation detail and the mode used will not affect the end-user of
        dlisio in any way.
        """
        eb = core.lis_ebtype.depth_rec_mode
        return self.entry_value(eb, default=0)

    @property
    def depth_reprc(self):
        """Datatype of depth/index channel

        The datatype that the depth/index channel is recorded as. This is a
        number corresponding to LIS79-specific types.
        """
        eb = core.lis_ebtype.reprc_output_depth
        return self.entry_value(eb)

    @property
    def depth_units(self):
        """Units of depth/index channel

        This is typically only defined when :attr:`depth_mode` is 1. When depth
        mode is 0, the depth channel is defined by the first Spec Block in
        :attr:`specs`.

        If you don't care about the depth recoding mode and just want the units
        of the index, use :attr:`index_units` instead.
        """
        eb = core.lis_ebtype.units_of_depth
        return self.entry_value(eb, default='.1IN')

    @property
    def direction(self):
        """Direction of the acquisition

        This UP/DOWN flag indicated whether the measurements where taken going
        upwards or downwards in the well. A value of 1 means UP, 255 means DOWN
        while 0 means "neither". Any other value is unspecified by LIS79.
        """
        eb = core.lis_ebtype.up_down_flag
        return self.entry_value(eb, default=1)

    @property
    def frame_size(self):
        """The size of one frame (row)

        This refers to the size (in bytes) of one row of data in the file.

        Notes
        -----

        LIS79 uses custom datatypes which do not exist on modern computers.
        This means that the frame size (dtype.itemsize) of the numpy arrays
        produced by dlisio may not always correspond to the frame size on disk.
        """
        eb = core.lis_ebtype.frame_size
        return self.entry_value(eb)

    @property
    def max_frames(self):
        """Maximum frames per Logical Record

        The maximum frames (rows) recorded per Logical Record. This refers to
        the fact that the log data is partitioned onto multiple Logical Record,
        but that is an implementation detail that most users do not need to
        care about.
        """
        eb = core.lis_ebtype.max_frames_pr_rec
        return self.entry_value(eb)

    @property
    def optical_log_depth_units(self):
        """Optical Log Depth Scale Units

        This flag specifies the depth units used on the optical log on the
        original recording. A value of 1 means 'feet', 255 means 'meters' while
        0 means 'time'. Any other value is unspecified by LIS79.
        """
        eb = core.lis_ebtype.depth_scale_units
        return self.entry_value(eb, default=1)

    @property
    def record_type(self):
        """Data Record Type

        Indicated the Logical Record type which is used to store the data which
        is described by this Data Format Specification Record.

        Notes
        -----

        Only Logical Record Type 0 (normal data) was ever defined by LIS79.
        Hence this attribute has little semantic value.
        """
        eb = core.lis_ebtype.data_rec_type
        return self.entry_value(eb, default=0)

    @property
    def reference_point(self):
        """Data Reference Point

        LIS79 defined the Data Reference Point as:

            Data Reference Point - There is a point on the tool string called
            the tool reference point. Its distance from the surface corresponds
            to measured depth. The data reference point is another point which
            is fixed relative to the tool string. At any instant during the
            real-time acquisition of data, the data reference point stands
            opposite the part of the hole to which the current output
            corresponds. This value is the distance of the data reference point
            above the tool reference point. It may be positive or negative. It
            is useful in determining the significance of data, such as tension
            or frame duration, which are not actually a function of depth. If
            absent, the value is undefined on the tape.
        """
        eb = core.lis_ebtype.ref_point
        return self.entry_value(eb)

    @property
    def reference_point_units(self):
        """Reference point units

        Units of the reference point described by
        :attr:`dlisio.lis.DataFormatSpec.reference_point`.
        """
        eb = core.lis_ebtype.ref_point_units
        return self.entry_value(eb, default='.1IN')

    @property
    def spacing(self):
        """Frame Spacing

        Depth difference between consecutive frames
        """
        eb = core.lis_ebtype.spacing
        return self.entry_value(eb)

    @property
    def spacing_units(self):
        """Frame Spacing Units

        Units of the frame spacing described by
        :attr:`dlisio.lis.DataFormatSpec.spacing`.
        """
        eb = core.lis_ebtype.spacing_units
        return self.entry_value(eb, default='.1IN')

    @property
    def spec_block_type(self):
        """Spec Block Type

        Defines which Block type is being used. Default is 0.
        """
        eb = core.lis_ebtype.data_rec_type
        return self.entry_value(eb, default=0)

    @property
    def spec_block_subtype(self):
        """Spec Block Subtype

        There are two different subtype of the Spec Blocks (0 or 1). These
        have slightly different properties.
        """
        eb = core.lis_ebtype.spec_bloc_subtype
        return self.entry_value(eb, default=0)

    def directional_spacing(self):
        if self.spacing is None:
            raise ValueError('No spacing recorded')

        # direction == 1 means that the logset is logged going up-hole. I.e the
        # depth (or other index) is _decreasing_. The spacing, which is used to
        # calculate next depths, is always positive. Here we flip its sign such
        # that later depth calculation can always *add* spacing and get the
        # correct result:
        #
        #  next = current + (-spacing)
        #
        # I.e. decreasing
        if self.direction == 1:   return -self.spacing
        if self.direction == 255: return self.spacing

        msg = 'Invalid direction (UP/DOWN flag). was: {}'
        raise ValueError(msg.format(self.direction))

    def entry_value(self, entry_type, default=None):
        entry = self.find_entry(entry_type)
        return entry.value if not entry is None else default

    def find_entry(self, entry_type):
        entry = [x for x in self.attic.entries if x.type == int(entry_type)]

        if len(entry) == 0:
            return None

        elif len(entry) == 1:
            return entry[0]

        msg = 'Multiple Entry Blocks of type {}'
        raise ValueError(msg.format(entry_type))

