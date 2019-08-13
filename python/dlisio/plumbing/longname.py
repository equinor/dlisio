from .basicobject import BasicObject
from .valuetypes import scalar, vector
from .utils import describe_dict

from collections import OrderedDict


class Longname(BasicObject):
    """ Structured names of other objects.

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
        'GENERAL-MODIFIER'  : vector('modifier'),
        'QUANTITY'          : scalar('quantity'),
        'QUANTITY-MODIFIER' : vector('quantity_mod'),
        'ALTERED-FORM'      : scalar('altered_form'),
        'ENTITY'            : scalar('entity'),
        'ENTITY-MODIFIER'   : vector('entity_mod'),
        'ENTITY-NUMBER'     : scalar('entity_nr'),
        'ENTITY-PART'       : scalar('entity_part'),
        'ENTITY-PART-NUMBER': scalar('entity_part_nr'),
        'GENERIC-SOURCE'    : scalar('generic_source'),
        'SOURCE-PART'       : vector('source_part'),
        'SOURCE-PART-NUMBER': vector('source_part_nr'),
        'CONDITIONS'        : vector('conditions'),
        'STANDARD-SYMBOL'   : scalar('standard_symbol'),
        'PRIVATE-SYMBOL'    : scalar('private_symbol')
    }

    def __init__(self, obj = None, name = None):
        super().__init__(obj, name = name, type = 'LONG-NAME')
        #: General modifier
        self.modifier        = []

        #: Something that is measureable E.g. the diameter of a pipe
        self.quantity        = None

        #: Specialization of a quantity
        self.quantity_mod    = []

        #: Altered form of the quantity. E.g. standard deviation is an altered
        #: form of a temperature quantity.
        self.altered_form    = None

        #: The entity of which the quantity is measured. E.g. entity =
        #: borehole, quantity = diameter
        self.entity          = None

        #: Specialization of an entity
        self.entity_mod      = []

        #: Distinguishes multiple instances of the same entity
        self.entity_nr       = None

        #: Part of an entity
        self.entity_part     = None

        #: Distinguishes multiple instances of the same entity part
        self.entity_part_nr  = None

        #: The source of the informations
        self.generic_source  = None

        #: A spesific part of the source information. E.g. "transmitter"
        self.source_part     = []

        #: Distinguishes multiple instances of the same source part
        self.source_part_nr  = []

        #: Conditions applicable at the time the information was acquired or
        #: generated
        self.conditions      = []

        #: Industry-standardized symbolic name by which the information is
        #: known. The possible values are specified by POSC
        self.standard_symbol = None

        #: Association between the recorded information and corresponding
        #: records or objects of the Producer’s internal or corporate database
        self.private_symbol  = None

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
