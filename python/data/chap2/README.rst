Chapter 2 - Data Organization
=============================

Test files for testing the general layout of files, defined in Chapter 2 of
rp66v1. This includes, but not limited to segmentation between Logical- and
Visible Records, Storage Unit Labels, padbytes and garbage data.

=================================== ===========================================
File                                Description
=================================== ===========================================
1lr-in-2vrs.dlis                    A logical record spanning 2 visible records

2lr-in-vr.dlis                      2 logical records in 1 visible record

3lrs-in-vr.dlis                     A single visible record with one logical
                                    record segmented into 3 logical record
                                    segments

3lr-in-vr-one-encrypted.dlis        Single VR with with 3 logical records, one
                                    encrypted

7K-file.dlis                        Testing that files between 4 and 8 kB are
                                    read correctly.

incomplete-sul.dlis                 Incomplete storage unit label

incomplete-vr.dlis                  Incomplete visible record

nondlis.txt                         Not a dlis file

old-vr.dlis                         Older visible record, see 2.3.6.2 Format
                                    Version of rp66v1

padbytes-bad.dlis                   Mismatch between padbyte length and logical
                                    record length

padbytes-encrypted.dlis             Explicitly formatted logical record with
                                    encrypted padbytes

padbytes-large-as-record.dlis       padbytes length == logical record length

padbytes-large-as-segment-body.dlis padbytes length == logical record segment
                                    length

pre-sul-garbage.dlis                Garbage before the storage unit label

pre-sul-pre-vrl-garbage.dlis        Garbage before storage unit label and
                                    visible record

small.dlis                          Test file smaller than 4kB

too-small-record.dlis               Visible record is smaller than the minimum
                                    requirement (20Bytes)

truncated-in-lrsh.dlis              File is truncated in the LRSH

truncated-on-full-lr.dlis           File is truncated on a complete LR, but not
                                    VR

truncated-in-second-lr.dlis         Mismatch between visible record length and
                                    remaining bytes. Second LR truncated

truncated-on-lrs.dlis               LRS expects successor, but none comes. File
                                    is truncated

wrong-lrhs.dlis                     Mismatch between logical record segment
                                    length and remaining bytes in visible
                                    record

=================================== ===========================================
