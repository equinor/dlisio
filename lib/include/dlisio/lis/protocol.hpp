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
 * field attributes is undefined and unused by the LIS79 standard.
 *
 * spec ref: LIS79 ch 2.2.1.1
 */
struct lrheader {
    lis::byte    type;
    std::uint8_t attributes;

    static constexpr const int size = 2;
};

/** Read Logical Record Header
 *
 * Read and parse the next lis::lrheader::size bytes into a lis::lrheader
 * instance.
 */
lrheader read_lrh(const char* xs) noexcept (true);

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

    static constexpr const std::uint32_t rectype = 1 << 14;
    static constexpr const std::uint32_t chcksum = 1 << 13 | 1 << 12;
    static constexpr const std::uint32_t filenum = 1 << 10;
    static constexpr const std::uint32_t reconum = 1 << 9;
    static constexpr const std::uint32_t parierr = 1 << 6;
    static constexpr const std::uint32_t chckerr = 1 << 5;
    static constexpr const std::uint32_t predces = 1 << 1;
    static constexpr const std::uint32_t succses = 1 << 0;
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
 * Records. Because there is no hint if and how many pad-bytes are present, it
 * must be checked manually between each PR. This function checks if the next n
 * bytes of a buffer are all pad-bytes.
 *
 * Returns true if all bytes are pad-bytes, that is, all bytes are
 * either 0x20 or 0x00.
 */
bool is_padbytes(const char* xs, std::uint16_t n);

/** Record types
 *
 *  All valid record types defined by LIS79.
 */
enum class record_type : std::uint8_t {
    normal_data         = 0,
    alternate_data      = 1,
    job_identification  = 32,
    wellsite_data       = 34,
    tool_string_info    = 39,
    enc_table_dump      = 42,
    table_dump          = 47,
    data_format_spec    = 64,
    data_descriptor     = 65,
    tu10_software_boot  = 95,
    bootstrap_loader    = 96,
    cp_kernel_loader    = 97,
    prog_file_header    = 100,
    prog_overlay_header = 101,
    prog_overlay_load   = 102,
    file_header         = 128,
    file_trailer        = 129,
    tape_header         = 130,
    tape_trailer        = 131,
    reel_header         = 132,
    reel_trailer        = 133,
    logical_eof         = 137,
    logical_bot         = 138,
    logical_eot         = 139,
    logical_eom         = 141,
    op_command_inputs   = 224,
    op_response_inputs  = 225,
    system_outputs      = 227,
    flic_comment        = 232,
    blank_record        = 234,
    picture             = 85,
    image               = 86
};

/** Check if type is a valid LIS79 record type
 *
 * Return if the value of type is defined in lis::record_type, else returns
 * false.
 */
bool valid_rectype(lis::byte type);

std::string record_type_str( record_type ) noexcept (true);

/** (Logical) Record Info
 *
 * A Logical Record (LR) always starts on a new Physical Record (PR) and may
 * span multiple PR's. While each PR has its own header (PRH), the LR Header
 * (LRH) is only recorded once - At the start of the *first* PR.
 *
 * record_info is a lightweight representation of a Logical Record, containing
 * information needed in order to find and extract the content of the Logical
 * Record.
 */
struct record_info {
    lis::record_type type;  // From Logical Record Header
    std::size_t      size;  // Sum off all PRH length fields
    std::int64_t     ltell; // Logical offset to the *first* PR

    bool consistent = true; // TODO implement succ/pred check
};

/** Logical Record (LR)
 *
 * A raw buffer of the Logical Record. This buffer is a contiguous sequence of
 * all bytes that constitute the full [1] Logical Record, ready to be parsed.
 * That is:
 *
 *                   -----------------------------------------------
 * File on disk:    | PRH | data1 | PRH | data2 | PRT | PRH | data3 |
 *                   -----------------------------------------------
 *
 *                   -----------------------
 * record.data:     | data0 | data1 | data2 |
 *                   -----------------------
 *
 * [1] The Logical Record Header (LRH) is not part of the raw buffer, as it's
 *     part of the record_info. The parsed LRH provides clues to the contentent
 *     of the record through its type-field. Hence it makes sense to keep the
 *     parsed header seperate from the unparsed record.
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

// Data Format Specification Records

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
 * An Entry Block can be of one of the types defined in lis::entry_type. All
 * types are equally structured, but differ in semantic meaning. Often the mere
 * presence/absence of a given type has semantic meaning. Such behavior should
 * be enforced on a higher level, such as lis::dfsr
 *
 * spec ref: LIS79 ch 4.1.6
 */
struct entry_block {
    lis::byte type;
    lis::byte size;
    lis::byte reprc;

    value_type value;

    static constexpr const int fixed_size = 3;
};

entry_block read_entry_block(const record&, std::size_t) noexcept (false);

namespace detail {

struct spec_block {
    lis::string mnemonic;
    lis::string service_id;
    lis::string service_order_nr;
    lis::string units;
    lis::i16    filenr;
    lis::i16    reserved_size;
    lis::byte   samples;
    lis::byte   reprc;  // TODO: should be sanity-checked somewhere
};

} // namespace detail

/** Data Specification Block - subtype 0 (DSB0)
 */
struct spec_block0 : public detail::spec_block {
    lis::byte api_log_type;
    lis::byte api_curve_type;
    lis::byte api_curve_class;
    lis::byte api_modifier;
    lis::byte process_level;

    static constexpr const int size = 40;
};

/** Data Specification Block - subtype 1 (DSB1)
 */
struct spec_block1 : public detail::spec_block {
    lis::i32  api_codes;
    lis::mask process_indicators;

    static constexpr const int size = 40;
};

spec_block0 read_spec_block0(const record&, std::size_t) noexcept (false);
spec_block1 read_spec_block1(const record&, std::size_t) noexcept (false);

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
struct dfsr {
    record_info info;
    std::vector< entry_block >        entries;
    std::vector< detail::spec_block > specs;
};

dfsr parse_dfsr( const lis::record& ) noexcept (false);

std::string dfs_fmtstr( const dfsr& dfs ) noexcept (false);

// Information Records

struct component_block {
    lis::byte   type_nb;
    lis::byte   reprc;
    lis::byte   size;
    lis::byte   category; // Category is undefined by LIS79
    lis::string mnemonic; // Fixed size string (4 bytes)
    lis::string units;    // Fixed size string (4 bytes)

    value_type component;

    static constexpr const int fixed_size = 12;
};

component_block read_component_block(const record&, std::size_t)
noexcept (false);


namespace detail {

struct file_record {
    lis::string file_name;
    lis::string service_sublvl_name;
    lis::string version_number;
    lis::string date_of_generation;
    lis::string max_pr_length;
    lis::string file_type;
    lis::string optional_file_name;
};

} // namespace detail

struct file_header : public detail::file_record {
    lis::string prev_file_name;

    static constexpr const int size = 56;
};

struct file_trailer : public detail::file_record {
    lis::string next_file_name;

    static constexpr const int size = 56;
};

file_header  parse_file_header( const record& )  noexcept (false);
file_trailer parse_file_trailer( const record& ) noexcept (false);

namespace detail {

/* Common base for Reel/Tape Header/Trailer Records */
struct reel_tape_record {
    lis::string service_name;
    lis::string date;
    lis::string origin_of_data;
    lis::string name;
    lis::string continuation_number;
    lis::string comment;
};

} // namespace detail

struct reel_header : public detail::reel_tape_record {
    lis::string prev_reel_name;
    static constexpr const int size = 126;
};

struct reel_trailer : public detail::reel_tape_record {
    lis::string next_reel_name;
    static constexpr const int size = 126;
};

struct tape_header : public detail::reel_tape_record {
    lis::string prev_tape_name;
    static constexpr const int size = 126;
};

struct tape_trailer : public detail::reel_tape_record {
    lis::string next_tape_name;
    static constexpr const int size = 126;
};

reel_header  parse_reel_header(  const record& ) noexcept (false);
reel_trailer parse_reel_trailer( const record& ) noexcept (false);
tape_header  parse_tape_header(  const record& ) noexcept (false);
tape_trailer parse_tape_trailer( const record& ) noexcept (false);

} // namespace lis79

} // namespace dlisio

#endif // DLISIO_LIS_PROTOCOL_HPP
