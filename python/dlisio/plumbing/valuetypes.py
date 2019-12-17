import logging

# Parse attribute as bool. A warning is issued if more than one value is found.
# This typically happens when there are inconsistencies in the file or the file
# violates the standard.
boolean = 1

# Parse attribute as scalar value. A warning is issued if more than one value
# is found. This typically happens when there are inconsistencies in the file
# or the file violates the standard.
scalar  = 2

# Parse attribute as vector.
vector  = 3

# Parse attribute as a vector in reversed order. Usually to accommodate for the
# fact that rp66 defines its array's as column major while python uses row
# major.
reverse = 4

def defaultvalue(attribute):
    """Returns a default value based on the attribute type"""
    if   attribute == scalar:  return None
    elif attribute == vector:  return []
    elif attribute == reverse: return []
    elif attribute == boolean: return None

def parsevalue(value, parse_as):
    """All attributes arrive as lists from the core library. Parse value based
    on parse_as"""
    msg = "Expected only 1 value, found {}, using the first."

    if parse_as == scalar:
        if len(value) != 1:
            logging.warning(msg.format(len(value)))

        value = value[0]
        return value

    elif parse_as == vector:
        return value

    elif parse_as == reverse:
        return value[::-1]

    elif parse_as == boolean:
        if len(value) != 1:
            logging.warning(msg.format(len(value)))
        return bool(value[0])

    else:
        problem = 'unknown value extraction descriptor {}'
        solution = 'should be either scalar, vector, or boolean'
        msg = ', '.join((problem.format(parse_as), solution))
        raise ValueError(msg)
