Frames and Channels
===================

Specific tests for channels and frames

================================= ==============================================
Filename                          Description
================================= ==============================================
1-channel-2-frames.dlis           Same channel belongs to two different frames

2-channels-same-content-diff-sign Two channels have same content, but different
                                  copynumber. They belong to different frames.

2-channels-same-sign-diff-content Two channels have same signature, but
                                  different content. Channel with that name
                                  belongs to a frame.

2-channels-same-sign-same-content Two channels have same signature and same
                                  content. Channel with that name belongs to a
                                  frame.

channel-missing.dlis              Frame refers to missing channel.

duplicated.dlis                   A frame containing two channels with the same
                                  signatures (mnemonic, origin and copynumber)

indexed-no-channels.dlis          Frame is indexed, but there are no channels

mainframe.dlis                    Indexed frame with channels TIME.0.0,
                                  TDEP.0.0, TIME.1.0

no-dimension.dlis                 Channel which doesn't have dimension attribute

nonindexed.dlis                   Non-indexed frame with channels

various.dlis                      Frame contains channels with various
                                  representation codes

================================= ==============================================

