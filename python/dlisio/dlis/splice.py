from collections import OrderedDict

from .basicobject import BasicObject
from . import utils


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
        Concatenation of all input channels

        RP66V1 name: *OUTPUT-CHANNELS*

    input_channels : list(Channel)
        Channels that where used to create the output channel

        RP66V1 name: *INPUT-CHANNELS*

    zones : list(Zone)
        Zones of each input channel that is used in the concatination process

        RP66V1 name: *ZONES*

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
        'OUTPUT-CHANNEL'  : utils.scalar,
        'INPUT-CHANNELS'  : utils.vector,
        'ZONES'           : utils.vector,
    }

    linkage = {
        'OUTPUT-CHANNEL'  : utils.obname('CHANNEL'),
        'INPUT-CHANNELS'  : utils.obname('CHANNEL'),
        'ZONES'           : utils.obname('ZONE')
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def output_channel(self):
        return self['OUTPUT-CHANNEL']

    @property
    def input_channels(self):
        return self['INPUT-CHANNELS']

    @property
    def zones(self):
        return self['ZONES']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Zones'] = utils.replist(self.zones, 'name')
        d['Output Channel'] = utils.replist(self.output_channel, 'name')
        d['Input Channels'] = utils.replist(self.input_channels, 'name')

        utils.describe_dict(buf, d, width, indent, exclude)
