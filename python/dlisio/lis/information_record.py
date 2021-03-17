import numpy as np

class InformationRecord():
    """ Information Record

    The 3 LIS Logical Record types Job Identification, Wellsite Data and Tool
    String Info are structured identically. This class implements the interface
    for them all.

    An Information Record can contain:

    - Identification of company name, well name and similar
    - Parameters used in computation
    - Data environments, such as how a curve is presented on a graphical display

    The content of a Information Record can be formatted in one of 2 ways:

    - As a table (structured)
    - As a list of single parameter values (unstructured)

    Whether the record is structured as a table or not, each individual entry
    is represented by a LIS Component Block (CB)
    :class:`dlisio.core.component_block`.

    Notes
    -----

    The LIS79 Specification is ambiguous on which record types that count as
    *Information Records*. The table in ``figure 3.9: Logical Record Types``
    includes Encrypted Table Dump and Table dump in the group called
    Information Records. The rest of the specification refers to Information
    Records as Job Identification, Wellsite Data and Tool String Info Records.
    This is how dlisio defines an Information Record too, as the structure of
    these are identical while Table Dump and Encrypted Table Dump Record share
    a different record structure.
    """
    def __init__(self, attic):
        self.attic = attic

    def __repr__(self):
        msg = 'InformationRecord(type={}, ltell={})'
        return msg.format(self.attic.info.type, self.attic.info.ltell)

    def isstructured(self):
        """ Is the record structured as a table

        Return True if the content of the record is structured as a table,
        otherwise returns False. Empty records - that is records with zero
        Component Blocks are considered unstructured.

        Returns
        -------

        isstructured : bool
        """
        return self.attic.isstructured

    def components(self):
        """ Component Blocks

        Return all the Component Blocks in the record in an unstructured list
        - Regardless of the intended structure of the record.

        Returns
        -------

        Component Blocks : list of :class:`dlisio.core.component_block`

        """
        return self.attic.components

    def table_name(self):
        """ Table name

        When the record contains a table, the name of the table is
        defined by the first Component Block in the record

        Raises
        ------

        ValueError
            If the record contains unstructured data. I.e. the content is not
            formatted as a table.

        Returns
        -------

        dlisio.core.component_block
            A CB containing the name of the table stored in this record
        """
        if not self.isstructured():
            msg  = '{}: Record is not structured as a table. '
            msg += 'Call components() to read CBs from unstructured records'
            raise ValueError(msg.format(self))

        return self.attic.components[0].component

    def table(self, fill=None, simple=False):
        """ Format the Information Record components as a table

        LIS explicitly allows Tables in Information Records to be sparse. That
        is, missing entries are allowed. If some table entries are not recorded
        in the file dlisio will fill that table cell with a default value,
        given by argument ``fill``. E.g. if the following table information is
        recorded in the Information Record::

            MNEM GCOD GDEC DEST DSCA
            ------------------------
            1    E2E  2         S5
            2    BBB  -    PF2

        Then row 1 of 'DEST' and row 2 of 'DSCA' will be filled by dlisio.

        Parameters
        ----------

        fill
            A default value to fill into cells with no data

        simple : bool
            If simple=False, the table will be populated with the
            :class:`component_block` directly. If simple=True, then the
            resulting table will be populated with the values from the
            :class:`dlisio.core.component_block`.

        Raises
        ------

        ValueError
            If the content of the record is not structured as a table.

        ValueError
            If the content of the record is ill-formed.

        Returns
        -------

        table : np.ndarray
            The Information Record structured in a `Numpy Structured Array
            <https://numpy.org/doc/stable/user/basics.rec.html>`_

        """
        if not self.isstructured():
            msg  = '{}: Record is not structured as a table. '
            msg += 'Call components() to read CBs from unstructured records'
            raise ValueError(msg.format(self))

        components = self.attic.components

        if len(components) == 1:
            return np.empty(0)

        if components[1].type_nb != 0:
            msg  = '{}: Ill-formed record, cannot create table. '
            msg += 'Call components() to read content without table-formatting'
            raise ValueError(msg.format(self))

        # Component Blocks of type 0 defines the start of a new row.
        nrows = len([x for x in components if x.type_nb == 0])

        # TODO: If we assume that the order of CB's (w.r.t. mnemonics) within a
        # Datum Block (a row) is consistent across rows, then we can enforce
        # the ordering of the mnemonics (columns) in the outputted array. But
        # note that LIS79 does not enforce such ordering of CB's.
        seen = set()
        columns = []
        for cb in components[1:]:
            if cb.mnemonic in seen: continue
            seen.add(cb.mnemonic)
            columns.append(cb.mnemonic)

        dtype = np.dtype({
            'names'   : columns,
            'formats' : ['O' for _ in columns]
        })
        table = np.full(nrows, fill, dtype=dtype)

        # TODO: verify that there are only unique mnemonics in a given row.
        # (I.e. in range [ CB(type_nb=0), CB(type_nb=0) ). If not, the last
        # instance will overwrite the previous instance(s) in the output table.
        row = -1
        for cb in components[1:]:
            if cb.type_nb == 0: row += 1
            table[cb.mnemonic][row] = cb.component if simple else cb

        return table
