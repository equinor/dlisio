ValueTypeBoolean = 0
ValueTypeScalar = 1
ValueTypeVector = 2

def boolean(name):
    return (name, ValueTypeBoolean)

def scalar(name):
    return (name, ValueTypeScalar)

def vector(name):
    return (name, ValueTypeVector)
