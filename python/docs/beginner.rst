Overview questions
==================

Purpose of this section is to provide people who just stumbled upon dlisio with
short overview.

.. contents:: :local:

General
-------

Is dlisio something I might be interested in?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
It might be useful for you if:

1. you have some **.dlis** files you want to know contents of
2. it is acceptable for you to use programming language to do so
3. this programming language is `Python`_

What do I need to know to work with dlisio?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* You need to have some knowledge in geophysics field to be able to interpret
  contents of the file
* You need to be fairly familiar with `Python`_ programming language to be able
  to run queries to the file

What dlisio can not do?
^^^^^^^^^^^^^^^^^^^^^^^
* dlisio can not write .dlis files *(unlikely to be supported)*
* dlisio can not read/write .lis files *(.lis read coming soon)*
* dlisio can not read/write .las files


Limitations
-----------

Is Python the only way to use dlisio?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Yes. At the moment there are no plans to make it accessible in other languages.

Can I be sure that dlisio presents me the data correctly?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
dlisio strives to present you with full and correct overview of the file.
Overall, you should be confident in the data you receive.
If dlisio has any remarks about what is presented to you, or if it makes any
assumptions, you will be informed about it through errors, warnings and info
messages.

However, dlisio still might fail to give you 100% correct overview of the data.
Reasons for this are:

* Specification is sometimes ambiguous and could be understood differently by
  all the parties involved.
* Files do not always conform to specification. If dlisio takes wrong guess
  about original intentions, it may present you with spoiled data.
* At the moment dlisio does not cover 100% of the specification. Parts of these
  not covered features have major impact on the data correctness (Update
  objects, Replacement sets).
* dlisio silently drops some information, like, for example, encrypted records.
  You might never know it was even present in the original file.
* Bugs :(

Can I read broken files with dlisio?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Somewhat. dlisio will bypass all the errors it can if requested by user.

More information can be found under :class:`dlisio.errors.ErrorHandler`.


Technical
---------

What software do I need to use dlisio?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* `Python`_: supported versions are **3.5.x**, **3.6.x**, **3.7.x**, **3.8.x**
* `pip`_: you need it only to install dlisio, it should come along with
  installed Python

How do I install dlisio?
^^^^^^^^^^^^^^^^^^^^^^^^
Installation process should be fairly simple as dlisio is distributed through
PyPi.

In command line run::

    pip install dlisio

(command might have to be different if your Python installation was not a
standard one).

On successful installation you should receive a similar message::

    Successfully installed dlisio-<latest-release>

Now you should be able to import dlisio from Python interpreter without any
errors::

    >>> import dlisio


Community
---------

Can I report a bug?
^^^^^^^^^^^^^^^^^^^
Yes, please do so under `dlisio issues`_.

May I suggest a feature?
^^^^^^^^^^^^^^^^^^^^^^^^
Yes, you may suggest a feature under `dlisio issues`_. However due to limited
resources available to the project, it might not get implemented.

We also welcome issues based on the untouched parts of the specification.

If you happen to find a file with important features not implemented by dlisio
(Update objects, Replacement Sets, etc) or any hidden data you are interested
in, we would appreciate information about it.

Where do I ask for help?
^^^^^^^^^^^^^^^^^^^^^^^^
`dlisio issues`_ would be the best place to go.


.. _`Python`: https://www.python.org/
.. _`pip`: https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line
.. _`dlisio issues`: https://github.com/equinor/dlisio/issues
