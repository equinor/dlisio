from .basicobject import BasicObject
from .valuetypes import scalar
from .utils import describe_attributes

from collections import OrderedDict

class Noformat(BasicObject):
    """
    Noformat objects contain description of unformatted data present in files.

    Attributes
    ----------

    consumer_name : str
        Client-provided name for the data, for example an external file
        specification

    description : str
        Textual description

    See also
    --------

    BasicObject : The basic object that Nofromat is derived from

    Notes
    -----

    The Noformat object reflects the logical record type NO-FORMAT, described in
    rp66. NO-FORMAT objects are defined in Appendix A.2 - Logical Record Types,
    described in detail in Chapter 5.10.1 Static and Frame Data, No-Format
    Objects.
    """
    attributes = {
        'CONSUMER-NAME' : scalar,
        'DESCRIPTION'   : scalar,
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def consumer_name(self):
        return self['CONSUMER-NAME']

    @property
    def description(self):
        return self['DESCRIPTION']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Consumer name'] = 'CONSUMER-NAME'
        d['Description']   = 'DESCRIPTION'

        describe_attributes(buf, d, self, width, indent, exclude)
