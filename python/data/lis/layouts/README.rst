Physical File configurations/layouts
====================================

Test files for different configurations of physical layouts.
Note that the actual Logical Records contain dummy data and can't be parsed by
any parsing routine. 

================== ===========================================================
Filename           Desciption
================== ===========================================================
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




================== ===========================================================
