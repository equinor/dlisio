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

*implicit* folder contains full files.

====================================== ========================================
Files in /implicit                     Description
====================================== ========================================
fdata-broken-obname.dlis               Obname length in first implicit record is
                                       bigger than remaining record length.
                                       Second implicit record is correct

fdata-encrypted.dlis                   Fdata record is encrypted

fdata-many-in-same-vr.dlis             Several fdata segments in same vr,
                                       including fdata with obname of min and
                                       max length

fdtata-non-0-type.dlis                 Contains implicit record of non-0 type

fdata-vr-aligned-padding.dlis          Simple fdata aligned with Visible Record
                                       border but with present padbytes

fdata-vr-aligned.dlis                  Simple fdata aligned with Visible Record
                                       border

fdata-vr-disaligned-checksum.dlis      Fdata is interrupted by Visible Record
                                       right after obname and lrs has checksum

fdata-vr-disaligned-in-obname.dlis     Fdata obname is interrupted by Visible
                                       Record border

fdata-vr-disaligned.dlis               Fdata which is interrupted by Visible
                                       Record in the middle of data

fdata-vr-obname-trailing.dlis          Fdata obname is interrupted by Visible
                                       Record border with just 1 byte to go and
                                       lrs has trailing length of 2 bytes
====================================== ========================================


Creating a valid .dlis-file
---------------------------

sul.dlis.part or start.dlis.part should be used as the first .part-file when
creating a valid file. Logical Records can then be constructed by adding
components in any order you please, as long as they respect the definitions
form Chapter 3 of rp66v1.
