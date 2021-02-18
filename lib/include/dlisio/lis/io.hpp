#ifndef DLISIO_LIS_IO_HPP
#define DLISIO_LIS_IO_HPP

#include <vector>
#include <string>
#include <ciso646>

#include <lfp/lfp.h>
#include <lfp/tapeimage.h>

#include <dlisio/lis/protocol.hpp>
#include <dlisio/stream.hpp>


namespace dlisio { namespace lis79 {
namespace lis = dlisio::lis79;

struct range {
public:
    using iterator = std::vector< record_info >::const_iterator;
    explicit range(iterator begin, iterator end) : start(begin), stop(end) {};

    iterator begin() const noexcept (true);
    iterator end() const noexcept (true);
    std::size_t size() const noexcept (true);

private:
    iterator start;
    iterator stop;
};

/** Index of Logical Records (LR)
 *
 * The index can contain arbitrary Logical Records, but is mainly intended to
 * store the LR's from one Logical File. Its main purpose is to give random
 * access to LR's within a LF.
 *
 * Implicit records (normal data and alternate data) are stored separately from
 * explicit- and fixed records to reduce the overhead of searching for specific
 * LR types. The absolute record order can be reconstructed from the tells in
 * the record_info's if needed.
 */
struct record_index {
public:
    record_index( std::vector< record_info > ex,
                  std::vector< record_info > im ) :
        expls( std::move(ex) ), impls( std::move(im) ) {};

    /** Return all assosiated iflr's given a Data Format Specification Record
     * (DFSR)
     *
     * Given a DFSR, implicits_of creates an iterable of implicit records
     * following the DFSR, terminated by either a new DFSR or End-of-Index.
     *
     * LIS79 does not explicitly mention the support for multiple DFSR or
     * logsets, other than redundant/identical copies of the same DFSR, but
     * states:
     *
     * > The Data Record is the key to the LIS format as it defines the format
     * of data in a data record that follows [1].
     *
     * Which we take to mean that the following relationship holds
     *
     *         logset0          logset1            logset2
     * |                       |       |                               |
     *  ---------------------------------------------------------------
     * | DFSR0 | IFLR0 | IFLR1 | DFRS1 | DFSR2 | IFLR2 | IFLR3 | IFLR4 |
     *  ---------------------------------------------------------------
     *
     * That is:
     *  - DFSR0 describes the content of IFLR0 and IFLR1
     *  - DFSR1 is either an empty logset or a duplicate of DFRS2 [2]
     *  - DFSR2 describes the content of IFLR2-4.
     *
     * Note that the returned range is working on iterators on the internal
     * storage of the record_index. This means it should be regarded as a short
     * lived object, which will be invalid if it outlives the record_index
     * itself.
     *
     * [1] spec ref: LIS79 ch 3.3.2
     * [2] spec ref: LIS79 ch 3.5 (group 2)
     */
    range implicits_of( std::int64_t dfsr_tell ) const noexcept (false);
    range implicits_of( const record_info& info ) const noexcept (false);

    /* Return all explicit- and fixed records */
    const std::vector< record_info >& explicits() const noexcept (true);

    /* Return all implicit records */
    const std::vector< record_info >& implicits() const noexcept (true);

    /* The number of records in the index */
    std::size_t size() const noexcept (true);
private:
    std::vector< record_info > expls {}; //and fixed
    std::vector< record_info > impls {};
};

/** LIS aware IO device
 *
 * iodevice provides an interface for indexing and reading logical records (LR)
 * from a raw LIS file.
 *
 * On disk, a LIS file is essentially organized as a
 * sequence of Physical Records (LR):
 *
 *                PR1               PR2               PR3
 *     |                     |               |                     |
 *      -----------------------------------------------------------
 *     | PRH | LRH | LR data | PRH | LR data | PRH | LRH | LR data |
 *      -----------------------------------------------------------
 *
 * In short, a PR is a mechanics for segmenting LRs into smaller chunks. LR's
 * _always_ start at the begining of a new PR, and may span multiple. Whether
 * or not a LR spans multiple LR's is described by the succesor/predeccesor
 * attributes in the PR headers:
 *
 *           predeccesor     successor   LRn     contains LRH
 *           ------------------------------------------------
 *      PR1      0               1       0           yes
 *      PR2      1               0       0           no
 *      PR3      0               0       1           yes
 *           ------------------------------------------------
 *
 * This means that the 3 PR's from the first illustration encapsulate 2 LRs.
 * The first LR spans PR1-PR2, and the second LR is contained entirely in PR3.
 * Note that the LR header is *not* repeated in each PR when the LR spans
 * multiple PRs.
 */
struct iodevice : public dlisio::stream {
public:
    explicit iodevice( lfp_protocol* p ) : dlisio::stream(p) {};

    /* Read the physical header from the file. UB if the next byte that is
     * _not_ a padbyte is not a part of the header [1]
     *
     * [1] LIS allows for unspecified padbytes between physical records. To combat
     * this, read_physical_header will scan passed any leading padbytes it might
     * find and then read the first non-padbytes as the header.
     *
     * @throw lis::eof_error
     *      function called at EOF or if all remaining bytes are padding.
     * @throw lis::io_error
     *      unable to read enough bytes from disk (not EOF)
     * @throw lis::truncation_error
     *      unable to read enough bytes from disk (EOF)
     */
    lis::prheader read_physical_header() noexcept (false);

    /* UB if position not at start of header - Should only be called directly
     * after a successful call to read_physical_header (and predecessor=0).
     */
    lis::lrheader read_logical_header()  noexcept (false);

    /** Create an index of Logical Records (LR)
     *
     * This function will return the index when hitting EOF or encountering one
     * of the following records:
     *
     *  - File Trailer Logical Record (TTLR)
     *  - Reel Header  Logical Record (RHLR)
     *  - Reel Trailer Logical Record (RTLR)
     *  - Tape Header  Logical Record (THLR)
     *  - Tape Trailer Logical Record (TTLR)
     *  - Logical EOF  Logical Record (LEOF)
     *
     *  or if encountering a File Header Logical Record (FHLR) that is not
     *  first in in the record. The second FHLR will _not_ be included in the
     *  index. This can typically be the case if the optional FTLR is missing.
     *
     *  In any case, the tell is left at the start of the _next_ LR in line, or
     *  at EOF.
     *
     * The returned record_index is a lightweight LR index which essentially
     * provides random-access to the LR's within the LF.
     */
    record_index index_records() noexcept (true);

    /** Index the next record
     *
     * Assumes that the next non-padbyte is the start of a PRH
     *
     * @throw lis::eof_error
     *      function called at EOF or if all remaining bytes are padding.
     * @throw lis::io_error
     *      unable to read enough bytes from disk (not EOF)
     * @throw lis::truncation_error
     *      unable to read enough bytes from disk (EOF)
     */
    record_info index_record() noexcept (false);
    record read_record( const record_info& ) noexcept (false);

    bool truncated() const noexcept (false);
    bool indexed() const noexcept (true);
private:
    bool is_indexed   = false;
    bool is_truncated = false;
};

/** Factory function for creating an iodevice
 *
 * Opens a new file handle for 'path', starting at offset 'offset'. The iodevice
 * wraps a lfp cfile protocol, and a lfp tapeimage if specififed.
 *
 * lfp_protocols and iodevice are opened without reading anything from the
 * file, which means it's perfectly valid to open a new iodevice at EOF without
 * the construction failing.
 *
 * A common use-case in lis is to open new file-handles for each logical file
 * until there are no more. Because lis in itself doesn't provide any clues to
 * whether there are more logical files to come in the current file this
 * process involves _trying_ to open-and-read new logical files until EOF hits.
 *
 * To make this process more smooth, open reads a single byte to verify that
 * the iodevice is not opened at EOF. If it is, open throws a lis::eof_error.
 * */
iodevice open( const std::string& path, std::int64_t offset, bool tapemark)
noexcept (false);

} // namespace lis79

} // namespace dlisio

#endif // DLISIO_LIS_IO_HPP
