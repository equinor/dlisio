import logging
import numpy as np


def zonelabels(zones, default):
    """ Creates a list of labels

    Uses Zone.name as a label. If there are multiple zones with the same name,
    Zone.labelfmt is used to distinguish them. If no name if found e.g. the
    zone is None, a default label specifying the number of the zone is used.

    Parameters
    ----------

    zones : list_like of Zone
        Missing Zone's can be None

    default : str
        deafault label to use for missing Zones

    Returns
    -------

    labels : np.array of str
    """
    if len(zones) == 0: return np.array(['DLISIO-UNZONED'])

    labels = []
    seen = {}

    for i, current in enumerate(zones):
        try:
            label = current.name
        except AttributeError:
            label = default + str(i)

        if label in seen:
            # Update the old zone with the same name
            previdx  = seen[label]
            prev     = zones[previdx]
            extended = prev.labelfmt.format(
                prev.name,
                prev.origin,
                prev.copynumber
            )

            labels[previdx] = extended
            seen[extended] = previdx

            label = current.labelfmt.format(
                current.name,
                current.origin,
                current.copynumber
            )

            if label == extended:
                msg  = 'Found duplicated zones (standard violation), '
                msg += 'unable to create unique labels'
                logging.warning(msg)

        labels.append(label)
        seen[label] = i

    return np.array(labels)


def sampling(data, shape, count=1):
    """
    Samplify takes a flat array and returns a structured numpy array, where each
    sample is shaped by shape, i.e. each sample may be scalar or ndarray.

    To structure the array this relationship need to hold [1]:

        len(data) % prod(dimensions) == 0

    [1] If there is no dimensions and only one sample in data, then the output array
        has one scalar sample.
        If there is no dimensions, the relationship can be re-evaluated with
        prod(dimensions) = count, where count is a guess on the samplecount


    Parameters
    ----------

    data : 1-d list_like
        list to be reshaped

    shape : list
        shape of each sample, follows definition by rp66. E.g. [2, 3] is a 2-d
        array with size 2 x 3

    count : int
        a guess on the samplecount, in case the there is no shape

    Returns
    -------

    sampled : np.ndarray
        structured array

    Examples
    --------

    Create a structured array

    >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    >>> dimensions = [2, 3]
    >>> sampled(data, dimensions)
    array(([[[1, 2, 3], [4 , 5, 6]],
            [[7, 8, 9], [10, 11, 12]]])

    Access the 1st sample:

    >>> arr[0]
    array([[1, 2, 3],
           [3, 4, 5])
    """
    data = np.array(data)
    if len(data) == 0: raise ValueError('no data')
    if len(shape) == 0:
        if len(data) == count:
            shape = [1]

        else:
            msg  = 'Empty dimensions, unable to structure array. '
            msg += 'By definition, the standard (rp66) declares the '
            msg += 'array to be undefined'
            logging.warning(msg)
            raise ValueError(msg)

    raw_elements    = len(data)
    sample_elements = int(np.product(np.array(shape)))

    if sample_elements == 0:
        msg = 'invalid dimensions, was {}'.format(shape)
        logging.warning(msg)
        raise ValueError(msg)

    if shape == [1]: shape = 1

    if raw_elements % sample_elements:
        msg  = 'Unable to shape array due to inconsistent dimensions. '
        msg += 'list of len={} cannot be shaped into a even number of '
        msg += 'samples of shape {}'
        msg.format(raw_elements, shape)
        raise ValueError(msg)

    samplecount = int(raw_elements / sample_elements)

    dtype = np.dtype((data.dtype, shape))
    array = np.ndarray(shape=(samplecount,), dtype=dtype, buffer=data)
    return array


def zonify(zones, samples, defaultlabel=None):
    """ Index samples by zone-names

    Parameters
    ----------

    zones : list_like of Zone

    samples : list_like
        structured array where each element should correspond to a zone.

    Returns
    -------

    zoned : dict
        dict of samples, indexed by Zone
    """
    if defaultlabel is None: defaultlabel = 'DLISIO-UNDEF-'

    zones = zonelabels(zones, defaultlabel)

    if len(zones) != len(samples):
        msg  = 'Number of samples ({}), does not match number of zones ({}). '
        msg += 'Using default labels for zone indexing.'
        msg.format(len(samples), len(zones))

        return {defaultlabel + str(i) : value for i, value in enumerate(samples)}

    return {key : value for key, value in zip(zones, samples)}
