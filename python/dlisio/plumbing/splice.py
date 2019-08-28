from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .linkage import obname
from .utils import describe_dict, replist

from collections import OrderedDict


class Splice(BasicObject):
    """
    Splice describes the process of concatinating multiple channels into one.
    The concatination is defined by the zone objects, where the first zone
    object corresponds to the first input channel and so on. The zones must be
    mutually disjoint but the ordering is arbitrary::

        Input Ch 1    input Ch 2  -> Output
        -----------------------------------------------
            |            |             |
            |           |              |         Zone1
            |          |               |
        -----------------------------------------------
            |         |               None
        -----------------------------------------------
            |           |               |
            |            |               |       Zone2
            |             |               |
        -----------------------------------------------

    Attributes
    ----------

    output_channel : Channel
        Concatination of all input channels

    input_channels : list(Channel)
        Channels that where used to create the output channel

    Zones : list(Zone)
        Zones of each input channel that is used in the concatination process

    See also
    --------

    BasicObject : The basic object that Splice is derived from

    Notes
    -----

    The Splice object reflects the logical record type SPLICE, defined in
    rp66. SPLICE records are listed in Appendix A.2 - Logical Record Types and
    described in detail in Chapter 5.8.9 - Static and Frame Data, SPLICE
    objects.

    """
    attributes = {
        'OUTPUT-CHANNEL'  : scalar('output_channel'),
        'INPUT-CHANNELS'  : vector('input_channels'),
        'ZONES'           : vector('zones')
    }

    linkage = {
        'output_channel'  : obname('CHANNEL'),
        'input_channels'  : obname('CHANNEL'),
        'zones'           : obname('ZONE')
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'SPLICE')
        self.output_channel  = None
        self.input_channels  = []
        self.zones           = []

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Zones'] = replist(self.zones, 'name')
        d['Output Channel'] = replist(self.output_channel, 'name')
        d['Input Channels'] = replist(self.input_channels, 'name')

        describe_dict(buf, d, width, indent, exclude)
