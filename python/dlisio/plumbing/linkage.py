from .. import core

def obname(objtype):
    def fingerprint(obj):
        return obj.fingerprint(objtype)
    return fingerprint

def objref(obj):
    return obj.fingerprint

def islink(val):
    # TODO: update to check repcode when repcode is back
    return (isinstance (val, core.obname) or
            isinstance (val, core.objref) or
            isinstance (val, core.attref))

def link_attribute(obj, attr, val):
    """
    Checks whether provided attribute is a known link attribute.
    If so, adds value to refs and sets default value
    """
    if isinstance(val, list):
        if len(val) == 0 or not islink(val[0]):
            return False
        attrval = [None] * len(val)
    else:
        if not islink(val):
            return False
        attrval = None

    obj.refs[attr] = val
    setattr(obj, attr, attrval)
    return True
