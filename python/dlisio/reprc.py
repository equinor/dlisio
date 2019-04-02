""" reprc -> formatstring

Conversion from dlis' representation codes to format-string char's.
"""
fmt = {
    "eof"  : '\0',
    1      : 'r',
    2      : 'f',
    3      : 'b',
    4      : 'B',
    5      : 'x',
    6      : 'V',
    7      : 'F',
    8      : 'z',
    9      : 'Z',
    10     : 'c',
    11     : 'C',
    12     : 'd',
    13     : 'D',
    14     : 'l',
    15     : 'u',
    16     : 'U',
    17     : 'L',
    18     : 'i',
    19     : 's',
    20     : 'S',
    21     : 'j',
    22     : 'J',
    23     : 'o',
    24     : 'O',
    25     : 'A',
    26     : 'q',
    27     : 'Q',
}

""" reprc -> type-string
Conversion from dlis' representation codes to type-strings that can be
interpreted by numpy.dtype. int's and uint's are normalized to 4-byte.

Note: dtype's for reprc with variable lenghts are not yet supported by dlisio
(reprc 19-20, 23-25, 27).
"""
dtype = {
    1      : 'f4',                   #Low precision floating point
    2      : 'f4',                   #IEEE single precision floating point
    3      : '2f4',                  #Validated single precision floating point
    4      : '3f4',                  #Two-way validated single precision floating point
    5      : 'f4',                   #IBM single precision floating point
    6      : 'f4',                   #VAX single precision floating point
    7      : 'f8',                   #IEEE double precision floating point
    8      : '2f8',                  #Validated double precision floating point
    9      : '3f8',                  #Two-way validated double precision floating point
    10     : 'c8',                   #Single precision complex
    11     : 'c16',                  #Double precision complex
    12     : 'i1',                   #Short signed integer
    13     : 'i2',                   #Normal signed integer
    14     : 'i4',                   #Long signed integer
    15     : 'u1',                   #Short unsigned integer
    16     : 'u2',                   #Normal unsigned integer
    17     : 'u4',                   #Long unsigned integer
    18     : 'u4',                   #Variable-length unsigned integer
    19     : 'i1,U',                 #Variable-length identifier
    20     : 'i4,U',                 #Variable-length ASCII character string
    21     : 'M',                    #Date and time
    22     : 'i4',                   #Origin reference
    23     : 'i4,i1,i1,U',           #Object name
    24     : 'i1,U,i4,i1,i1,U',      #Object reference
    25     : 'i1,U,i4,i1,i1,U,i1,U', #Attribute reference
    26     : 'i1',                   #Boolean status
    27     : 'i1,U',                 #Units expression
}
