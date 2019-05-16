def obname(objtype):
    def fingerprint(obj):
        return obj.fingerprint(objtype)
    return fingerprint

def objref(obj):
    return obj.fingerprint
