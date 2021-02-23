LIS API Reference
=================

.. currentmodule:: dlisio.lis

Load a LIS-file
---------------
.. autofunction:: dlisio.lis.load

LIS Physical File
-----------------
.. autoclass:: dlisio.lis.physical_file()

LIS Logical File
-----------------
.. autoclass:: dlisio.lis.logical_file()

LIS Curves
----------
.. autofunction:: dlisio.lis.curves()

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

Utilities
---------
.. autoclass:: dlisio.lis.HeaderTrailer
