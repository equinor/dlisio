LIS Logical Records - Curves
============================

Parts for various curves tests: DFSR PRs

=============================== ================================================
Filename        Desciption
=============================== ================================================
dfsr-depth-dir-down.lis.part    Depth default file. Depth recoding mode (13): 1.
                                Direction (4): DOWN. Frame Spacing (8): 1.
                                Units for frame spacing (9): .1IN. Units of
                                Depth (14) : .1IN. Depth reprc (15): int32.
dfsr-depth-dir-invalid.lis.part Same as default, but Direction (4): invalid,
dfsr-depth-dir-no.lis.part      Same as default, but Direction (4) not present.
dfsr-depth-dir-none.lis.part    Same as default, but Direction (4): NONE.
dfsr-depth-dir-up.lis.part      Same as default, but Direction (4): UP.
dfsr-depth-reprc-bad.lis.part   Same as default, but Depth reprc (15) is invalid
dfsr-depth-reprc-none.lis.part  Same as default, but Depth reprc (15) is missing
dfsr-depth-reprc-size.lis.part  Same as default, but Depth reprc (15) is stored
                                as 32-bit int.
dfsr-depth-spacing-no.lis.part  Same as default, but Frame Spacing (8) not
                                present.
dfsr-dimensional-bad.lis.part   CH01 has 2 size of 5, when size(repc) is 2.
dfsr-dimensional-int.lis.part   CH01 has 2 int entries per sample, CH02 has 1.
dfsr-entries-default.lis.part   No entries but terminator defined.
dfsr-entries-defined.lis.part   All entries have a value.
dfsr-fast-bad.lis.part          CH01 has 2 int samples, when size is 5,
                                size(repc) is 1.
dfsr-fast-depth.lis.part        Depth default file. CH01 has 2 byte samples.
                                CH02 has 1 int32 sample
dfsr-fast-dimensional.lis.part  CHO1 has 2 byte samples with size 6. CH02 has
                                1 int32 sample.
dfsr-fast-int.lis.part          CH01 has 2 int samples, CH02 has 1 int sample.
dfsr-fast-str.lis.part          CH01 has 2 str samples, CH02 has 1 str sample.
dfsr-fast-two.lis.part          CH01 has 2 int samples, CH02 has 3 int samples.
                                CHO3 has 1 int sample.
dfsr-repcodes-fixed.lis.part    Channels of 8 fixed-sized repcodes: 1 byte,
                                3 ints and 4 floats.
dfsr-repcodes-invalid.lis.part  Channel has unknown repcode.
dfsr-repcodes-mask.lis.part     Channel of mask type.
dfsr-repcodes-string.lis.part   Channel of string type.
dfsr-subtype0.lis.part          Record subtype: 0. All values defined.
dfsr-subtype1.lis.part          Record subtype: 1. All values defined.
dfsr-suppressed.lis.part        Reserved size: CH1 4, CH2 -4, CH3 1, CH4 -1
=============================== ================================================

Parts for various curves tests: Fdata PRs corresponding to respective DFSRs

=============================== ================================================
Filename        Desciption
=============================== ================================================
fdata-depth-down-PR1.lis.part   Depth: 1, Data: 16; 17
fdata-depth-down-PR2.lis.part   Depth: 3, Data: 18; 19
fdata-depth-down-PR3.lis.part   Depth: 5, Data: 20;
fdata-depth-up-RP1.lis.part     Depth: 53, Data: 37; 36
fdata-depth-up-RP2.lis.part     Depth: 51, Data: 35; 34
fdata-depth-up-RP3.lis.part     Depth: 49, Data: 33;
fdata-dimensional-int.lis.part  Data: [1, 2], 3; [4, 5], 6
fdata-fast-depth.lis.part       Depth: 1, Data (2, 3)s, 4; (5, 6)s, 7
fdata-fast-dimensional.lis.part Data: ([1, 2, 3], [4, 5, 6])s, 7;
                                ([8, 9, 10], [11, 12, 13])s, 14;
fdata-fast-int.lis.part         Data: (1, 2)s, 3; (4, 5)s, 6
fdata-fast-str.lis.part         Data: ("STR sample 1    ", "STR sample 2    ")s,
                                "STR not sampled "
fdata-fast-two.lis.part         Data: (1, 2)s, (3, 4, 5)s, 6;
                                (7, 8)s, (9, 10, 11)s, 12
fdata-repcodes-fixed.lis.part   One frame of data with fixed-size values
fdata-repcodes-mask.lis.part    One frame of data with mask value
fdata-repcodes-string.lis.part  One frame of data with string value
fdata-suppressed.lis.part       Data: 1 (4B), 2 (4B), 3(1B), 4(1B)
=============================== ================================================

