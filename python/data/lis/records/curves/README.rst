LIS Logical Records - Curves
============================

Parts for various curves tests: DFSR PRs

=============================== ================================================
Filename                        Description
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
dfsr-entries-bad-reprc.lis.part Entry reprc is 0x53.
dfsr-entries-bad-type.lis.part  Entry type is 0x41.
dfsr-entries-default.lis.part   No entries but terminator defined.
dfsr-entries-defined.lis.part   All entries have a value.
dfsr-fast-depth.lis.part        Depth default file. CH01 has 2 byte samples.
                                CH02 has 1 int32 sample
dfsr-fast-dimensional.lis.part  CHO1 has 1 int32 sample, CH02 has 2 byte samples
                                with size 6, CH03 has 1 int32 sample.
dfsr-fast-first.lis.part        CH01 has 2 int samples, CH02 has 1 int sample,
                                CH03 has 1 int sample.
dfsr-fast-index.lis.part        Depth recoding mode (13): 0. Direction (4):
                                DOWN. CH01 has 1 int sample, CH02 has 2 int
                                samples, CH03 has 1 int sample.
dfsr-fast-int-bad.lis.part      CH01 has 1 int sample, CH02 has 3 int samples,
                                when size is 4, size(repc) is 1, CH03 has 1 int
                                sample
dfsr-fast-int.lis.part          CH01 has 1 int sample, CH02 has 2 int samples,
                                CH03 has 1 int sample.
dfsr-fast-str.lis.part          CH01 has 1 int sample, CH02 has 2 str samples,
                                CH03 has 1 str sample.
dfsr-fast-two.lis.part          CH01 has 1 int sample, CH02 has 2 int samples,
                                CH03 has 3 int samples, CHO4 has 1 int sample.
dfsr-mnemonics-same.lis.part    Contains channels: NAME, NAME, TEST, NAME
dfsr-repcodes-fixed.lis.part    Channels of 8 fixed-sized repcodes: 1 byte,
                                3 ints and 4 floats.
dfsr-repcodes-invalid.lis.part  Channel has unknown repcode.
dfsr-repcodes-mask.lis.part     Channel of mask type.
dfsr-repcodes-string.lis.part   Channel of string type.
dfsr-samples-0.lis.part         One channel with samples=0.
dfsr-simple.lis.part            3 channels with samples=1, size=4, repc=int32.
dfsr-size-0-one-block.lis.part  One channel with size=0.
dfsr-size-0-string.lis.part     First channel is int with size 4, second is
                                string with size=0.
dfsr-size-0-two-blocks.lis.part First channel with size=0, second with size 4.
dfsr-size-lt-repcode.lis.part   Total size is 2, repcode size is 4.
dfsr-subtype0.lis.part          Record subtype: 0. All values defined.
dfsr-subtype1.lis.part          Record subtype: 1. All values defined.
dfsr-suppressed.lis.part        Reserved size: CH01 4, CH02 -4, CH03 1, CH04 -1.
dfsr-suppressed-bad.lis.part    Reserved size: CH01 4, CH02 -4, CH03 1, CH04 -1.
                                CH04 has mismatching repcode of size 2.
=============================== ================================================

Parts for various curves tests: Fdata PRs corresponding to respective DFSRs

=============================== ================================================
Filename                        Description
=============================== ================================================
fdata-bad-fdata.lis.part        Bytes: [0, 0, 0, 1, 0, 0, 0, 2, 0, 0]
fdata-depth-down-PR1.lis.part   Depth: 1, Data: 16; 17
fdata-depth-down-PR2.lis.part   Depth: 3, Data: 18; 19
fdata-depth-down-PR3.lis.part   Depth: 5, Data: 20;
fdata-depth-up-RP1.lis.part     Depth: 53, Data: 37; 36
fdata-depth-up-RP2.lis.part     Depth: 51, Data: 35; 34
fdata-depth-up-RP3.lis.part     Depth: 49, Data: 33;
fdata-dimensional-int.lis.part  Data: [1, 2], 3; [4, 5], 6
fdata-fast-depth.lis.part       Depth: 1, Data (2, 3)s, 4; (5, 6)s, 7
fdata-fast-dimensional.lis.part Data: 1, ([2, 3, 4], [5, 6, 7])s, 8;
                                9, ([10, 11, 12], [13, 14, 15])s, 16;
fdata-fast-index1.lis.part      Data: 1, (2, 3)s, 4;
fdata-fast-index2.lis.part      Data: 5, (6, 7)s, 8;
fdata-fast-index3.lis.part      Data: 9, (10, 11)s, 12;
fdata-fast-index4.lis.part      Data: 13, (14, 15)s, 16;
fdata-fast-int.lis.part         Data: 1, (2, 3)s, 4; 5, (6, 7)s, 8
fdata-fast-str.lis.part         Data: 1,
                                      ("STR sample 1    ", "STR sample 2    ")s,
                                      "STR not sampled "
fdata-fast-two.lis.part         Data: 1, (2, 3)s, (4, 5, 6)s, 7;
                                8, (9, 10)s, (11, 12, 13)s, 14;
fdata-repcodes-fixed.lis.part   One frame of data with fixed-size values
fdata-repcodes-mask.lis.part    One frame of data with mask value
fdata-repcodes-string.lis.part  One frame of data with string value
fdata-simple.lis.part           Data: 1, 2, 3
fdata-size.lis.part             Data: 1 (4B), 2 (4B)
fdata-suppressed.lis.part       Data: 1 (4B), 2 (4B), 3(1B), 4(1B)
=============================== ================================================

