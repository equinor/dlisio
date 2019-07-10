ValueTypeBoolean = 0
ValueTypeScalar = 1
ValueTypeVector = 2
ValueTypeReverse = 3
ValueTypeDict = 4

def boolean(name):
    return (name, ValueTypeBoolean)

def scalar(name):
    return (name, ValueTypeScalar)

def vector(name):
    return (name, ValueTypeVector)

def reverse(name):
    return (name, ValueTypeReverse)

def dictentry(name):
    return (name, ValueTypeDict)

def vtvalue(value_type, value):
    """
    Returns actual value of value vector based on value_type
    """
    if value_type == ValueTypeScalar:
        return value[0]

    elif value_type == ValueTypeVector:
        return value

    elif value_type == ValueTypeReverse:
        return value[::-1]

    elif value_type == ValueTypeBoolean:
        return bool(value[0])

    elif value_type == ValueTypeDict:
        return value[0]

    else:
        problem = 'unknown value extraction descriptor {}'
        solution = 'should be either scalar, vector, or boolean'
        msg = ', '.join((problem.format(value_type), solution))
        raise ValueError(msg)
