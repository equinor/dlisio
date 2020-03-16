Chapter 4, 5, 6, 7 - Semantics
==============================

Test-files designed for testing dlis concepts defined in chapter 4-7 in rp66v1.

EFLR - Explicitly Formatted Logical Records
-------------------------------------------

Test files for explicit data types. Except for some few exceptions, see table
below, these files contain one full Logical Record with one or more objects.
Each object contains all possible attributes defined by rp66v1 in Chapter 5 &
6. Every Logical Record has one and only one Logical Record Segment::

    Logical record segment header 
    Set   
    Template
    Object 1
    Object 2
    ...     
    Object n

Bytes 0x00 and 0x01 correspond to the LRS length. These bytes are supposed to
be overwritten by test framework.  Byte 0x02 contains attributes. Expected
value for this byte is 80 for EFLR and 00 for IFLR. User is not expected to
assure padbytes, this is being done by the framework. Note 1: if provided value
is odd (for example 81 or 01), current version of code won't do anything -
assuring correct padbytes would be on user.  Note 2: current dlis code doesn't
enforce bytes parity.

======================= ======================================================
Filename                Description
======================= ======================================================
envelope                Contains SUL and for 4 of VR (Virtual Record). Bytes
                        0x50 and 0x51 correspond to VR length. These bytes will
                        be overwritten by the test suite to match the size of
                        the final file.

file-header2            Second File-header for testing multiple logical files

origin2                 Second origin file

\***-inc                Files for testing multiple logical files

axis-encrypted          Encrypted records

channel-same-objects    Channel duplication

coefficient-wrong       Coefficient objects that do not conform to the rp66v1
                        specification

fdata***                contains IFLR(s) of type FDATA, referencing Frame
                        objects defined in the frame**.dlis.part files

======================= ======================================================


Creating a valid .dlis-file
...........................

All created files should start with the envelop.dlis.part. After that, add
files in whatever order you need for your test case. Remember:

1) A physical file (.dlis) is segmented into Logical Files whenever a
Fileheader object is encountered. I.e. every time you insert a fileheader file
you create a new logical file.

2) frames must precede any fdata that references that frame

IFLR - Implicitly Formatted Logical Records
-------------------------------------------

Test files for implicit data types, like FDATA

================================================ ==================================================
Filename                                         Description
================================================ ==================================================
all-reprcodes.dlis                               1 Frame containing 27 Channels, each with a
                                                 different representation code
                                                 
big-ascii.dlis                                   Ascii with around 2000 characters

broken-ascii.dlis                                Ascii with incorrect specified length. Around 240
                                                 characters are expected, but only 20 are actually
                                                 present

broken-utf8-ascii.dlis                           Ascii containing non-utf8 characters

duplicate-framenos.dlis                          2 FDATA containing different values, but they have
                                                 the same frame number

duplicate-framenos-same-frames.dlis              2 FDATA containing the same value and having the
                                                 same frame number
                                                 
missing-framenos.dlis                            Only has frame number 2 and 4, frame number 1 and
                                                 3 are missing
                                                 
multidimensions-ints-various.dlis                Integers with different dimensions configuration

multidimensions-multifdata.dlis                  Dimensional data present inside FDATA

multidimensions-validated.dlis                   Validated value inside of dimensional data

out-of-order-framenos-one-frame.dlis             2 frames in 1 FDATA with decreasing frame numbers

out-of-order-framenos-two-frames.dlis            2 frames in 2 FDATA with decreasing frame numbers

out-of-order-framenos-two-frames-multifdata.dlis Frame numbers would be in correct order if FDATA
                                                 order is switched.

two-various-fdata-in-one-iflr.dlis               2 frames in one FDATA, with multiple channels

================================================ ==================================================

/reprcodes
----------

Test-files for parsing IFLR's of type FDATA. Only the representation code in
Channel and the fdata is different. All files in this directory follow this
structure::

    Sul
    Fileheader('N')
    Channel(CH**)
    Frame(FRAME-REPRCODE)
    fdata(FRAME-REPRCODE)

The filname corresponds to the type stored in the fdata. Byte 151 contains
first frame number 01, followed by the value.

/reprcodes-x2
-------------

All files follow the same structure as in /reprcodes, but there are multiple
(2) frames in each FDATA. Byte 151 contains first frame number 01, followed by
value, then frame number 02, then value.

Remaining files
---------------

================================================ ==================================================
Filename                                         Description
================================================ ==================================================
many-logical-files.dlis                          Contains several logical files, one without file
                                                 header

many-logical-files-same-object.dlis              Contains 2 logical files with the same objects and
                                                 encrypted records

================================================ ==================================================
