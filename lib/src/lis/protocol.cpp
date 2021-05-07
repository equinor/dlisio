#include <cstdint>
#include <cstring>
#include <algorithm>
#include <cstring>
#include <type_traits>

#include <fmt/core.h>

#include <dlisio/exception.hpp>
#include <dlisio/lis/protocol.hpp>
#include <dlisio/lis/types.h>
#include <dlisio/lis/types.hpp>

namespace dlisio { namespace lis79 {
namespace lis = dlisio::lis79;

/* Definitions of static members

 * In C++11 static members need to be defined outside the class definition in
 * order to be odr-used [1]. These definitions can go away if we ever upgrade to
 * C++17 or higher.
 *
 * [1] https://en.cppreference.com/w/cpp/language/static
 */
constexpr const int lis::lrheader::size;
constexpr const int lis::prheader::size;
constexpr const int lis::spec_block0::size;
constexpr const int lis::spec_block1::size;
constexpr const int lis::entry_block::fixed_size;
constexpr const int lis::component_block::fixed_size;
constexpr const int lis::file_header::size;
constexpr const int lis::file_trailer::size;
constexpr const int lis::tape_header::size;
constexpr const int lis::tape_trailer::size;
constexpr const int lis::reel_header::size;
constexpr const int lis::reel_trailer::size;

bool is_padbytes(const char* xs, std::uint16_t size) {
    constexpr int PADBYTE_NULL  = 0x00;
    constexpr int PADBYTE_SPACE = 0x20;

    /* Calling this function with size=0 is nonsensical. We regard this special
     * case as: "In this buffer of zero bytes, there are no padbytes". So the
     * function returns false.
     */
    if (size == 0) return false;

    auto* cur = xs;
    char padfmt = *cur;
    if ( (padfmt != PADBYTE_NULL) and (padfmt != PADBYTE_SPACE) ) {
        return false;
    }

    while ( ++cur < xs + size ) {
        if (*cur != padfmt) return false;
    }

    return true;
}

lis::prheader read_prh(char* xs) noexcept (false) {
    char buffer[lis::prheader::size];
    std::memcpy(buffer, xs, prheader::size);

    #ifdef HOST_LITTLE_ENDIAN
        std::reverse(buffer + 0, buffer + 2);
        std::reverse(buffer + 2, buffer + 4);
    #endif

    lis::prheader head;
    std::memcpy(&head.length,      buffer + 0, sizeof(std::uint16_t));
    std::memcpy(&head.attributes,  buffer + 2, sizeof(std::uint16_t));
    return head;
}

lis::lrheader read_lrh(const char* xs) noexcept (true) {
    lis::lrheader head;

    std::memcpy(&head.type,       xs + 0, sizeof( std::uint8_t ));
    std::memcpy(&head.attributes, xs + 1, sizeof( std::uint8_t ));

    return head;
}

bool valid_rectype(lis::byte type) {
    const auto rectype = static_cast< lis::record_type >(lis::decay( type ));
    using rt = lis::record_type;

    switch (rectype) {
        case rt::normal_data:
        case rt::alternate_data:
        case rt::job_identification:
        case rt::wellsite_data:
        case rt::tool_string_info:
        case rt::enc_table_dump:
        case rt::table_dump:
        case rt::data_format_spec:
        case rt::data_descriptor:
        case rt::tu10_software_boot:
        case rt::bootstrap_loader:
        case rt::cp_kernel_loader:
        case rt::prog_file_header:
        case rt::prog_overlay_header:
        case rt::prog_overlay_load:
        case rt::file_header:
        case rt::file_trailer:
        case rt::tape_header:
        case rt::tape_trailer:
        case rt::reel_header:
        case rt::reel_trailer:
        case rt::logical_eof:
        case rt::logical_bot:
        case rt::logical_eot:
        case rt::logical_eom:
        case rt::op_command_inputs:
        case rt::op_response_inputs:
        case rt::system_outputs:
        case rt::flic_comment:
        case rt::blank_record:
        case rt::picture:
        case rt::image:
            return true;
        default:
            return false;
    }
}

std::string record_type_str( lis::record_type type ) noexcept (true) {
    using rt = lis::record_type;

    switch ( lis::decay(type) ) {
        case rt::normal_data:         return "Normal Data";
        case rt::alternate_data:      return "Alternate Data";
        case rt::job_identification:  return "Job Identification";
        case rt::wellsite_data:       return "Wellsite Data";
        case rt::tool_string_info:    return "Tool String Info";
        case rt::enc_table_dump:      return "Encrypted Table Dump";
        case rt::table_dump:          return "Table Dump";
        case rt::data_format_spec:    return "Data Format Specification";
        case rt::data_descriptor:     return "Data Descriptor";
        case rt::tu10_software_boot:  return "TU10 Software Boot";
        case rt::bootstrap_loader:    return "Bootstrap Loader";
        case rt::cp_kernel_loader:    return "CP-Kernel Loader Boot";
        case rt::prog_file_header:    return "Program File Header";
        case rt::prog_overlay_header: return "Program Overlay Header";
        case rt::prog_overlay_load:   return "Program Overlay Load";
        case rt::file_header:         return "File Header";
        case rt::file_trailer:        return "File Trailer";
        case rt::tape_header:         return "Tape Header";
        case rt::tape_trailer:        return "Tape Trailer";
        case rt::reel_header:         return "Reel Header";
        case rt::reel_trailer:        return "Reel Trailer";
        case rt::logical_eof:         return "Logical EOF";
        case rt::logical_bot:         return "Logical BOT";
        case rt::logical_eot:         return "Logical EOT";
        case rt::logical_eom:         return "Logical EOM";
        case rt::op_command_inputs:   return "Operator Command Inputs";
        case rt::op_response_inputs:  return "Operator Response Inputs";
        case rt::system_outputs:      return "System Outputs to Operator";
        case rt::flic_comment:        return "FLIC Comment";
        case rt::blank_record:        return "Blank Record/CSU Comment";
        case rt::picture:             return "Picture";
        case rt::image:               return "Image";
        default:
            return "Invalid LIS79 Record Type";
    }
}

namespace {

using std::swap;
const char* cast( const char* xs, lis::i8& i ) noexcept (true) {
    std::int8_t x;
    xs = lis_i8( xs, &x );

    lis::i8 tmp{ x };
    swap( i, tmp );

    return xs;
}

const char* cast( const char* xs, lis::i16& i ) noexcept (true) {
    std::int16_t x;
    xs = lis_i16( xs, &x );

    lis::i16 tmp{ x };
    swap( i, tmp );

    return xs;
}

const char* cast( const char* xs, lis::i32& i )
noexcept (true) {
    std::int32_t x;
    xs = lis_i32( xs, &x );

    lis::i32 tmp{ x };
    swap( i, tmp );

    return xs;
}

const char* cast( const char* xs, lis::f16& f )
noexcept (true) {
    float x;
    xs = lis_f16( xs, &x );
    f = lis::f16{ x };
    return xs;
}

const char* cast( const char* xs, lis::f32& f )
noexcept (true) {
    float x;
    xs = lis_f32( xs, &x );
    f = lis::f32{ x };
    return xs;
}

const char* cast( const char* xs, lis::f32low& f )
noexcept (true) {
    float x;
    xs = lis_f32low( xs, &x );
    f = lis::f32low{ x };
    return xs;
}

const char* cast( const char* xs, lis::f32fix& f )
noexcept (true) {
    float x;
    xs = lis_f32fix( xs, &x );
    f = lis::f32fix{ x };
    return xs;
}

/* string- or alphanumeric (reprc 65) is a bit special in that it doesn't
 * contain its own length. I don't see a nice way around this, other than to
 * break the cast's interface by adding length as a parameter.
 */
const char* cast(const char* xs, lis::string& s, std::int32_t len)
noexcept (true) {
    std::vector< char > str;
    str.resize( len );
    xs = lis_string( xs, len, str.data() );

    lis::string tmp{ std::string{ str.begin(), str.end() } };
    swap( s, tmp );
    return xs;
}

const char* cast( const char* xs, lis::byte& i )
noexcept (true) {
    std::uint8_t x;
    xs = lis_byte( xs, &x );

    lis::byte tmp{ x };
    swap( tmp, i );
    return xs;
}

const char* cast(const char* xs, lis::mask& s, std::int32_t len)
noexcept (true) {
    std::vector< char > str;
    str.resize( len );
    xs = lis_mask( xs, len, str.data() );

    lis::mask tmp{ std::string{ str.begin(), str.end() } };
    swap( s, tmp );
    return xs;
}

template < typename T >
const char* extract( const char* xs, T& val )
noexcept (false) {
    xs = cast( xs, val );
    return xs;
}

template < typename T, typename U>
const char* extract( const char* xs, T& val, U size )
noexcept (false) {
    const auto sz = lis::decay( size );
    xs = cast( xs, val, sz );
    return xs;
}

template < typename T >
T& reset( lis::value_type& value ) noexcept (false) {
    return value.emplace< T >();
}

template < typename T >
const char* element( const char* xs,
                     T size,
                     lis::byte reprc,
                     lis::value_type& val )
noexcept (false) {
    auto repr = static_cast< lis::representation_code>( lis::decay(reprc) );
    using rpc = lis::representation_code;
    switch (repr) {
        case rpc::i8 :    return extract( xs, reset< lis::i8     >(val) );
        case rpc::i16:    return extract( xs, reset< lis::i16    >(val) );
        case rpc::i32:    return extract( xs, reset< lis::i32    >(val) );
        case rpc::f16:    return extract( xs, reset< lis::f16    >(val) );
        case rpc::f32:    return extract( xs, reset< lis::f32    >(val) );
        case rpc::f32low: return extract( xs, reset< lis::f32low >(val) );
        case rpc::f32fix: return extract( xs, reset< lis::f32fix >(val) );
        case rpc::string: return extract( xs, reset< lis::string >(val), size );
        case rpc::byte:   return extract( xs, reset< lis::byte   >(val) );
        case rpc::mask:   return extract( xs, reset< lis::mask   >(val), size );
        default: {
            const auto msg = "unable to interpret attribute: "
                             "unknown representation code {}";
            const auto code = lis::decay(reprc);
            throw std::runtime_error(fmt::format(msg, code));
        }
    }

    return xs;
}

void validate_entry( const lis::entry_block& entry ) {
    const auto type = lis::decay(entry.type);
    if ( type > int(lis::entry_type::spec_bloc_subtype) ) {
        const auto msg = "lis::validate_entry: unknown entry type {}";
        throw std::runtime_error( fmt::format(msg, type) );
    }

    const auto size = lis::decay(entry.size);

    const auto reprc = lis::decay(entry.reprc);
    const auto reprc_size = lis_sizeof_type(reprc);

    if ( reprc_size < 0 ) {
        // will fail with invalid repcode even if entry size is 0.
        // possible to reconsider if such file ever seen in reality
        const auto msg = "lis::validate_entry: unknown representation code {} "
                         "for entry (type: {})";
        const auto code = lis::decay(reprc);
        throw std::runtime_error(fmt::format(msg, code, type));
    }

    if (size != reprc_size and size > 0 and reprc_size != LIS_VARIABLE_LENGTH) {
        const auto msg = "lis::validate_entry: invalid entry (type: {}). "
                         "Expected size for reprc {} is {}, was {}";
        throw std::runtime_error( fmt::format(msg, type, reprc, reprc_size,
                                              size) );
    }

}

} // namespace

lis::entry_block read_entry_block( const lis::record& rec, std::size_t offset )
noexcept (false) {
    const auto* cur = rec.data.data() + offset;
    const auto* end = rec.data.data() + rec.data.size();

    if ( std::distance(cur, end) < lis::entry_block::fixed_size ) {
        const auto msg = "lis::entry_block: "
                         "{} bytes left in record, expected at least {}";
        const auto left = std::distance(cur, end);
        throw std::runtime_error( fmt::format(
                    msg, left, lis::entry_block::fixed_size) );
    }

    lis::entry_block entry;

    cur = cast( cur, entry.type  );
    cur = cast( cur, entry.size  );
    cur = cast( cur, entry.reprc );

    validate_entry(entry);

    if ( std::distance(cur, end) < lis::decay( entry.size ) ) {
        const auto msg = "lis::entry_block: "
                         "{} bytes left in record, expected at least {}";
        const auto left = std::distance(cur, end);
        throw std::runtime_error(fmt::format(msg, left, lis::decay(entry.size)));
    }

    if ( lis::decay(entry.size) != 0 )
        element(cur, entry.size, entry.reprc, entry.value);

    return entry;
}

namespace {

/* Visitor for lis::value_type
 *
 * Check if the _value_ held by the variant equals "val", regardless of the
 * type held by the variant. It follows normal C++ comparison rules
 * between different numeric types.
 */
struct contains_numeric_value {
    explicit contains_numeric_value( float val ) : val(val) {};

    template <
        typename T,
        typename std::enable_if<
            std::is_arithmetic< typename T::value_type >::value>::type* = nullptr
    >
    bool operator()( const T& x ) const noexcept (true) {
        return val == lis::decay(x);
    }

    template < typename T >
    bool operator ()( T&& ) const noexcept (true) {
        return false;
    }

private:
    float val;
};

bool contains_numeric( const lis::value_type& x, float val )
noexcept (false) {
    return mpark::visit(contains_numeric_value{val}, x);
}

template < typename T >
void read_spec_block( const char* cur, const char* end, T& spec )
noexcept (false) {

    if ( std::distance(cur, end) < T::size ) {
        const auto msg = "lis::spec_block: "
                         "{} bytes left in record, expected at least {}";
        const auto left = std::distance(cur, end);
        throw std::runtime_error(fmt::format(msg, left, T::size));
    }

    constexpr int padbyte = 1;

    cur = cast( cur, spec.mnemonic,         4 );
    cur = cast( cur, spec.service_id,       6 );
    cur = cast( cur, spec.service_order_nr, 8 );
    cur = cast( cur, spec.units,            4 );
    cur += 4;                       // Skip subtype-specific fields
    cur = cast( cur, spec.filenr );
    cur = cast( cur, spec.reserved_size );
    cur += (2*padbyte);             // Skip padding
    cur += 1;                       // Skip subtype-specific fields
    cur = cast( cur, spec.samples );
    cast( cur, spec.reprc );
}

} // namespace

spec_block0 read_spec_block0(const record& rec, std::size_t offset) noexcept (false) {
    const auto* cur = rec.data.data() + offset;
    const auto* end = rec.data.data() + rec.data.size();

    lis::spec_block0 spec;
    read_spec_block(cur, end, spec);

    /* Skip to API codes */
    cur += 22;
    cur = cast( cur, spec.api_log_type    );
    cur = cast( cur, spec.api_curve_type  );
    cur = cast( cur, spec.api_curve_class );
    cur = cast( cur, spec.api_modifier    );

    /* Skip to process level */
    cur += 6;
    cast( cur, spec.process_level );

    return spec;
}

spec_block1 read_spec_block1(const record& rec, std::size_t offset) noexcept (false) {
    const auto* cur = rec.data.data() + offset;
    const auto* end = rec.data.data() + rec.data.size();

    lis::spec_block1 spec;
    read_spec_block(cur, end, spec);

    /* Skip to API codes */
    cur += 22;
    cur = cast( cur, spec.api_codes );

    /* Skip to process_indicators */
    cur += 9;
    cast( cur, spec.process_indicators, 5 );

    return spec;
}

lis::dfsr parse_dfsr( const lis::record& rec ) noexcept (false) {
    lis::dfsr formatspec;
    formatspec.info = rec.info; //carry over the header information of the record

    int subtype = 0;
    std::size_t offset = 0;

    while (true) {
        const auto entry = read_entry_block(rec, offset);
        const auto type  = static_cast< lis::entry_type >(lis::decay(entry.type));

        if ( type == lis::entry_type::spec_bloc_subtype ) {
            if ( contains_numeric( entry.value, 1 ) ) {
                subtype = 1;
            }
        }

        offset += lis::entry_block::fixed_size + lis::decay(entry.size);
        formatspec.entries.push_back( std::move(entry) );

        if ( type == lis::entry_type::terminator )
            break;
    }

    while ( offset < rec.data.size() ) {
        if (subtype == 0) {
            formatspec.specs.emplace_back( read_spec_block0(rec, offset) );
            offset += lis::spec_block0::size;
        } else {
            formatspec.specs.emplace_back( read_spec_block1(rec, offset) );
            offset += lis::spec_block1::size;
        }
    }

    return formatspec;
}
process_indicators::process_indicators( const lis::mask& mask ) {
    constexpr std::size_t MASK_SIZE = 5;

    if ( lis::decay(mask).size() != MASK_SIZE ) {
        throw std::runtime_error("Invalid mask length");
    }

    unsigned char buffer[ MASK_SIZE ];
    std::memcpy( buffer, lis::decay(mask).data(), MASK_SIZE );

    /* Mask out fields                 byte       bit */
    true_vertical_depth_correction = buffer[0] & 1 << 5;
    data_channel_not_on_depth      = buffer[0] & 1 << 4;
    data_channel_is_filtered       = buffer[0] & 1 << 3;
    data_channel_is_calibrated     = buffer[0] & 1 << 2;
    computed                       = buffer[0] & 1 << 1;
    derived                        = buffer[0] & 1 << 0;
    tool_defined_correction_nb_2   = buffer[1] & 1 << 7;
    tool_defined_correction_nb_1   = buffer[1] & 1 << 6;
    mudcake_correction             = buffer[1] & 1 << 5;
    lithology_correction           = buffer[1] & 1 << 4;
    inclinometry_correction        = buffer[1] & 1 << 3;
    pressure_correction            = buffer[1] & 1 << 2;
    hole_size_correction           = buffer[1] & 1 << 1;
    temperature_correction         = buffer[1] & 1 << 0;
    auxiliary_data_flag            = buffer[2] & 1 << 1;
    schlumberger_proprietary       = buffer[2] & 1 << 0;

    original_logging_direction = (buffer[0] & (1 << 7 | 1 << 6)) >> 6;
}

namespace {

void validate_component( const lis::component_block& component ) {
    const auto type = lis::decay(component.type_nb);
    /* For now consider only 0, 69 and 73 to be valid, but note that Customer
     * Tape Subset Appendix G (A) identifies values 1-4 in addition.
     */
    switch (type) {
        case 0 :
        case 69:
        case 73:
            break;
        default: {
            const auto mnem = lis::decay(component.mnemonic);
            const auto msg = "lis::validate_component: unknown component type {} "
                             "in component {}";
            throw std::runtime_error( fmt::format(msg, type, mnem) );
        }
    }

    const auto size = lis::decay(component.size);

    const auto reprc = lis::decay(component.reprc);
    const auto reprc_size = lis_sizeof_type(reprc);

    if ( reprc_size < 0 ) {
        // will fail with invalid repcode even if entry size is 0.
        // possible to reconsider if such file ever seen in reality
        const auto msg = "lis::validate_component: unknown representation code {} "
                         "in component {}";
        const auto mnem = lis::decay(component.mnemonic);
        const auto code = lis::decay(reprc);
        throw std::runtime_error(fmt::format(msg, code, mnem));
    }

    if (size != reprc_size and size > 0 and reprc_size != LIS_VARIABLE_LENGTH) {
        const auto msg =
            "lis::validate_component: invalid component (mnem: {}). "
            "Expected size for reprc {} is {}, was {}";
        const auto mnem = lis::decay(component.mnemonic);
        throw std::runtime_error(fmt::format(msg, mnem, reprc, reprc_size, size));
    }
}

} // namespace

lis::component_block read_component_block( const lis::record& rec, std::size_t offset )
noexcept (false) {
    const auto* cur = rec.data.data() + offset;
    const auto* end = rec.data.data() + rec.data.size();

    if ( std::distance(cur, end) < lis::component_block::fixed_size ) {
        const auto msg = "lis::component_block: "
                         "{} bytes left in record, expected at least {}";
        const auto left = std::distance(cur, end);
        throw std::runtime_error( fmt::format(
                    msg, left, lis::component_block::fixed_size) );
    }

    lis::component_block component;

    cur = cast( cur, component.type_nb );
    cur = cast( cur, component.reprc );
    cur = cast( cur, component.size );
    cur = cast( cur, component.category );
    cur = cast( cur, component.mnemonic, 4 );
    cur = cast( cur, component.units, 4 );

    validate_component(component);

    if ( std::distance(cur, end) < lis::decay( component.size ) ) {
        const auto msg = "lis::component_block: "
                         "{} bytes left in record, expected at least {}";
        const auto left = std::distance(cur, end);
        throw std::runtime_error(fmt::format(msg, left, lis::decay(component.size)));
    }

    if ( lis::decay(component.size) != 0 )
        element(cur, component.size, component.reprc, component.component);

    return component;
}

information_record parse_info_record( const lis::record& rec )
noexcept (false) {
    lis::information_record inforec;
    inforec.info = rec.info; //carry over the header information of the record

    std::size_t offset = 0;
    while ( offset < rec.data.size() ) {
        const auto component = read_component_block(rec, offset);
        offset += lis::component_block::fixed_size + lis::decay(component.size);
        inforec.components.push_back( std::move(component) );
    }

    return inforec;
}

text_record parse_text_record( const lis::record& raw)
noexcept (false) {
    const auto type = static_cast< lis::record_type >(lis::decay(raw.info.type));
    if ( not (type == lis::record_type::op_command_inputs or
              type == lis::record_type::op_response_inputs or
              type == lis::record_type::system_outputs or
              type == lis::record_type::flic_comment) ) {

        const auto type = lis::decay(raw.info.type);
        const auto type_str = lis::record_type_str(raw.info.type);
        const auto msg = "parse_text_record: Invalid record type, {} ({})";
        throw std::runtime_error(fmt::format(msg, type, type_str));
    }
    lis::text_record rec;
    rec.type = raw.info.type;
    cast(raw.data.data(), rec.message, raw.data.size());

    return rec;
}

namespace {

void parse_name( const char* cur, lis::file_header& rec ) {
    cast(cur, rec.prev_file_name, 10);
}

void parse_name( const char* cur, lis::file_trailer& rec) {
    cast(cur, rec.next_file_name, 10);
}

template< typename T >
void parse_file_record( const record& raw, T& rec ) noexcept (false) {
    if ( not (raw.info.type == lis::record_type::file_header or
              raw.info.type == lis::record_type::file_trailer) ) {

        const auto type = lis::decay(raw.info.type);
        const auto type_str = lis::record_type_str(raw.info.type);
        const auto msg = "parse_file_record: Invalid record type, {} ({})";
        throw std::runtime_error(fmt::format(msg, type, type_str));
    }

    if ( raw.data.size() < T::size ) {
        //TODO log when too many bytes
        const auto type_str = lis::record_type_str(raw.info.type);
        const auto msg = "parse_file_record: Unable to parse record, "
                         "{} Records are {} bytes, raw record is only {}";
        throw std::runtime_error(
                fmt::format(msg, type_str, T::size, raw.data.size()) );
    }

    constexpr int BLANK = 1;
    const auto* cur = raw.data.data();

    cur = cast(cur, rec.file_name, 10);
    cur += 2 * BLANK;
    cur = cast(cur, rec.service_sublvl_name, 6 );
    cur = cast(cur, rec.version_number     , 8 );
    cur = cast(cur, rec.date_of_generation , 8 );
    cur += 1 * BLANK;
    cur = cast(cur, rec.max_pr_length, 5 );
    cur += 2 * BLANK;
    cur = cast(cur, rec.file_type, 2 );
    cur += 2 * BLANK;
    parse_name(cur, rec);
}

} // namespace

file_header parse_file_header( const record& raw ) {
    lis::file_header fileheader;
    parse_file_record( raw, fileheader );
    return fileheader;
}

file_trailer parse_file_trailer( const record& raw ) {
    lis::file_trailer filetrailer;
    parse_file_record( raw, filetrailer );
    return filetrailer;
}

namespace {

const char* parse_name( const char* cur, lis::reel_header& rec ) {
    return cast(cur, rec.prev_reel_name, 8);
}

const char* parse_name( const char* cur, lis::reel_trailer& rec ) {
    return cast(cur, rec.next_reel_name, 8);
}

const char* parse_name( const char* cur, lis::tape_header& rec ) {
    return cast(cur, rec.prev_tape_name, 8);
}

const char* parse_name( const char* cur, lis::tape_trailer& rec ) {
    return cast(cur, rec.next_tape_name, 8);
}

template< typename T >
void parse_reel_tape_record( const record& raw, T& rec ) {
    const auto type = static_cast< lis::record_type >(lis::decay(raw.info.type));
    if ( not (type == lis::record_type::reel_header or
              type == lis::record_type::reel_trailer or
              type == lis::record_type::tape_header or
              type == lis::record_type::tape_trailer) ) {

        const auto type = lis::decay(raw.info.type);
        const auto type_str = lis::record_type_str(raw.info.type);
        const auto msg = "parse_reel_tape_record: Invalid record type, {} ({})";
        throw std::runtime_error(fmt::format(msg, type, type_str));
    }

    if ( raw.data.size() < T::size ) {
        //TODO log when too many bytes
        const auto msg = "Unable to parse record. "
                         "Expected {} bytes, raw record is only {}";
        throw std::runtime_error(fmt::format(msg, T::size, raw.data.size()));
    }

    constexpr int BLANK = 1;
    const auto* cur = raw.data.data();

    cur = cast(cur, rec.service_name, 6);
    cur += 6 * BLANK;
    cur = cast(cur, rec.date, 8);
    cur += 2 * BLANK;
    cur = cast(cur, rec.origin_of_data, 4);
    cur += 2 * BLANK;
    cur = cast(cur, rec.name, 8);
    cur += 2 * BLANK;
    cur = cast(cur, rec.continuation_number, 2);
    cur += 2 * BLANK;
    cur = parse_name(cur, rec);
    cur += 2 * BLANK;
    cast(cur, rec.comment, 74);
}

} // namespace

tape_header parse_tape_header( const record& raw ) {
    lis::tape_header tapeheader;
    parse_reel_tape_record( raw, tapeheader );
    return tapeheader;
}

tape_trailer parse_tape_trailer( const record& raw ) {
    lis::tape_trailer tapetrailer;
    parse_reel_tape_record( raw, tapetrailer );
    return tapetrailer;
}

reel_header parse_reel_header( const record& raw ) {
    lis::reel_header reelheader;
    parse_reel_tape_record( raw, reelheader );
    return reelheader;
}

reel_trailer parse_reel_trailer( const record& raw ) {
    lis::reel_trailer reeltrailer;
    parse_reel_tape_record( raw, reeltrailer );
    return reeltrailer;
}

} // namespace lis79

} // namespace dlisio
