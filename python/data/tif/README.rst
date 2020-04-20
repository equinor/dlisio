TIF envelope
============

Test-files designed for testing TIF encapsulation

Templates
---------

Files have different structure and point of this folder to provide files of all
seen types.

======================= ======================================================
Filename                Description
======================= ======================================================
1.dlis                  1 TM before SUL, 1 TM before LF, 1 TM before every VR,
                        2 TMs in the end

2.dlis                  1 TM before SUL, 1 TM before LF, 1 TM before every VR,
                        3 TMs in the end

3.dlis                  1 TM before SUL, 1 TM before LF, 1 TM before every VR,
                        4 TMs in the end

4.dlis                  2 TMs before SUL, 1 TM before LF, 1 TM before every VR,
                        2 TMs in the end

5.dlis                  1 TMs before SUL, 1 TM before LF, 1 TM before every VR,
                        3 TMs in the end

6.dlis                  1 TM before SUL, 0 TMs before LF, 1 TM before every VR,
                        2 TMs in the end

7.dlis                  1 TM before SUL, 0 TMs before LF, 1 TM before every VR,
                        0 TMs in the end

8.dlis                  no SUL, 0 TMs before LF, 1 TM before every VR, 2 TMs in
                        the end

9.dlis                  no SUL, 1 TM before LF, 1 TM before every VR, 2 TMs in
                        the end

inconsistency.dlis      1 TM before SUL, 0 TMs before first LF, 1 TM before
                        second LF, 1 TM befre every VR, 2 TMs in the end

======================= ======================================================

Irregular
---------

Some files seen to be of structure not strictly defined by TIF.


======================= ======================================================
Filename                Description
======================= ======================================================
misalignment.dlis       1 TM before SUL, 0 TMs before LF, 1 TM before every VR,
                        2 TMs in the end, then padding with zeroes. Length of
                        some VRs is not divisible by 4 and 2 additional bytes
                        are required before next TM.

padding.dlis            1 TM before SUL, 0 TMs before LF, 1 TM before every VR,
                        2 TMs in the end, then padding with zeroes

suls.dlis               1 TM before SUL, 0 TMs before LF, 1 TM before every VR,
                        SUL before every LF, 2 TMs in the end

======================= ======================================================

Layout
------

TM can happen in different position according to EFLR and IFLR. Files represent
various situations like that.

======================= ======================================================
Filename                Description
======================= ======================================================
fdata-aligned.dlis      FDATA is present, but VR happens before it.

fdata-disaligned.dlis   FDATA is present, new VR happens in the middle of record

FF01.dlis               TM contains FF01 bytes. Note that it spoils even length
                        requirement of the VR

LR-aligned.dlis         LR is aligned with VR borders.

LR-disaligned.dlis      LR is not aligned with VR borders.

======================= ======================================================
