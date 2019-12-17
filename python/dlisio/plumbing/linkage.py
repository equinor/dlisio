import logging

from .. import core

def obname(objtype):
    def fingerprint(obj):
        if not isinstance(obj, core.obname): raise TypeError
        return obj.fingerprint(objtype), objtype
    return fingerprint

def objref(obj):
    if not isinstance(obj, core.objref): raise TypeError
    return obj.fingerprint, obj.type

def lookup(obj, reftype, value):
    """Create a fingerprint from reftype(value) and look up corresponding
    object in the logical file of obj."""
    try:
        fp, objtype = reftype(value)
    except TypeError:
        msg = "Unable to create object-reference to '{}'"
        logging.warning(msg.format(value))
        return None

    try:
        return obj.logicalfile[objtype][fp]
    except KeyError:
        msg = "Referenced object '{}' not in logical file"
        logging.warning(msg.format(fp))
        return None
    except TypeError:
        msg = 'Unable to find referenced object, {} has no logical file'
        logging.warning(msg.format(obj))
        return None

def isreference(val):
    """Check if val is a rp66 reference typ"""
    # TODO: update to check repcode when repcode is back
    return (isinstance (val, core.obname) or
            isinstance (val, core.objref) or
            isinstance (val, core.attref))
