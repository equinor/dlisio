LIS Logical Records
===================

Test files for different Logical Record types.

=============== ==============================================================
Filename        Description
=============== ==============================================================
inforec_01.lis  Structured record. Table is dense - I.e. all table entries are
                recorded.
inforec_02.lis  Structured record. Table is sparse - I.e. several table entries
                are not recorded in record.
inforec_03.lis  Unstructure record. I.e. not organised as a table. All CB's have 
                type_nb==0
inforec_04.lis  Unstructure record. I.e. not organised as a table. Not all CB's
                have type_nb==0
inforec_05.lis  Illformed record. First CB have type_nb==73, second CB does
                _not_ have type_nb==0
inforec_06.lis  Empty record - Contains 0 CBs
inforec_07.lis  Empty Table - Contains only 1 CB (type_nb==73)
=============== ==============================================================

LIS parts (if file is not listed, it means there is nothing peculiar about it).

=============================== ================================================
Filename                        Description
=============================== ================================================
FHLR-too-long.lis.part          File Header has 2 more bytes than expected.
FHLR-too-short.lis.part         File Header has too few bytes.
FTLR-broken-structure.lis.part  Data is present where spaces are supposed to be
inforec-cut-in-fixed.lis.part   Component block is cut after mnemonic
inforec-cut-in-value.lis.part   Component blick is cur in component value
inforec-encoded.lis.part        Mnemonic, units and value are encoded in koi8-r
TTLR-encoded.lis.part           Name and some other values are encoded in koi8-r
TTLR-too-long.lis.part          Tape Trailer has more bytes than fixed size.
TTLR-too-short.lis.part         Tape Trailer is 2 bytes short of expected size.
=============================== ================================================
