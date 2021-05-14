.. currentmodule:: dlisio

Logging
=======

dlisio is using
`Python's standard library logging module <https://docs.python.org/3/library/logging.html#module-logging>`_
to emit several logs.
dlisio only supplies the loggers, while
`configuring <https://docs.python.org/3/howto/logging.html#configuring-logging>`_
them is left to the user.
If not, the logging modules
`default configuration <https://docs.python.org/3/howto/logging.html#what-happens-if-no-configuration-is-provided>`_
applies.

For example, next may be done to make all modules to print to stderr info
messages, not just warnings and errors as it happens by default:

.. code-block:: python

    >>> import logging
    >>> logger = logging.getLogger('dlisio')
    >>> logger.setLevel(logging.DEBUG)
    >>> ch = logging.StreamHandler()
    >>> ch.setLevel(logging.INFO)
    >>> formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    >>> ch.setFormatter(formatter)
    >>> logger.addHandler(ch)

