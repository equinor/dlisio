from .. import core


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
    but are encoded in some way - a common is the degree symbol [1]_. Plenty of
    files use other encodings too.

    LIS does not explicitly mention that strings should be ASCII, but it also
    doesn't mention any encodings.

    This function sets the code pages that dlisio will try *in order* when
    decoding the string-types specified by LIS and DLIS. UTF-8 will always be
    tried first, and is always correct if the file behaves according to spec.

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
    There is no place in the LIS or DLIS spec to put or look for encoding
    information, decoding is a wild guess. Plenty of strings are valid in
    multiple encodings, so there's a high chance that decoding with the wrong
    encoding will give a valid string, but not the one the writer intended.

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

    >>> from dlisio import dlis, common
    >>> common.set_encodings([])
    >>> with dlis.load('file.dlis') as (f, *_):
    ...     print(getchannel(f).units)
    b'custom unit\\xb0'
    >>> common.set_encodings(['latin1'])
    >>> with dlis.load('file.dlis') as (f, *_):
    ...     print(getchannel(f).units)
    'custom unit°'
    >>> common.set_encodings(['utf-16'])
    >>> with dlis.load('file.dlis') as (f, *_):
    ...     print(getchannel(f).units)
    '畣瑳浯甠楮끴'
    """
    core.set_encodings(list(encodings))
