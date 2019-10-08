Chapter 3 - Logical Record Syntax
=================================

Testfiles for the general layout of (Explicitly) Formatted Logical Records,
defined in Chapter 3 of rp66v1.

============================ =================================================
File / directory             Description     
============================ =================================================
sul.dlis.part                Default Storage Unit Label
start.dlis.part              SUL + all the VR and LRSH bytesiBytes 50 and 51
                             contain VR length. Bytes 54 and 55 contain LRSH
                             length. These bytes will be overwritten by the
                             test suite to match the size of the final file.
/set                         Set components
/template                    Object template
/object                      Objects descriptor + object name
/objattr                     Object attributes
/implicit                    Indirectly formatted logical records
/reprcode                    Object attribute of various representation codes
============================ =================================================

Creating a valid .dlis-file
---------------------------

sul.dlis.part or start.dlis.part should be used as the first .part-file when
creating a valid file. Logical Records can then be constructed by adding
components in any order you please, as long as they respect the definitions
form Chapter 3 of rp66v1.
