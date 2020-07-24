import logging

from .. import core

def obname(objtype):
    def fingerprint(obj):
        if not isinstance(obj, core.obname): raise TypeError
        return obj, objtype
    return fingerprint

def objref(obj):
    if not isinstance(obj, core.objref): raise TypeError
    return obj.name, obj.type

def lookup(lf, reftype, value):
    """Create a fingerprint from reftype(value) and look up corresponding
    object in the logical file."""
    try:
        name, objtype = reftype(value)
    except TypeError:
        msg = "Unable to create object-reference to '{}'"
        logging.warning(msg.format(value))
        return None

    try:
        return lf.object(objtype, name.id, name.origin, name.copynumber)
    except ValueError as e:
        msg = "Unable to find linked object: {}"
        logging.warning(msg.format(str(e)))
        return None

def isreference(val):
    """Check if val is a rp66 reference typ"""
    # TODO: update to check repcode when repcode is back
    return (isinstance (val, core.obname) or
            isinstance (val, core.objref) or
            isinstance (val, core.attref))

def findframe(fp, logical_file):
    """Find all frames containing the channel"""
    frames = []
    for frame in logical_file.frames:
        for channel in frame.channels:
            if channel.fingerprint != fp: continue
            frames.append(frame.attic.name)

    return frames
