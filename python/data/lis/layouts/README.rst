Physical File configurations/layouts
====================================

Test files for different configurations of physical layouts.
Note that the actual Logical Records contain dummy data and can't be parsed by
any parsing routine. 

================== ===========================================================
Filename           Description
================== ===========================================================
attributes_01.lis  Bit 16 (unreserved) is set [real files].
attributes_02.lis  Bit 16 set, File Number and Record Number present
attributes_03.lis  Bit 16 set, File Number, Record Number and mock Checksum
                   present
attributes_04.lis  Parity error bit set in File Trailer
attributes_05.lis  Checksum error bit set in File Trailer
attributes_06.lis  File Number and Record Number attributes set. PR length is 6.


layout_00.lis      RHLR, THLR, FHLR, FTLR, TTLR, RTLR
layout_01.lis      Size of some PRs is not divisible by 2


layout_tif_00.lis  Basic layout: TM(0), RHLR, TM(0), THLR, TM(1), TM(0), FHLR,
                   TM(0), FTLR, TM(1), TM(0), TTLR, TM(0), RTLR, TM(1), TM(1)
layout_tif_01.lis  Several Logical Files, Tapes and Reels. TM(0) before every
                   PR. Structure dismissing TM(0)s:
                   RHLR, THLR, TM(1), FHLR, FTLR, TM(1), FHLR, FTLR, TM(1),
                   TTLR, THLR, TM(1), FHLR, FTLR, TM(1), TTLR, RTLR, TM(1),
                   RHLR, THLR; TM(1), FHLR, FTLR, TM(1), TTLR, RTLR, TM(1),
                   TM(1)
layout_tif_02.lis  Basic layout, but no TM(1)s to separate Files:
                   TM(0), RHLR, TM(0), THLR, TM(0), FHLR, TM(0), FTLR, TM(0),
                   TTLR, TM(0), RTLR, TM(1), TM(1)
layout_tif_03.lis  Basic layout, but 3 TM(1) at EOF
layout_tif_04.lis  Basic layout, but no TM(1) at EOF
layout_tif_05.lis  Basic layout, but missing TTLR and RTLR
layout_tif_06.lis  Basic layout, but missing TTLR and RTLR and no TM(1) at EOF
layout_tif_07.lis  Basic layout, but missing TTLR and RTLR and 3 TM(1)s at EOF
layout_tif_08.lis  New reel follows after missing TTLR and RTLR. Omitting TM(0):
                   RHLR, THLR, TM(1), FHLR, FTLR, TM(1), RHLR, THLR, TM(1),
                   FHLR, FTLR, TM(1), TTLR, RTLR, TM(1), TM(1)
layout_tif_09.lis  Basic layout, but missing RTLR


padding_01.lis     Non-TIFed file with PRs of size not divisible by 4 and no
                   additional padding
padding_02.lis     TIFed file with PRs of size not divisible by 4 and no
                   additional padding
padding_03.lis     TIFed file with padding that assures minimal custom PR size
padding_04.lis     TIFed file with 00 padding that assures PR size is divisible
                   by 4
padding_05.lis     TIFed file with non-00 padding that assures PR size is
                   divisible by 4
padding_06.lis     TIFed file with 00es after last tapemark to assure file size
                   is divisible by custom number


successor_00.lis   File is correctly divided into several successive PRs
successor_01.lis   Successive PR expected, but new PR follows
successor_02.lis   Successive PR expected, but RHLR follows
successor_03.lis   Successive PR expected, but THLR follows
successor_04.lis   Successive PR expected, but FHLR follows


truncated_01.lis   File is truncated where successive PR is expected
truncated_02.lis   File is truncated in the middle of the data
truncated_03.lis   File is truncated after LR header
truncated_04.lis   File is truncated in LR header
truncated_05.lis   File is truncated after PR header
truncated_06.lis   File is truncated in PR header
truncated_07.lis   TIFed file is truncated where successive PR is expected
truncated_08.lis   TIFed file is truncated in the middle of the data
truncated_09.lis   TIFed file is truncated after LR header
truncated_10.lis   TIFed file is truncated in LR header
truncated_11.lis   TIFed file is truncated after PR header
truncated_12.lis   TIFed file is truncated in PR header
truncated_13.lis   TIFed file is truncated after TM
truncated_14.lis   TIFed file is truncated in TM
truncated_15.lis   File is truncated in second LF


wrong_01.lis       Not a LIS file
wrong_02.lis       Not a LIS TIFed file
wrong_03.lis       File zeroed from certain point
wrong_04.lis       TIF TM is wrong
wrong_05.lis       LR Type is wrong
================== ===========================================================
