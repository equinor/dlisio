import logging
import numpy as np

from collections import OrderedDict, namedtuple
from textwrap import fill

from .dimensional import issequence, validshape, sampling

class Summary():
    """Summary of metadata object"""
    def __init__(self, info=None):
        self.info = info

    def __repr__(self):
        return self.info

def headerinfo(obj):
    """Get headerinfo from object"""
    d = OrderedDict()
    d['name']   = obj.name
    d['origin'] = obj.origin
    d['copy']   = obj.copynumber
    return d

def parseoptions(fmt):
    """"Create a dict with option based fmt-string"""
    modes = set([x for x in fmt])

    options = {
        'attr'  : False,
        'empty' : False,
        'head'  : False,
        'stash' : False,
        'inv'   : False,
        'refs'  : False,
        'units' : False
    }

    if 'e' in modes: options['empty'] = True
    if 'a' in modes: options['attr']  = True
    if 'h' in modes: options['head']  = True
    if 'i' in modes: options['inv']   = True
    if 's' in modes: options['stash'] = True
    if 'r' in modes: options['refs']  = True
    if 'u' in modes: options['units'] = True
    return options

def remove_empties(d):
    """Drop entries with no value. '0' is considered to be a valid value."""
    clean = OrderedDict()
    for key, attr in d.items():
        try:
            value = attr.value
        except AttributeError:
            value = attr

        if issequence(value):
            if all(not entry and entry != 0
                   for entry in np.array(value).flatten()) :
                continue
        else:
            if not value and value != 0: continue

        clean[key] = attr

    return clean

def replist(elements, mode):
    """Customize representation of metadata objects. Elements that are not
    derived from BasicObject are represented as is.

    Attributes
    ----------

    elements : list_like

    mode : str
        How metadata objects should be represented [1]


    Returns
    -------

    replist : list of str

    Notes
    -----

    [1] Mode gives the option to choose what information that should be
    included in the representation string:

    ========== ==================================================
    mode       Description
    ========== ==================================================
    'name'     names as repr, e.g 'TIME'
    'typename' type and name as repr, e.g 'Channel('TIME')'

    otherwise  full representation with type, name, origin, copy
    ========== ==================================================
    """
    from .basicobject import BasicObject

    try:
        elements = list(elements)
    except TypeError:
        return elements

    reprs = []

    for x in elements:
        if not issubclass(x.__class__, BasicObject):
            reprs.append(str(x))
            continue

        if mode == 'name':
            rep = x.name
        elif mode == 'typename':
            rep = repr(x)
        else:
            rep = '{}({}, {}, {})'.format(
                x.type.capitalize(),
                x.name,
                x.origin,
                x.copynumber
            )

        reprs.append(rep)

    return reprs

def describe_header(buf, text, width, indent, lvl=1):
    """Create a header or a section header"""
    if text is None: return text

    if lvl == 1:
        sep = ''.join('-' for _ in range(len(text)))
        text = [sep, text, sep]
    elif lvl == 2:
        sep = '--'
        text = [text, '--']

    for line in text:
        describe_text(buf, line, width, indent)

def describe_description(buf, description, width, indent, exclude):
    """If description references a long_name objects, use its describe. Else
    print as is."""
    if not description and exclude['empty']: return None

    try:
        ln = description.describe(width=width, indent=indent, exclude='hes')
        describe_header(buf, 'Description', width, indent, lvl=2)
        buf.write(repr(ln))

    except AttributeError:
            d = {'Description' : description}
            describe_dict(buf, d, width, indent, exclude)

# performance is twice better if this is defined outside of all functions
object_attribute = namedtuple('ObjectAttribute', 'value, units')

def describe_sampled_attrs(buf, attic, dims, valuekey, extras, width, indent,
        exclude, single=True):
    """Describe attributes that needs to be sampled (re-shaped)"""

    valids, invs = OrderedDict(), OrderedDict()
    try:
        value = attic[valuekey].value
        units = attic[valuekey].units
        shape = validshape(value, dims)
        valids['Value(s)'] = object_attribute(sampling(value, shape), units)
    except KeyError:
        pass
    except ValueError:
        invs['Value(s)'] = object_attribute(value, units)

    if extras:
        for label, key in extras.items():
            try:
                value = attic[key].value
                units = attic[key].units
                shape = validshape(value, dims)
                valids[label] = object_attribute(
                    sampling(value, shape, single=single), units)
            except KeyError:
                pass
            except ValueError:
                invs[label] = object_attribute(value, units)

    if valids:
        describe_dict(buf, valids, width, indent, exclude)

    if not exclude['inv'] and invs:
        describe_header(buf, 'Invalid dimensions', width, indent, lvl=2)
        describe_dict(buf, invs, width, indent, exclude)

def describe_attributes(buf, d, obj, width, indent, exclude=None):
    """Describe attributes that first need to be retrieved from object.
    If value is not found in objects attribute dictionary, it is assumed to be
    a simple value and will be printed without any changes
    """
    for key, label in d.items():
        if label not in obj.attic.keys():
            try:
                if label in obj.attributes.keys():
                    # key is valid, but not present. Retrieve default
                    d[key] = obj[label]
            except TypeError:
                continue
        else:
            value = obj[label]
            units = obj.attic[label].units
            d[key] = object_attribute(value, units)

    describe_dict(buf, d, width, indent, exclude)

def describe_dict(buf, d, width, indent, exclude=None):
    """Print a dict nicely into the buffer"""

    if exclude is None: exclude = parseoptions('')
    if exclude['empty']: d = remove_empties(d)

    if len(d) == 0: return

    keylen = len(max(list(d.keys()), key=len))
    subindent = ''.ljust(keylen)

    for key, attr in d.items():
        units = ""
        try:
            value = attr.value
            if not exclude['units']:
                units = attr.units.strip()
        except AttributeError:
            value = attr
        prefix    = ''.join([indent, key.ljust(keylen), ' : '])
        subindent = ''.ljust(len(prefix))

        if issequence(value):
            describe_array(buf, value, width, prefix, subindent=subindent, writeempty=True, units=units)
        else:
            describe_text(buf, value, width, prefix, subindent=subindent, units=units)
    buf.write('\n')

def describe_text(buf, text, width, indent, subindent=None, units=''):
    """Wrap text with textwrapper and write to the buffer"""

    if subindent is None: subindent = indent

    if text is None: text = str(None)
    else: text = str(text)

    if len(text) == 0: text = '""'

    wrapped = fill(
        '{}{units}'.format(text, units=" [{}]".format(units) if units else ""),
        width             = width,
        initial_indent    = indent,
        subsequent_indent = subindent
    )
    buf.write(wrapped)
    buf.write('\n')

def describe_array(buf, a, width, indent, subindent=None, writeempty=False, units=''):
    """Write a list into the buffer in a nice printable way"""
    if subindent is None: subindent = indent

    a = np.array(a)
    if len(a) == 0 and not writeempty:
        return

    if len(a) == 0 and writeempty:
        describe_text(buf, [], width, indent, subindent, units=units)
        return

    if a.size == 1:
        describe_text(buf, a[0], width, indent, subindent, units=units)
        return

    sep = ' '
    if a.ndim > 1:
        # Let numpy's array2string handle multidimensional arrays
        buf.write(indent)
        samples = np.array2string(
            a,
            prefix = subindent,
            separator = sep,
            max_line_width = width
        )
        buf.write(samples)
        # TODO:
        # 1) units might make length > width
        # 2) default [] might not look very nice with multidimensional values
        buf.write(" [{}]".format(units) if units else "")
        buf.write('\n')
        return

    reprs = [str(x) for x in a]

    maxlen = len(max(reprs, key=len))
    text = sep.join([x.ljust(maxlen) for x in reprs])
    describe_text(buf, text, width, indent, subindent=subindent, units=units)
