LIS Logical Records
===================

Test files for different Logical Record types

=============== ==============================================================
Filename        Desciption
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

