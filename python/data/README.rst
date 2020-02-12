Welcome to the test-file directory of dlisio 
============================================

This directory contains all test-files used by dlisio's Python test suite.  

Our test-files are mostly synthetic. We create our own files with the minimal
necessary information needed to test specific cases.  Files are grouped into
subdirectories based on what chapters in the dlis standard [1]_ they aim to
test.

Each subdirectory has its own README with more detailed information.

====================================== ========================================
Files in /data                         Description
====================================== ========================================
206_05a-_3_DWL_DWL_WIRE_258276498.DLIS An actual produced file

====================================== ========================================

.dlis.part
----------

Due to all the quirks of dlis-files, testing them is quite involved. Too make
the testing a bit more effective, we introduce the concept of .dlis.part-files:

    A .dlis.part file is essentially just one small part of a dlis-file - the
    part we want to test.

By itself, a .dlis.part-file cannot be loaded by dlisio. However they are
designed in such a way that they can easily be concatenated with other
.dlis.part files to form a valid file, directly in your unit-test. The file
conftest.py defines a number of fixtures that makes this concatenation process
easy.

The README in directory's containing .dlis-part-files contains guides on how
these files can be concatenated into a valid file, without you having to
manually inspect the binary.

Note that excessive use of on-the-fly file concatenation has a negative effect
on the run-time of the test-suite.


Contributing
------------

Feel free to add new test-files if needed. To avoid an excessive amount of
test-files, please investigate if you can use the existing files for your test
before you add new files. When adding a new file, please consider:

- To avoid excessive amounts of test-files, check if the existing files
  contain what you need before you add something new
- Many things can be tested without physical files. E.g. any object (Frame,
  Channel etc..) can be created directly in Python, without a file-backing
- New file(s) should only contain the minimal possible information needed in order
  to test whatever needs testing
- If new file(s) are added, update the relevant README.rst with a short
  description

.. [1] API RP66 v1, http://w3.energistics.org/RP66/V1/Toc/main.html
