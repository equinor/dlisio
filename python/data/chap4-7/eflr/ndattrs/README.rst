Chapter 4, 5, 6, 7 - Semantics - Dimensional attributes tests
=============================================================

Testfiles for dimensional attributes tests.

============================ =================================================
File / directory             Description     
============================ =================================================
object.dlis.part             Object with identification 'I.OBJECT-O.10-C.0'
/set                         Set components. Should contain LR header
/template                    Labels
/objattr                     Various attribute values
============================ =================================================

*objattr* folder contains values.

======================================= =======================================
Files in /objattr                       Description
======================================= =======================================
0.5-1.5-2.5-3.5.dlis.part               4 FSINGL values: 0.5, 1.5, 2.5, 3.5

0.5-1.5-2.5.dlis.part                   3 FSINGL values: 0.5, 1.5, 2.5

0.5-1.5.dlis.part                       2 FSINGL values: 0.5, 1.5

0.5.dlis.part                           1 FSINGL value:  0.5

1-2-3-4-5-6-7-8-9-10-11-12.dlis.part    12 USHORT values: 1, 2, 3, 4, 5, 6, 7,
                                        8, 9, 10, 11, 12

1-2-3-4-5.dlis.part                     5 USHORT values: 1, 2, 3, 4, 5

1-2-3-4.dlis.part                       4 USHORT values: 1, 2, 3, 4

1-2-3.dlis.part                         3 USHORT values: 1, 2, 3

1-2.dlis.part                           2 USHORT values: 1, 2

1.dlis.part                             1 USHORT value:  1

2-3.dlis.part                           2 USHORT values: 2, 3

2.dlis.part                             1 USHORT value: 2

4.dlis.part                             1 USHORT value: 4

2001-Jan-1,2002-Feb-2.dlis.part         2 DTIME values: 1 Jan 2001, 2 Feb 2002

2001-Jan-1.dlis.part                    1 DTIME value:  1 Jan 2001

complex-(0.5-1.5),(2.5-3.5).dlis.part   2 CSINGL values: (0.5, 1.5), (2.5, 3.5)

complex-(0.5-1.5).dlis.part             1 CSINGL value:  (0.5, 1.5)

empty-INT.dlis.part                     0 USHORT values

empty-OBNAME.dlis.part                  0 OBNAME values

False-True.dlis.part                    2 STATUS values: False, True

False.dlis.part                         1 STATUS value:  False

string-val1,val2.dlis.part              2 ASCII values: val1, val2

string-val1.dlis.part                   1 ASCII value:  val1

validated-(0.5-1.5),(2.5-3.5).dlis.part 2 FSING1 values: (0.5, 1.5), (2.5, 3.5)

validated-(0.5-1.5).dlis.part           1 FSING1 value:  (0.5, 1.5)

zones-2.dlis.part                       2 OBNAME values. For convenience,
                                        object names start with ZONE

zones-4.dlis.part                       4 OBNAME values. For convenience,
                                        object names start with ZONE

zones-5.dlis.part                       5 OBNAME values. For convenience,
                                        object names start with ZONE
======================================= =======================================


Creating a valid .dlis-file
---------------------------

envelope.dlis.part from the parent directory should be used as the first
.part-file when creating a valid file. Logical Record can then be constructed
by adding parts in any order you please, as long as they respect the
definitions form Chapter 3 of rp66v1.
