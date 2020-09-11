import re

from .. import core

class regex_matcher(core.matcher):
    """ Regex matcher

    A regex matcher using Python's re module, that can be passed to
    dl::pool::get along with the search patterns.

    Examples
    --------

    create a matcher that is case insensitive and displays debug information:

    >>> matcher = regex_matcher(re.IGNORECASE | re.DEBUG)

    Which then can be used like so:

    >>> matcher.match("FO*", "FOO")
    True
    """
    def __init__(self, flags=0):
        core.matcher.__init__(self)
        self.flags = flags

    def match(self, pattern, candidate):
        """ Overrides dl::matcher::match """
        try:
            compiled = re.compile(str(pattern), flags=self.flags)
        except:
            msg = 'Invalid regex: {}'.format(pattern)
            raise ValueError(msg)

        return bool(re.match(compiled, str(candidate)))

class exact_matcher(core.matcher):
    """ Exact matcher

    A matcher using the == operator for comparison, that can be passed to
    dl::pool::get along with the search parameter(s).
    """
    def __init__(self):
        core.matcher.__init__(self)

    @staticmethod
    def match(pattern, candidate):
        """ Overrides dl::matcher::match """
        return pattern == candidate
