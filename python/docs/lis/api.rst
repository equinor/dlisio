LIS API Reference
=================

.. currentmodule:: dlisio.lis

Load a LIS-file
---------------
.. autofunction:: dlisio.lis.load

LIS Physical File
-----------------
.. autoclass:: dlisio.lis.PhysicalFile()

LIS Logical File
-----------------
.. autoclass:: dlisio.lis.LogicalFile()

LIS Curves
----------
.. autofunction:: dlisio.lis.curves()
.. autofunction:: dlisio.lis.curves_metadata()

LIS Logical Records
-------------------

.. note::
   dlisio's LIS reader is not yet feature complete and the following list does
   not reflect the full set of Logical Records defined in LIS79.

File Header (FHLR)
..................
.. class:: dlisio.core.file_header

    File Header Logical Record (FHLR)

    .. attribute:: file_name

        File Name - A unique, fixed length, name for a Logical File within a
        Logical Tape. The file name consists of two parts:

        **Service name** - A 6 character Name of the service or program that
        created the tape

        **File number** - A 3 character counter that counts the files in a logical tape

        The service name and file number are seperated by a dot (".")

        :type: str

    .. attribute:: service_sublvl_name

        Service Sub Level Name - Subdevision of the Service ID that is used to
        further classify the source of data.

        :type: str

    .. attribute:: version_number

        Version number for the software that wrote the original data

        :type: str

    .. attribute:: date_of_generation

        Date of generation for the software that wrote the original data.
        Format: Year/Month/Day

        :type: str

    .. attribute:: max_pr_length

        Maximum physical record length

        :type: str

    .. attribute:: file_type

        Indicator for the kind of information in the file. For example: LL for
        label, LO for log data or CA for Calibration

        :type: str

    .. attribute:: prev_file_name

        Optional previous file number. When used, it has the same format as :attr:`file_name`.

        :type: str

File Trailer (FTLR)
...................
.. class:: dlisio.core.file_trailer

    File Trailer Logical Record (FTLR)

    The FTLR is an optional last record of a Logical File. It's identical to
    the :class:`dlisio.core.file_header` with exception of the attribute
    :attr:`dlisio.core.file_header.prev_file_name`, which in the trailer is replaced with
    :attr:`next_file_name`.

    .. attribute:: file_name
    .. attribute:: service_sublvl_name
    .. attribute:: version_number
    .. attribute:: date_of_generation
    .. attribute:: max_pr_length
    .. attribute:: file_type
    .. attribute:: next_file_name

        Optional next file number. When used, it has the same format as :attr:`file_name`.

        :type: str

Tape Header (THLR)
..................
.. class:: dlisio.core.tape_header()

    Tape Header Logical Record (THLR)

    .. attribute:: service_name

        The name of the service or program that created the tape. This name is
        used as the service name in :attr:`dlisio.core.file_header.file_name`
        (and :attr:`dlisio.core.file_trailer.file_name`) for all Logical Files
        in the tape

        :type: str

    .. attribute:: date

        Date when the original data was acquired. Format: Year/Month/Day

        :type: str

    .. attribute:: origin_of_data

        The system that originally acquired or created the data

        :type: str

    .. attribute:: name

        Tape name - An ID that can aid to identify the Logical Tape, where applicable

        :type: str

    .. attribute:: continuation_number

        Tape continuation number - sequential ordering of tapes on the same reel

        :type: str

    .. attribute:: comment

        Any relevant remarks concerning the Logical Tape or the content of it

        :type: str

    .. attribute:: prev_tape_name

        An ID that can be used to identify the previous Logical Tape, where
        applicable. Should be blank for the first tape

        :type: str

Tape Trailer (TTLR)
...................
.. class:: dlisio.core.tape_trailer()

    Tape Trailer Logical Record (TTLR)

    The TTLR is optional. It's identical to the
    :class:`dlisio.core.tape_header` with exception of the attribute
    :attr:`dlisio.core.tape_header.prev_tape_name`, which in the trailer is
    replaced with :attr:`next_tape_name`.

    .. attribute:: service_name
    .. attribute:: date
    .. attribute:: origin_of_data
    .. attribute:: name
    .. attribute:: continuation_number
    .. attribute:: comment
    .. attribute:: next_tape_name

        An ID that can be used to identify the next Logical Tape, where
        applicable. Should be blank for the last tape

        :type: str

Reel Header (RHLR)
..................
.. class:: dlisio.core.reel_header()

    Reel Header Logical Record (RHLR)

    .. attribute:: service_name

        The name of the service or program that created the tape. This name is
        used as the service name in :attr:`dlisio.core.file_header.file_name`
        (and :attr:`dlisio.core.file_trailer.file_name`) for all Logical Files
        in the tape

        :type: str

    .. attribute:: date

        Date when the physical reel was created. Format: Year/Month/Day

        :type: str

    .. attribute:: origin_of_data

        The system that originally acquired or created the data

        :type: str

    .. attribute:: name

        Reel name - A 8 character name used to identify a specific reel of
        tape. This name matches the visual identification written on the tape
        container

        :type: str

    .. attribute:: continuation_number

        A number sequentially ordering multiple physical reels. The value is in
        the range 1 to 99

        :type: str

    .. attribute:: comment

        Any relevant remarks related to the physical reel of tape

    .. attribute:: prev_reel_name

        An ID that can be used to identify the previous Physical Reel, where
        applicable.

        :type: str

Reel Trailer (RTLR)
...................
.. class:: dlisio.core.reel_trailer()

    Reel Trailer Logical Record (RTLR)

    The RTLR is optional. It's identical to the
    :class:`dlisio.core.reel_header` with exception of the attribute
    :attr:`dlisio.core.reel_header.prev_reel_name`, which in the trailer is
    replaced with :attr:`next_reel_name`.

    .. attribute:: service_name
    .. attribute:: date
    .. attribute:: origin_of_data
    .. attribute:: name
    .. attribute:: continuation_number
    .. attribute:: comment
    .. attribute:: next_reel_name

        An ID that can be used to identify the next Physical Reel, where
        applicable.

        :type: str

Data Format Specification
.........................
.. autoclass:: dlisio.lis.DataFormatSpec()

Job Identification
..................

Job Identification Logical Records implement the interface of
:class:`dlisio.lis.InformationRecord`

Tool String Info
................

Tool String Info Logical Records implement the interface of
:class:`dlisio.lis.InformationRecord`

Wellsite Data
.............

Wellsite Data Logical Records implement the interface of
:class:`dlisio.lis.InformationRecord`

Operator Command Inputs
.......................

Operator Command Inputs Records implement the interface of
:class:`dlisio.core.text_record`

Operator Response Inputs
........................

Operator Response Inputs Records are used to store input issued to the operator in
response to a system request for information. They implement the interface of
:class:`dlisio.core.text_record`

System Outputs to Operator
..........................

System Outputs to Operator Records are used to store system output messages
issued by the operator. They implement the interface of
:class:`dlisio.core.text_record`

FLIC Comment
............

Comment Records implement the interface of :class:`dlisio.core.text_record`

LIS Structures
--------------

Other structures defined by LIS79

.. class:: dlisio.core.spec_block_0()

    Spec Block - Subtype 0

    A Spec Block contains information needed to correctly parse one channel from
    a frame. It also contains useful information such as the units of the curve
    measurement.

    .. note::
        For those familiar with DLIS, Spec Blocks are analogous to DLIS
        Channels :class:`dlisio.dlis.Channel`.

    .. attribute:: mnemonic

        Name of the channel

        :type: str

    .. attribute:: service_id

        The service ID identifies the tool, the tool string used to measure the
        datum, or the name of the computed product.

        :type: str

    .. attribute:: service_order_nr

        A unique number which identifies the logging trip to the well-site.

        :type: str

    .. attribute:: units

        Units of the channel

        :type: str

    .. attribute:: file_nb

        Indicates the file number at the time the data was first acquired and
        written (for well-site data acquisitions only). This number, together
        with service_id and service_order_nr will uniquely identify any data
        string for the purpose of merging or other processing.

        :type: int

    .. attribute:: reserved_size

        The number of bytes reserved for this channel in the frame. If size is
        negative, the output is suppressed. The space is still reserved, and is
        the absolute value of this entry.

        :type: int

    .. attribute:: samples

        The number of samples recorded per frame. When samples == 1, the
        channel is sampled at the same interval as the index of the frame.

        :type: int

    .. attribute:: reprc

        The type of the recorded channel data. This number refers to one of the
        LIS79-defined data types.

        :type: int

    .. attribute:: api_log_type

        This, together with the attributes :attr:`api_curve_type`,
        :attr:`api_curve_class` and :attr:`api_modifier` form a largly outdated
        log/curve code system utilizing a 2 digit curve code. Ref API Bulletin
        D-9 Feb '79.

        :type: int

    .. attribute:: api_curve_type

        See :attr:`api_log_type`.

        :type: int

    .. attribute:: api_curve_class

        See :attr:`api_log_type`.

        :type: int

    .. attribute:: api_modifier

        See :attr:`api_log_type`.

        :type: int

    .. attribute:: process_level

        Process level is a measure of the amount of processing done to obtain
        the curve. The size of the number increases in proportion to the amount
        of processing. However, the system has never been objectively defined.

        :type: int

.. class:: dlisio.core.spec_block_1()

    Spec Block - Subtype 1

    Spec Blocks subtype 1 share most of its attributes with
    :class:`dlisio.core.spec_block_0`. However, there are 3 notable differences:

    - The ``api_*``-attributes are replaced with :attr:`api_codes`
    - Subtype 1 has no ``process_level``
    - Subtype 1 defines :attr:`process_indicators`, which do not exist in subtype 0.

    .. attribute:: mnemonic
    .. attribute:: service_id
    .. attribute:: service_order_nr
    .. attribute:: units
    .. attribute:: file_nb
    .. attribute:: reserved_size
    .. attribute:: samples
    .. attribute:: reprc
    .. attribute:: api_codes

        API codes form a log/curve system featuring a 3-digit curve code (Ref:
        API Bulletin D-9 Jul '79). The API codes are represented as a 32 bit
        integer. The 8-digit number can be masked out to dd/ddd/dd/d. E.g
        ``45310011`` should be interpreted as::

        - Log Type    = 45
        - Curve Type  = 310
        - Curve Class = 01
        - Modifier    = 1

        :type: int

    .. attribute:: process_indicators

        Process Indicators are used to define different processes or
        corrections that have been performed on the channel. The process
        indicators are defined as a bit-mask of 40 bits:

        ======= ===========================================
        Bit nr  Definition
        ======= ===========================================
        0-1     original logging direction [1]
        2       true vertical depth correction
        3       data channel not on depth
        4       data channel is filtered
        5       data channel is calibrated
        6       computed (processed thru a function former)
        7       derived (computed from more than one tool)
        8       tool defined correction nb 2
        9       tool defined correction nb 1
        10      mudcake correction
        11      lithology correction
        12      inclinometry correction
        13      pressure correction
        14      hole size correction
        15      temperature correction
        22      auxiliary data flag
        23      schlumberger proprietary
        ======= ===========================================

        A value of 1 for a specific bit means that the correction or process is
        applied. Note that bits not listed in the table are undefined /
        unassigned  by LIS79.

        [1] Bits 0 and 1 form a single entry that defines the original logging
        direction for this channel. A value of '01' (1) indicates down-hole.
        '10' (2) indicated up-hole, while '00' (0) indicates an ambiguous
        direction. I.e.  stationary. '11' (3) is undefined.

        For convenience the bitmask is expanded to an object with all the above
        definitions as attributes.

        :type: dlisio.core.process_indicators

.. class:: dlisio.core.process_indicators()

    .. attribute:: original_logging_direction
        :type: int
    .. attribute:: true_vertical_depth_correction
        :type: bool
    .. attribute:: data_channel_not_on_depth
        :type: bool
    .. attribute:: data_channel_is_filtered
        :type: bool
    .. attribute:: data_channel_is_calibrated
        :type: bool
    .. attribute:: computed
        :type: bool
    .. attribute:: derived
        :type: bool
    .. attribute:: tool_defined_correction_nb_2
        :type: bool
    .. attribute:: tool_defined_correction_nb_1
        :type: bool
    .. attribute:: mudcake_correction
        :type: bool
    .. attribute:: lithology_correction
        :type: bool
    .. attribute:: inclinometry_correction
        :type: bool
    .. attribute:: pressure_correction
        :type: bool
    .. attribute:: hole_size_correction
        :type: bool
    .. attribute:: temperature_correction
        :type: bool
    .. attribute:: auxiliary_data_flag
        :type: bool
    .. attribute:: schlumberger_proprietary
        :type: bool

.. class:: dlisio.core.component_block()

   Component Block (CB)

   Component Blocks are the basic structure of an Information Record. Each CB
   contains an individual piece of information.

   .. attribute:: type_nb

        Helps define how a :class:`dlisio.lis.InformationRecord` is formatted.
        E.g. as a series of individual pieces of information or a table of
        information.

        :type: int

   .. attribute:: reprc

        The type of :attr:`component`

        :type: int

   .. attribute:: size

       The size of :attr:`component`

       :type: int

   .. attribute:: category

       Category is undefined by LIS79

       :type: int

   .. attribute:: mnemonic

       The name of the Component Block

       :type: str

   .. attribute:: units

       The units of measurement for :attr:`component`

       :type: str

   .. attribute:: component

       The actual data of this Component Block


.. autoclass:: dlisio.lis.InformationRecord


Utilities
---------
.. autoclass:: dlisio.lis.HeaderTrailer

.. class:: dlisio.core.text_record

    Describes Miscellaneous records which contain one text field.

    .. attribute:: message

        Complete content of the record. Text might be fully human-readable,
        partly human-readable or be just a bytes sequence.
        To get more control over the returned value refer to
        :ref:`Strings and encodings`.

        :type: str or bytes

