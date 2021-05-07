Investigation hints
===================

This section might be helpful to dlisio developers or very advanced users who
want to find a cause of a specific dlisio failure.

.. note::  Unfortunately, dlisio has little debugging support. Thus failure
           investigation at the moment is not easy.

.. note::  You **might** be able to fix the file by making changes
           just in a couple of places.

.. contents:: :local:


Prerequisites
-------------

You:

 1. Are in extreme need of reading as much data as possible from That One File
    which dlisio fails to read, or need to investigate it
 2. Are very familiar with rp66 specification
 3. Have a good grasp on working with binary files
 4. Can build dlisio_ and lfp_ from source code and have enough knowledge to
    debug it


Overview
--------

When error happens on load, it usually means that file structure itself is
spoiled. So you should be able to find error just by checking VR and LR
headers.

When the file itself loads, it means that data layout is fine, which
*probably* means that *data* itself is fine and is written as intended. Errors
on accessing objects indicate that intention didn't match RP66 specification.

You can find more about various failures in :ref:`Errors Reference`.


Visual inspection
-----------------

Visually inspect the file to decide if failure cause is obvious.

Open the file in binary editor, scroll through it.

* Make sure that it looks like every other dlis file that opens correctly.
  Regardless of the extension, file contents might not be dlis.
* See if you notice zeroed-out bytes at the end of the file. This likely means
  there was an error during file creation and data is truncated.

Find failure offset
-------------------

.. note::  Remember that dlisio fails when it definitely can't process the
           data anymore. Which means that real error might have happened
           somewhere **before** the failure point indicates.

Error on load
^^^^^^^^^^^^^
If error happened during data load, you might see in the error message last
known absolute offset aka physical tell (decimal). Usually offset would point
to the position of LRS which dlisio was unable to process.

Error on parse
^^^^^^^^^^^^^^
If error happened during parsing, you'll likely find object set, object or
attribute identification in the error message. You may search the binary
file in UTF-8 mode to find these markers in the respective logical file,
thus establishing some resemblance of failure offset.

Failure offset hint not present
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In some cases this might not be enough and you'll have to dig into the code,
which won't be easy and straightforward.

Some first steps:

* Build dlisio_ and lfp_ in debug mode.
* Start Python debugging process.
* Find failing C++ call.
* Start gdb (or similar C++ debugger) and connect to Python process.
* While debugging further keep in mind that dlisio uses layered-file-protocol
  library. It means that all the offsets passed inside dlisio are not absolute
  (TIF or rp66 header bytes are not included), so you'll have to dig into lfp_
  library to find out what really happens.
* You might need to modify the code to give yourself more anchor points if
  failure, for example, happens late in the long loop.


Figure out failure reason
-------------------------

Results of your investigation might be something that makes sense - certain
specification violation, missing bytes or some specific but consistent between
several files error.

Sometimes, however, it won't be possible to figure out what exactly went wrong.
Then failure can't be classified and there is little that can be fixed.


Check VR boundaries
^^^^^^^^^^^^^^^^^^^

Search for the first bytes ``FF 01`` before and after offset. Check that
record length matches distance between the tells (if file is tiffed, be
aware of tif header bytes which will affect the distance).
In most cases VR header will be ``20 00 FF 01``. If it is not, look
closer. What you see might still be a valid record header. Or it can be random
bytes which happened to be ``FF 01``.


Check LRS
^^^^^^^^^

Find LRS to which failing tell belongs by manually counting logical record
segments from the start of the VR. Pay attention to the header (attributes and
code). If attributes or code seem to be random, something is likely spoiled
already. EFLR expected codes are [``0x00 - 0x0B``], IFLR ones are ``0x00`` and
``0x01``. Attribute byte pattern often is ``xxx00000``, but can differ.

Make sure that all the attributes make sense and create consistent record.
Check the padbytes length: it might be too big and "eat" part of the data.

Check attributes in template/object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For EFLRs find the object that fails and manually check object attributes
based on object set template. You might find that some objects are missing data
or that there are major specification violations.

Check fdata
^^^^^^^^^^^

For IFLRs find failing frame. Make sure that you see frame name near the
start of the record. It might be difficult to check the format
string and all the data, but you can compare failing frame record length with
previous frame record length. More often than not they should be the same. You
might also check the frame numbers, they are usually sequential.

Fixes
-----
In certain cases you might be able to fix the issue yourself.

Remember that there is no guarantee that your fix will lead to the correct file:

* fix itself might be wrong
* there might already be too much data missing
* fix might create screwed image of the file
* there might be more errors further down the file

Investigation examples
----------------------

Examples of files which could be read by dlisio after changing just one byte:

* Very last fdata record had spoiled padbytes length ``0x75``. In all the
  previous frames padbytes length was ``0x01``, which indicated it should be
  the same in the last one. Changing ``0x75`` to ``0x01`` fixed the issue.
* File-Header set type was set to ``0xF8`` (named set), while in reality it was
  unnamed as it should be. Changing ``0xF8`` to ``0xF0`` fixed the issue.
* Type attribute in Equipment set was declared to be invariant (value ``0x5D``)
  in template.
  Then instead of skipping this attribute in objects value ``0x20`` (use
  default) was used. Changing ``0x5D`` to ``0x3D`` in template fixed the issue.

.. _`dlisio`: https://github.com/equinor/dlisio
.. _`lfp`: https://github.com/equinor/layered-file-protocols
.. _`VR`: Visible Record /Visible Envelope ??
.. _`LR`: Logical Record
