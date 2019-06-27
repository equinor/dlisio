"""
Supporting methods for dataobject class.
Are moved into separate file in order not to clutter interface
"""

import numpy as np
import logging

Simple  = 0
Sampled = 1
Zoned   = 2

def data_attribute(obj, attr, val):
    """
    Checks whether provided attribute is a known data attribute.
    If so, adds value to datapoints and sets default value
    """
    if not attr in obj.datamap:
        return False

    obj.datapoints[attr] = val
    setattr(obj, attr, np.empty(0))
    return True

def combined_dtype(parts, fmtlabel):
    """
    dtype combined of different parts.

    As dtype name will use:
    * part name (if unique)
    * part name with origin and copy numbers
    * DLISIO-CUSTOM-<number> if part object is None

    Parameters
    ----------
    parts:
        list of tuples: (object part, expected dtype)
    fmtlabel:
        recipe for how to format parts with same names
    """
    seen = {}
    types = []

    source = "duplicated mnemonic in object '{}'"
    problem = "but rich label for '{}' cannot be formatted"
    msg = ', '.join((source, problem))
    info = 'name = {}, origin = {}, copynumber = {}'.format

    for i, (o, odtype) in enumerate(parts):
        if o:
            name = o.name
        else:
            # if object is None, assign custom unique name
            name = "DLISIO-CUSTOM-"+str(i)

        current = (name, odtype)

        # first time for this label, register it as "seen before"
        if name not in seen:
            seen[name] = (i, (o, odtype))
            types.append(current)
            continue

        try:
            label = fmtlabel(o.name, o.origin, o.copynumber)
        except (TypeError, ValueError):
            logging.error(msg.format(obj.name, o.name))
            logging.debug(info(o.name, o.origin, o.copynumber))
            raise

        types.append((label, odtype))

        # the first-seen curve with this name has already been updated
        if seen[o.name] is None:
            continue

        prev_index, (prev, prev_dtype) = seen[o.name]

        try:
            label = fmtlabel(prev.name, prev.origin, prev.copynumber)
        except (TypeError, ValueError):
            logging.error(msg.format(obj.name, o.name))
            logging.debug(info(prev.name, prev.origin, prev.copynumber))
            raise

        # update the previous label with this name, and mark (with None)
        # for not needing update again
        types[prev_index] = (label, prev_dtype)
        seen[o.name] = None

    dtype = np.dtype(types)
    return dtype

def value_dtype(obj, data):
    """
    Returns dtype of one single value.
    Ex: i8; 3f8 (for validated values); O (for objects)
    """
    if isinstance(data[0], tuple):
        shape = (len(data[0]), )
    else:
        shape = ()
    dt = np.array(data).dtype
    v_dtype = np.dtype((dt, shape))
    return v_dtype

def element_dtype(obj, data):
    """
    Creates dtype of one element based on dimension and value dtype.
    Ex: (i8, (2, 3)); ( (f8, (2,)), (2, 3) )
    """
    v_dtype = value_dtype(obj, data)
    shape = tuple(obj.dimension)
    el_dtype = np.dtype((v_dtype, shape))
    return el_dtype

def zoned_dtype(obj, data):
    """
    Creates dtype of zoned data based on dtype of each element.
    Ex: [('zone-A', 'i8', (2,)), ('zone-B', 'i8', (2,))]
    """
    el_dtype = element_dtype(obj, data)
    if not obj.zones:
        z_dtype = np.dtype([("unzoned", el_dtype)])
    else:
        parts = [(zone, el_dtype) for zone in obj.zones]
        z_dtype = combined_dtype(parts, obj.dtype_fmt.format)
    return z_dtype

def get_data_length(obj):
    """
    Gets length of sampled, zoned and simple data, asserts it's consistent.
    """
    def assert_data_len_consistency(data, expected_ln):
        if expected_ln:
            assert len(data) == expected_ln
            return expected_ln
        else:
            return len(data)

    sampled_ln, zoned_ln, simple_ln = None, None, None
    try:
        for label, data in obj.datapoints.items():
            datapoint = obj.datamap[label]()
            if   datapoint == Sampled:
                sampled_ln = assert_data_len_consistency(data, sampled_ln)
            elif datapoint == Zoned:
                zoned_ln = assert_data_len_consistency(data, zoned_ln)
            elif datapoint == Simple:
                simple_ln = assert_data_len_consistency(data, simple_ln)
            else:
                msg = "Type {} is not supported"
                raise RuntimeError(msg.format(datapoint))
        return sampled_ln, zoned_ln, simple_ln
    except AssertionError:
        msg = ("Length of data in datapoints inconsistent {} {}. "
               "Shape of doesn't match each other")
        raise ValueError(msg.format(obj.name, obj.__class__))

def assure_dimensionality(obj):
    """
    Verifies whether dimension and axis attributes are provided
    and attempts to supply them if they are not
    """
    if not obj.dimension:
        supply_dimension(obj)
    if obj.axis:
        if len(obj.axis) != len(obj.dimension):
            msg = ("Axes {} were present for {}, "
                   "but do not correspond with dimension {}")
            logging.warning(msg.format(obj.axis, obj.name, obj.dimension))
    else:
        obj.axis = [None] * len(obj.dimension)

def supply_dimension(obj):
    """
    Some files are missing dimension attributes but have data supplied.
    This method attempts to supply this attributed based on data properties.
    """
    try:
        sampled_ln, zoned_ln, simple_ln = get_data_length(obj)
    except ValueError as e:
        logging.warning("Failed to guess missing dimension. "+str(e))
        return

    if sampled_ln or zoned_ln or simple_ln:
        msg = ("Missing dimension for {}. Attempt to supply dimension")
        logging.info(msg.format(obj.name))

        if zoned_ln:
            zones = 1 if len(obj.zones) == 0 else len(obj.zones)
            if zoned_ln % zones == 0:
                obj.dimension = [zoned_ln // zones]
            else:
                msg = ("Failed to guess dimension for zoned obj {} {}. "
                       "Data length is {}, but number of zones is {}, "
                       "so can't get integer number of zones.")
                logging.warning(msg.format(obj.name, obj.__class__,
                                           zoned_ln, zones))
                return
        elif simple_ln:
            if sampled_ln and (sampled_ln % simple_ln != 0):
                msg = ("Failed to guess dimension for sampled obj {} {}. "
                       "Sampled and non-sampled data do not correspond")
                logging.warning(msg.format(obj.name, obj.__class__))
                return
            obj.dimension = [simple_ln]
        elif sampled_ln:
            # if there is no 1-sampled data,
            # consider every value to be a sample
            obj.dimension = [1]
        else:
            raise RuntimeError("Unexpected value in checked if")

def reshape_datapoints(obj):
    """
    Creates numpy array of corresponding dimensions out of identified
    datapoints.
    Before that will try to supply dimension attribute if not provided.
    """
    def reshape(obj, data, array_type):
        if len(data) == 0:
            return np.empty(0)

        if obj.dimension == []:
            msg = ("Unable to identify dimension {} {} and construct values {}")
            logging.warning(msg.format(obj.name, obj.__class__, data))
            return np.empty(0)

        if   array_type == Zoned:
            return reshape_zoned(obj, data)

        elif array_type == Simple:
            return reshape_simple(obj, data)

        elif array_type == Sampled:
            return reshape_sampled(obj, data)

        else:
            raise RuntimeError("Unexpected array type passed: "+array_type)

    assure_dimensionality(obj)

    for label, data in obj.datapoints.items():
        setattr(obj, label, reshape(obj, data, obj.datamap[label]()))

def reshape_simple(obj, data):
    el_dtype = element_dtype(obj, data)
    return np.ndarray(shape=(), dtype=el_dtype, buffer=np.array(data))

def reshape_zoned(obj, data):
    zone_size = np.prod(np.array(obj.dimension))
    zones_nr = 1 if len(obj.zones) == 0 else len(obj.zones)
    if zone_size * zones_nr == len(data):
        z_dtype = zoned_dtype(obj, data)
        return np.ndarray(shape=(), dtype=z_dtype, buffer=np.array(data))
    else:
        msg = ("{} {} Zoned data {} doesn't correspond to dimension {}")
        logging.warning(msg.format(
                       obj.name, obj.__class__, data, obj.dimension))
        return np.empty(0)

def reshape_sampled(obj, data):
    sample_size = np.prod(np.array(obj.dimension))
    if len(data) % sample_size == 0:
        shape = (len(data)//sample_size, )
        el_dtype = element_dtype(obj, data)
        return np.ndarray(shape=shape, dtype=el_dtype, buffer=np.array(data))
    else:
        msg = ("{} {} Sampled data {} doesn't correspond to dimension {}")
        logging.warning(msg.format(
                        obj.name, obj.__class__, data, obj.dimension))
        return np.empty(0)
