Chapter 2 - Data Organization
=============================

Test files for testing the general layout of files, defined in Chapter 2 of
rp66v1. This includes, but not limited to segmentation between Logical- and
Visible Records, Storage Unit Labels, padbytes and garbage data.

=================================== ===========================================
File                                Description
=================================== ===========================================
2lr-in-vr.dlis                      2 logical records in 1 visible record

7K-file.dlis                        Testing that files between 4 and 8 kB are
                                    read correctly.

example-record.dlis                 A single visible record with one logical
                                    record segmented into 3 logical record
                                    segments

fdata-many-in-same-vr.dlis          A single visible record, with several
                                    Indirectly formatted logical records of type
                                    fdata

fdata-vr-aligned.dlis               One fdata aligned with visible record

incomplete-sul.dlis                 Incomplete storage unit label

incomplete-vr.dlis                  Incomplete visible record

lr-in-2vrs.dlis                     A logical record spanning 2 visible records

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

truncated.dlis                      Mismatch between visible record length and
                                    remaining bytes

wrong-lrhs.dlis                     Mismatch between logical record segment
                                    length and remaining bytes in visible
                                    record

=================================== ===========================================
