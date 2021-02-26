from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .describe import describe_dict

from collections import OrderedDict


class Longname(BasicObject):
    """ Structured names of other objects.

    Attributes
    ----------

    modifier : list(str)
        General modifier

    quantity : str
        Something that is measureable E.g. the diameter of a pipe

    quantity_mod : list(str)
        Specialization of a quantity

    altered_form : str
        Altered form of the quantity. E.g. standard deviation is an altered
        form of a temperature quantity.

    entity : str
        The entity of which the quantity is measured. E.g. entity =
        borehole, quantity = diameter

    entity_mod : list(str)
        Specialization of an entity

    entity_nr : str
        Distinguishes multiple instances of the same entity

    entity_part : str
        Part of an entity

    entity_part_nr : str
        Distinguishes multiple instances of the same entity part

    generic_source : str
        The source of the information

    source_part : list(str)
        A specific part of the source information. E.g. "transmitter"

    source_part_nr : list(str)
        Distinguishes multiple instances of the same source part

    conditions : list(str)
        Conditions applicable at the time the information was acquired or
        generated

    standard_symbol : str
        Industry-standardized symbolic name by which the information is
        known. The possible values are specified by POSC

    private_symbol : str
        Association between the recorded information and corresponding
        records or objects of the Producer’s internal or corporate database


    See also
    --------

    BasicObject : The basic object that Longname is derived from

    Notes
    -----

    The Longname object reflects the logical record type LONG-NAME, defined in
    rp66. LONG-NAME objects are listed in Appendix A.2 - Logical Record Types,
    and described in detail in Chapter 5.4.1 - Static and Frame Data, Long-Name
    Objects.
    """

    attributes = {
        'GENERAL-MODIFIER'  : vector,
        'QUANTITY'          : scalar,
        'QUANTITY-MODIFIER' : vector,
        'ALTERED-FORM'      : scalar,
        'ENTITY'            : scalar,
        'ENTITY-MODIFIER'   : vector,
        'ENTITY-NUMBER'     : scalar,
        'ENTITY-PART'       : scalar,
        'ENTITY-PART-NUMBER': scalar,
        'GENERIC-SOURCE'    : scalar,
        'SOURCE-PART'       : vector,
        'SOURCE-PART-NUMBER': vector,
        'CONDITIONS'        : vector,
        'STANDARD-SYMBOL'   : scalar,
        'PRIVATE-SYMBOL'    : scalar,
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def modifier(self):
        return self['GENERAL-MODIFIER']

    @property
    def quantity(self):
        return self['QUANTITY']

    @property
    def quantity_mod(self):
        return self['QUANTITY-MODIFIER']

    @property
    def altered_form(self):
        return self['ALTERED-FORM']

    @property
    def entity(self):
        return self['ENTITY']

    @property
    def entity_mod(self):
        return self['ENTITY-MODIFIER']

    @property
    def entity_nr(self):
        return self['ENTITY-NUMBER']

    @property
    def entity_part(self):
        return self['ENTITY-PART']

    @property
    def entity_part_nr(self):
        return self['ENTITY-PART-NUMBER']

    @property
    def generic_source(self):
        return self['GENERIC-SOURCE']

    @property
    def source_part(self):
        return self['SOURCE-PART']

    @property
    def source_part_nr(self):
        return self['SOURCE-PART-NUMBER']

    @property
    def conditions(self):
        return self['CONDITIONS']

    @property
    def standard_symbol(self):
        return self['STANDARD-SYMBOL']

    @property
    def private_symbol(self):
        return self['PRIVATE-SYMBOL']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['General modifier']   =  self.modifier
        d['Quantity']           =  self.quantity
        d['Quantity modifier']  =  self.quantity_mod
        d['Altered form']       =  self.altered_form
        d['Entity']             =  self.entity
        d['Entity modifier']    =  self.entity_mod
        d['Entity number']      =  self.entity_nr
        d['Entity part']        =  self.entity_part
        d['Entity part number'] =  self.entity_part_nr
        d['Generic source']     =  self.generic_source
        d['Source part']        =  self.source_part
        d['Source part number'] =  self.source_part_nr
        d['Conditions']         =  self.conditions
        d['Standard symbol']    =  self.standard_symbol
        d['Private symbol']     =  self.private_symbol

        describe_dict(buf, d, width, indent, exclude)
