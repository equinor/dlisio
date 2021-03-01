Organization codes
==================

Organizations are assigned their own organization codes by `energistics <https://www.energistics.org/rp66-organization-codes/>`_.
These organization codes typically pop up in the metadata of dlis files, e.g. to identify the producer.

The rp66v1 standard allows vendors to specify their own metadata objects. It
also specifies that the type of such vendor-specific objects should always
start with the organization code like so:

.. code-block:: python

    >>> f.unknowns
    dict_keys(['440-FILE', '440-OP-TOOL', '440-CHANNEL'])

From he naming we can see that these objects are defined by Schlumberger. The
semantic meaning of such objects may only be known to the producer.


=========== =========================================================================
Name (Code) Description (Organization Name)
=========== =========================================================================
0           Subcommittee On Recommended Format For Digital Well Data, Basic Schema
1           Operator
2           Driller
3           Mud Logger
4           Abyssus Marine Services AS
6           ALT – Advanced Logic Technology (added 2014-09-18)
9           Amerada Hess
10          Analysts, The
12          ArenaPetro
15          Baker Hughes Inteq
20          Baroid
30          Birdwell
40          Reeves (1 Jan 99; formerly BPB)
50          Brett Exploration
58          Canrig (added 2009-09-09)
60          Cardinal
65          Center Line Data
66          Subcommittee On Recommended Format For Digital Well Data, DLIS Schema
70          Century Geophysical
77          CGG Logging, Massey France
80          Charlene Well Surveying
85          China Oilfield Services Limited (COSL) (added 2019-02-11)
90          Compagnie de Services Numerique
95          Comprobe
100         Computer Data Processors
110         Computrex
115         COPGO Wood Group
120         Core Laboratories
125         CRC Wireline, Inc.
126         Crocker Data Processing Pty Ltd
127         Tucker Wireline Services (formerly Davis Great Guns Logging, Wichita, KS)
128         Datalog Technology (added 2009-09-09)
130         Digigraph
137         Tucker Technologies (formerly Digital Logging Inc.), Tulsa, OK.
140         Digitech
145         Deines Perforating
148         Drillog Petro-Dynamics Limited
150         Baker Atlas (formerly Dresser Atlas)
155         Dynamic Technologies (DTCC)
160         Earthworm Drilling
170         Electronic Logging Company
180         Elgen
190         El Toro
200         Empire
205         Encom Technology, Ltd.
206         Ensigh Geophysics, Ltd.
208         Epoch (merged with Canrig, Nov 2008; added 2009-09-09)
210         Frontier
213         GeoEnergy, Inc.
214         Geokinetics Inc.
215         Geolog
216         Geophysical Data Systems (added 2015-01-13)
217         Geoshare
218         GEO·X Systems Ltd.
220         G O International
225         GOWell Petroleum (added 2012-04-02)
230         Gravilog
240         Great Guns Servicing
250         Great Lakes Petroleum Services
260         GTS
268         Guardian Data Seismic Pty. Ltd.
270         Guns
280         Halliburton Logging
283         Harvey Rock Physics (added 2015-01-13)
285         Horizon Production Logging
290         Husky
293         INOVA Geophysical Equipment Limited (updated 2012-04-02)
295         Input/Output, Inc.
297         iO Data AS
300         Jetwell
305         Landmark Graphics
310         Lane Wells
315         Logicom Computer Services (UK) Ltd
320         Magnolia
330         McCullough Tool
332         Mitchell Energy Corporation
333         MST Ltd. (Modern Seismic Technologies) – added 2014-08-15)
335         Paradigm Geophysical (formerly Mincom Pty Ltd)
337         DPTS Limited (formerly MR-DPTS Limited, changed as of 2008-08-12)
338         NRI On-Line Inc
339         Oilware, Inc.
340         Pan Geo Atlas
342         Pathfinder Energy Services
345         Perfco
350         Perfojet Services
360         Perforating Guns of Canada
361         Petcom, Inc.
362         CGG (FKA Petroleum Exploration Computer Consultants, Ltd).
363         Petrologic Limited
364         PetroMar Technologies
366         Phillips Petroleum Company
367         Phoenixdata Services Pty Ltd.
368         Petroleum Geo-Services (PGS)
370         Petroleum Information
380         Petrophysics
390         Pioneer
392         The Practical Well Log Standards Group
395         IHS Energy Log Services (formerly Q. C. Data Collectors)
400         Ram Guns
410         Riley’s Datashare
418         RODE
420         Roke
430         Sand Surveys
440         Schlumberger
450         Scientific Software
455         Seismic Instruments, Inc.
460         Seismograph Service
462         SEGDEF
463         SEG Technical Standards High Density Media Format Subcommittee
464         Shell Services Company
465         Stratigraphic Systems, Inc.
466         Spectrum ASA
467         Sperry-Sun Drilling Services
468         SEPTCO
469         Sercel, Inc.
470         Triangle
471         Thrubit Logging(added 2009-09-09)
472         TGS
475         Troika International
480         Welex
490         Well Reconnaissance
495         Wellsite Information Transfer Specification (WITS)
500         Well Surveys
510         Western
520         Westronics
525         Winters Wireline
530         Wireline Electronics
540         Worth Well
560         Z & S Consultants Limited
999         Reserved for local schemas
1000        Energistics (formerly POSC, changed as of 2006-11-06)
=========== =========================================================================
