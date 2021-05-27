from collections import OrderedDict

from .basicobject import BasicObject
from . import utils


class Noformat(BasicObject):
    """
    Noformat objects contain description of unformatted data present in files.

    Attributes
    ----------

    consumer_name : str
        Client-provided name for the data, for example an external file
        specification

        RP66V1 name: *CONSUMER-NAME*

    description : str
        Textual description

        RP66V1 name: *DESCRIPTION*

    See also
    --------

    BasicObject : The basic object that Nofromat is derived from

    Notes
    -----

    The Noformat object reflects the logical record type NO-FORMAT, described in
    rp66. NO-FORMAT objects are defined in Appendix A.2 - Logical Record Types,
    described in detail in Chapter 5.10.1 Static and Frame Data, No-Format
    Objects.
    """
    attributes = {
        'CONSUMER-NAME' : utils.scalar,
        'DESCRIPTION'   : utils.scalar,
    }

    def __init__(self, attic, lf):
        super().__init__(attic, lf=lf)

    @property
    def consumer_name(self):
        return self['CONSUMER-NAME']

    @property
    def description(self):
        return self['DESCRIPTION']

    def describe_attr(self, buf, width, indent, exclude):
        d = OrderedDict()
        d['Consumer name'] = 'CONSUMER-NAME'
        d['Description']   = 'DESCRIPTION'

        utils.describe_attributes(buf, d, self, width, indent, exclude)

    def data(self):
        """Raw data

        A raw byte buffer of all the records corresponding to the noform-object.
        Content of this data is not defined by rp66v1. However, the name and
        description of the no-format object might give an indication about its
        content.

        Returns
        -------
        data : bytes
            Raw bytes

        Examples
        --------
        Look at the description of the no-format object to see if it contains
        information about nature of the data

        >>> print(noformat.describe())
        ---------
        No-format
        ---------
        name   : 2
        origin : 0
        copy   : 0
        ---
        Consumer name : FILE
        Description   : /home/files.txt

        Save the data

        >>> out = open('noformat.txt', 'wb')
        >>> out.write(noformat.data())
        >>> out.close()

        It is not uncommon that the no-format object itself is not enough to
        understand its content. Some vendors store additional information in
        other custom object types. In that case some manual digging into the
        file might reveal the information necessary to correctly understand
        the no-format content:

        >>> images = f.find('.*IMAGE.*', matcher=dlisio.dlis.utils.regex_matcher())
        >>> for image in images:
        >>>     print(image.describe())
        ---------
        my_image
        ---------
        name   : MYIMAGE
        origin : 0
        copy   : 0
        ---
        Unknown attributes
        --
        NAME          : MYIMAGE.PNG
        NOFORMAT-NAME : dlisio.core.obname(id='MYIMAGE', origin=0, copynum=0)

        Check for no-format records:

        >>> for noformat in f.noformats:
        >>>     print(noformat.describe())
        ---------
        No-format
        ---------
        name   : NOFORMAT-MYIMAGE
        origin : 0
        copy   : 0
        ---
        Consumer name : MYIMAGE
        Description   : My very important image

        Store the result:

        >>> noformat = f.object("NO-FORMAT", "NOFORMAT-MYIMAGE")
        >>> out = open('MYIMAGE.PNG', 'wb')
        >>> out.write(noformat.data())
        >>> out.close()
        """
        return utils.noformat(self)
