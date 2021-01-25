#ifndef DLISIO_LIS_PROTOCOL_HPP
#define DLISIO_LIS_PROTOCOL_HPP

#include <cstdint>
#include <ciso646>
#include <vector>

#include <mpark/variant.hpp>

#include <dlisio/lis/types.hpp>

namespace dlisio { namespace lis79 {

/** Logical Record Header (LRH)
 *
 * A Logical Record starts with LRH. This header defines the type of the
 * record. It should be one of the values defined in `lis::record_type`.  The
 * field undefined is - as the name suggest - undefined and unused by the LIS79
 * standard.
 *
 * spec ref: LIS79 ch 2.2.1.1
 */
struct lrheader {
    lis::byte    type;
    std::uint8_t undefined;

    static constexpr const int size = 2;
};

/** Read Logical Record Header
 *
 * Read and parse the next lis::lrheader::size bytes into a lis::lrheader
 * instance.
 */
lrheader read_lrh(const char* xs) noexcept (false);

/** Physical Record Header (PRH)
 *
 * Physical Records are the glue between the physical format (raw bytes on
 * disk) and the logical format.
 *
 * The PRH length includes the header itself and the Physical Record Trailer (if
 * present).
 *
 * The PRH attributes is a bitmask. The successor and predecessor bits define
 * if the content of this PR is part of the same LR as the previous/next PR's.
 * These are needed to stitch together LR's that are segmented onto multiple
 * PR's.
 *
 * spec ref: LIS79 ch 2.3.1.1
 */
struct prheader {
    std::uint16_t length;
    std::uint16_t attributes;

    static constexpr const int size = 4;

    static constexpr const int rectype = 1 << 14;
    static constexpr const int chcksum = 1 << 13 | 1 << 12;
    static constexpr const int filenum = 1 << 10;
    static constexpr const int reconum = 1 << 9;
    static constexpr const int parierr = 1 << 6;
    static constexpr const int chckerr = 1 << 5;
    static constexpr const int predces = 1 << 1;
    static constexpr const int succses = 1 << 0;
};

/** Read Physical Record Header
 *
 * Read and parse the next lis::prheader::size bytes into a lis::prheader
 * instance.
 */
prheader read_prh(char* xs) noexcept (false);

/** Check if all bytes in the buffer are pad-bytes
 *
 * The spec allows for an unspecified number of pad-bytes between Physical
 * Records. Because there is no hint if and now many pad-bytes are present, it
 * must be checked manually between each PR. This function checks if the next n
 * bytes of a buffer are all pad-bytes.
 *
 * Returns true if all bytes are pad-bytes, that is, all bytes are
 * either 0x20 or 0x00.
 */
bool padbytes(const char* xs, std::uint16_t n);

/** Record types
 *
 *  All valid record types defined by LIS79.
 */
enum class record_type : std::uint8_t {
    normal_data  = 0,
    alt_data     = 1,
    job_id       = 32,
    wellsite     = 34,
    toolstring   = 39,
    encrp_table  = 42,
    table_dump   = 47,
    format_spec  = 64,
    descriptor   = 65,
    sw_boot      = 95,
    bootstrap    = 96,
    cp_kernel    = 97,
    program_fh   = 100,
    program_oh   = 101,
    program_ol   = 102,
    fileheader   = 128,
    filetrailer  = 129,
    tapeheader   = 130,
    tapetrailer  = 131,
    reelheader   = 132,
    reeltrailer  = 133,
    logical_eof  = 137,
    logical_bot  = 138,
    logical_eot  = 139,
    logical_eom  = 141,
    op_command   = 224,
    op_response  = 225,
    sys_output   = 227,
    flic_comm    = 232,
    blank_rec    = 234,
    picture      = 85,
    image        = 86
};

/** Check if type is a valid LIS79 record type
 *
 * Return if the value of type is defined in lis::record_type, else returns
 * false.
 */
bool valid_rectype(lis::byte type);

/** (Logical) Record Info
 *
 * A Logical Record (LR) always starts on a new Physical Record (PR) and may
 * span multiple PR's. While each PR has it's own header (PRH), the LR Header
 * (LRH) is only recorded once - At the start of the *first* PR.
 *
 * record_info contains all information needed in order to find and extract
 * the content of the Logical Record.
 */
struct record_info {
    std::int64_t  ltell; // offset to the *first* PR
    lis::lrheader lrh;   // Logical Record Header
    lis::prheader prh;   // The _first_ Physical Record Headers

    bool consistent = true; // TODO implement succ/pred check
    std::size_t size;
    record_type type() const noexcept (false);
};

/** Logical Record (LR)
 *
 * A raw buffer of the Logical Record. This buffer is a contiguous sequence of
 * all bytes that constitutes the _full_ Logical Record, ready to be parsed.
 * That is:
 *
 *                   -----------------------------------------------
 * File on disk:    | PRH | data1 | PRH | data2 | PRT | PRH | data3 |
 *                   -----------------------------------------------
 *
 *                   -----------------------
 * record.data:     | data0 | data1 | data2 |
 *                   -----------------------
 */
struct record {
    record_info         info;
    std::vector< char > data;
};

using value_type = mpark::variant<
    mpark::monostate,
    lis::i8,
    lis::i16,
    lis::i32,
    lis::f16,
    lis::f32,
    lis::f32low,
    lis::f32fix,
    lis::string,
    lis::byte,
    lis::mask
>;

/** A base class for for all parsed record types
 *
 * The purpose of this class is to carry over the header information and the
 * tell from the raw records.  The tell is a unique identifier for lis::record
 * and serves as a light-weight reference such that the source of the object is
 * not lost. This information is _especially_ important when dealing with DFS
 * records and their implicit relationship to the following implicit records.
 *
 * If this class is going to live in it's current for remains to see, but as a
 * short-term solution it serves as nicely as a bridge between unparsed- and
 * parsed data.
 */
struct parsed_record {
    lis::record_info info;
};

enum class entry_type : std::uint8_t {
    terminator         = 0,
    data_rec_type      = 1,
    spec_block_type    = 2,
    frame_size         = 3,
    up_down_flag       = 4,
    depth_scale_units  = 5,
    ref_point          = 6,
    ref_point_units    = 7,
    spacing            = 8,
    spacing_units      = 9,
    undefined          = 10,
    max_frames_pr_rec  = 11,
    absent_value       = 12,
    depth_rec_mode     = 13,
    units_of_depth     = 14,
    reprc_output_depth = 15,
    spec_bloc_subtype  = 16,
};

/** Entry Block (EB)
 *
 * General information about the "frame".
 *
 * A Entry Block can be one of the types defined in lis::entry_type. All types
 * are equally structured, but differ in semantic meaning. Often the mere
 * presence/absence of a given type has semantic meaning. Such behavior should be
 * enforced on a higher level, such as lis::dfsr
 *
 * spec ref: LIS79 ch 4.1.6
 */
struct entry_block {
    lis::byte type;
    lis::byte size;
    lis::byte reprc;

    value_type value;
};

entry_block read_entry_block(const record&, std::size_t*) noexcept (false);

namespace {

struct spec_block {
    lis::string mnemonic;
    lis::string service_id;
    lis::string service_order_nr;
    lis::string units;
    lis::i16    filenr;
    lis::i16    ssize;
    lis::byte   samples;
    lis::representation_code reprc;
};

}

/** Data Specification Block - subtype 0 (DSB0)
 */
struct spec_block0 : spec_block {
    lis::byte api_log_type;
    lis::byte api_curve_type;
    lis::byte api_curve_class;
    lis::byte api_modifiers;

    static constexpr const int size = 40;
};

/** Data Specification Block - subtype 1 (DSB1)
 */
struct spec_block1 : public spec_block {
    lis::byte api_log_type;
    lis::byte Vapi_curve_type;
    lis::byte api_curve_class;
    lis::byte api_modifiers;

    static constexpr const int size = 40;
};

spec_block0 read_spec_block0(const record&, std::size_t*) noexcept (false);
spec_block1 read_spec_block1(const record&, std::size_t*) noexcept (false);

/** Data Format Specification Record (DFSR)
 *
 * Contains all information needed to parse the sub-sequent implicit (normal
 * data) records. The Entry Block are essentially attributes containing general
 * information about the frame as a whole. Each DSB contains information about
 * a single channel. Together these contain the necessary information to parse
 * a row of data from an iflr.
 *
 * TODO: The entry_blocks has a lot of implicit behavior tied to them (e.g.
 * their presence/absence. Support all the implied behavior
 *
 * spec ref: LIS79 ch 4.1.6
 */
struct dfsr : public parsed_record {
    std::vector< entry_block > entries;
    std::vector< spec_block > specs;
};

dfsr parse_dfsr( const lis::record& ) noexcept (false);

std::string dfs_fmtstr( const dfsr& dfs ) noexcept (false);

} // namespace lis79

} // namespace dlisio

#endif // DLISIO_LIS_PROTOCOL_HPP
