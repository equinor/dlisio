from . import core
from . import plumbing

import re


""" regex and exact matchers are frequently used by most methods on
logicalfile. To avoid the overhead of initializing a new instance of these for
every method-call they are cached as globals here.

Although possible, these globals are not intended to be changed by the end user directly.
"""
regex = plumbing.regex_matcher(re.IGNORECASE)
exact = plumbing.exact_matcher()

def get_encodings():
    """Get codepages to use for decoding strings

    Get the currently set codepages used when decoding strings.

    Returns
    -------
    encodings : list

    See also
    --------
    set_encodings
    """
    return core.get_encodings()

def set_encodings(encodings):
    """Set codepages to use for decoding strings

    RP66 specifies that all strings should be in ASCII, meaning 7-bit. Strings
    in ASCII have identical bitwise representation in UTF-8, and python strings
    are in UTF-8. However, a lot of files contain strings that aren't ASCII,
    but encoded in some way - a common is the degree symbol [1]_, but plenty of
    files use other encodings too.

    This function sets the code pages that dlisio will try *in order* when
    decoding strings (IDENT, ASCII, UNITS, and when they appear as members in
    e.g. ATTREF). UTF-8 will always be tried first, and is always correct if
    the file behaves according to spec.

    Available encodings can be found in the Python docs [2]_.

    If none of the encodings succeed, all strings will be returned as a bytes
    object.

    Parameters
    ----------
    encodings : list of str
        Ordered list of encodings to try

    Warns
    -----
    UnicodeWarning
        When no decode was successful, and a bytes object is returned

    Warnings
    --------
    There is no place in the DLIS spec to put or look for encoding information,
    decoding is a wild guess. Plenty of strings are valid in multiple encodings,
    so there's a high chance that decoding with the wrong encoding will give a
    valid string, but not the one the writer intended.

    Warnings
    --------
    It is possible to change the encodings at any time. However, only strings
    created after the change will use the new encoding. Having strings that are
    out of sync w.r.t encodings might lead to unexpected behaviour.  It is
    recommended that the file is reloaded after changing the encodings to
    ensure that all strings use the same encoding.

    See also
    --------
    get_encodings : currently set encodings

    Notes
    -----
    Strings are decoded using Python's bytes.decode(errors = 'strict').

    References
    ----------
    .. [1] https://stackoverflow.com/questions/8732025/why-degree-symbol-differs
    .. [2] https://docs.python.org/3/library/codecs.html#standard-encodings

    Examples
    --------
    Decoding of the same string under different encodings

    >>> dlisio.set_encodings([])
    >>> with dlisio.load('file.dlis') as (f, *_):
    ...     print(getchannel(f).units)
    b'custom unit\\xb0'
    >>> dlisio.set_encodings(['latin1'])
    >>> with dlisio.load('file.dlis') as (f, *_):
    ...     print(getchannel(f).units)
    'custom unit°'
    >>> dlisio.set_encodings(['utf-16'])
    >>> with dlisio.load('file.dlis') as (f, *_):
    ...     print(getchannel(f).units)
    '畣瑳浯甠楮끴'
    """
    core.set_encodings(list(encodings))
