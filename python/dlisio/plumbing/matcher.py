import re

from .. import core

class regex_matcher(core.matcher):
    """ Regex matcher

    A regex matcher using Python's re module, that can be passed to
    dl::pool::match along with the search patterns.

    Examples
    --------

    create a matcher that is case insensitive and displays debug information,
    and pass it to dl::pool with the search patterns for type and name:

    >>> m = matcher(re.IGNORECASE | re.DEBUG)
    >>> result = metadata.match("TYPE", "NAME", m)
    """
    def __init__(self, flags):
        core.matcher.__init__(self)
        self.flags = flags

    def match(self, pattern, candidate):
        """ Overrides dl::matcher::match """
        try:
            compiled = re.compile(str(pattern), flags=self.flags)
        except:
            msg = 'Invalid regex: {}'.format(pattern)
            raise ValueError(msg)

        if (re.match(compiled, str(candidate))):
            return True
        else:
            return False

