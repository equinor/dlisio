#include <algorithm>
#include <array>
#include <cassert>
#include <cctype>
#include <ciso646>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include <dlisio/dlisio.hpp>
#include <dlisio/types.hpp>

namespace {

template <typename F>
bool is_sul_number_field_valid( const char* xs, F f) noexcept {
    /*
     * Check that following holds for the current string under xs:
     *
     * * it has zero or more leading spaces (as per isspace)
     * * it has 1 or more characters
     * * for all of them f returns True
     * * it ends with a \0 NUL-byte
     *
     * which means it takes C-strings, and the terminating 0 must be inserted
     * accordingly
     */
    if( !xs || *xs == '\0' ) return false;

    do {
        if( !std::isspace( *xs ) ) break;
    } while( *++xs );

    if( *xs == '\0' ) return false;

    do {
        if( !f( *xs ) ) break;
    } while( *++xs );

    while( *xs ){
        if( !std::isspace( *xs ) ) return false;
        ++xs;
    }

    return true;
}

bool is_zero_string( const char* xs ) noexcept {
    auto fn = [](char c) { return c == '0'; };
    return is_sul_number_field_valid(xs, fn);
}

bool is_number_string( const char* xs ) noexcept {
    auto fn = [](char c) { return std::isdigit(c); };
    return is_sul_number_field_valid(xs, fn);
}

int parse_revision( const char* rawin, int* major, int* minor ) {
    /*
     * The standard requires version numbers to be a non-zero-terminated
     * ASCII string on the format VN.mm where N is the major revision (1-9),
     * and mm is the minor revision 00, 01.. 99
     */

    /*
     * blazing if short string optimisation is enabled, but even if not then
     * accept the cost of std::string a one-off function
     */
    const std::string in( rawin, rawin + 5 );

    /*
     * V1.00 is probably the most common, so check for that before looking
     * for patterns
     */

    if( in == "V1.00" ) {
        *major = 1;
        *minor = 0;
        return dl::ERROR_OK;
    }

    /* Now look for well-formed, non-V1.00 versions */

    if(            'V' == in[ 0 ]
         && std::isdigit( in[ 1 ] )
         &&        '.' == in[ 2 ]
         && std::isdigit( in[ 3 ] )
         && std::isdigit( in[ 4 ] ) ) {
        *major =  in[ 1 ] - '0';
        *minor = (in[ 3 ] - '0') * 10
               + (in[ 4 ] - '0');
        return dl::ERROR_OK;
    }

    return dl::ERROR_UNEXPECTED_VALUE;

    /* Not formatted according to spec, try and figure something out anyway */
    // Case: formatted as int, mis-aligned?
    // Case: dropped leading V?
    // Case: dropped dot?
    // Case: drpoped minors?
}

/* hexdump -vCn 80 in.dlis v1
 * 000  20 20 20 31 56 31 2e 30  30 52 45 43 4f 52 44 20  |   1V1.00RECORD |
 * 010  38 31 39 32 44 65 66 61  75 6c 74 20 53 74 6f 72  |8192Default Stor|
 * 020  61 67 65 20 53 65 74 20  20 20 20 20 20 20 20 20  |age Set         |
 * 030  20 20 20 20 20 20 20 20  20 20 20 20 20 20 20 20  |                |
 * 040  20 20 20 20 20 20 20 20  20 20 20 20 20 20 20 20  |                |
 *
 * A well-formatted whitespace padded storage-unit-label for dlis v1. The
 * fields, with their respective sizes:
 *
 * Storage Unit Sequence Number  4
 * DLIS Version                  5
 * Storage Unit Structure        6
 * Maximum Record Length         5
 * Storage Set Identifier       60
 */

int sulv1( const char* xs,
           int* seqnum,
           std::int64_t* maxlen,
           int* layout,
           char* id ) noexcept {

    /*
     * read from the input record into a local zero'd buffer. Because the next
     * chunk is always longer than the last, there's no need to explicitly zero
     * in-between
     */
    std::array< char, 8 > buffer{{}};

    /*
     * If number parsing fails (atoi, atol), it returns 0, which on both these
     * cases is an invalid value (they're all defined to be >= 1), so any zero
     * is, at best, a protocol error, but most likely invalid tokens
     */

    std::copy_n( xs + 0, 4, std::begin( buffer ) );
    const auto seq = is_number_string(buffer.data()) ?
                        std::atoi( buffer.data() ) : -1;

    /* skip revision, already parsed and known to be V1.00 */

    /*
     * with 5 digits, maxlen can overflow ints on 16-bit int platforms, but
     * longs are good. The type of output maxlen is int64, however, because
     * later revisions can have huge records overflowing 32bit int
     * (theoretically), and this keeps the two revisions' maxlen uniform in
     * type.
     */
    std::copy_n( xs + 15, 5, std::begin( buffer ) );
    const auto len = is_number_string(buffer.data()) ?
                        std::atol( buffer.data() ) : -1;

    /*
     * In revision 1, only RECORD is a valid structure description, so just
     * check that
     */
    std::copy_n( xs + 9, 6, std::begin( buffer ) );
    const auto rec = std::equal( std::begin( buffer ),
                                 std::begin( buffer ) + 6,
                                 "RECORD" );

    /*
     * In theory, output values could always be set, and output-values of 0 as
     * "undefined" could be a part of the interface. However, that means
     * clients can't use their own values with confidence, and have weaker
     * exception guarantees
     */

    if( seqnum && seq > 0 ) *seqnum = seq;
    if( maxlen && len > 0 ) *maxlen = len;
    if( layout && rec )     *layout = dl::STRUCTURE_RECORD;
    if( id )                std::copy_n( xs + 20, 60, id );

    /* all good? */
    if( seq > 0 && len > 0 && rec ) return dl::ERROR_OK;

    /*
     * a max-length of 0 means "undefined upper limit", but is considered
     * valid. However, sequence-num and rec has to be >= 1 and RECORD/true
     * respectively, so if either of those are wrong, we're in inconsistent
     * territory
     *
     * Only report it as such if output params aren't nullptr, because if they
     * are, caller don't care if they're correct or not
     */
    if( seqnum && seq <= 0 ) return dl::ERROR_INCONSISTENT;
    if( maxlen && len < 0 )  return dl::ERROR_INCONSISTENT;
    if( layout && !rec )     return dl::ERROR_INCONSISTENT;

    /*
     * re-read the max-length and check if a correct[1] zero was input
     *
     * [1] correct in the sense it's accepted as explicit zero as input, which
     * includes any leading-spaces leading-zeros optionally-zero terminated
     * strings
     */
    if (maxlen && len == 0){
        std::copy_n( xs + 15, 5, std::begin( buffer ) );
        buffer[ 5 ] = '\0';
        if( !is_zero_string( buffer.data() ) )
            return dl::ERROR_INCONSISTENT;
        *maxlen = 0;
    }
    return dl::ERROR_OK;
}

} // namespace

namespace dl {

int sul( const char* xs,
         int* seqnum,
         int* major,
         int* minor,
         int* layout,
         std::int64_t* maxlen,
         char* id ) {
    /*
     * First, check for DLIS1, which means the Storage Unit Label is 80 bytes
     * long ASCII, and revision starts at byte 4
     */
    std::array< char, 5 > revision{{}};
    std::copy_n( xs + 4, 5, std::begin( revision ) );

    /* now parse the revision field */
    int vmajor = -1;
    int vminor = -1;
    auto err = parse_revision( revision.data(), &vmajor, &vminor );

    if( err == dl::ERROR_UNEXPECTED_VALUE ) {
        /*
         * version couldn't parse - this is probably either not a DLIS file or
         * it's increadibly corrupted or malformed, but try assuming revision 1
         * and see if the rest parses fine. If it's not a DLIS file, or it's
         * very corrupted, a new protocol violation probably shows up really
         * fast
         */

        vmajor = 1;
        vminor = 0;
    } else if( err != dl::ERROR_OK )
        return err;

    if( vmajor == 1 && vminor == 0 ) {
        *major = 1;
        *minor = 0;
        auto errv1 = sulv1( xs, seqnum, maxlen, layout, id );

        if( errv1 == dl::ERROR_OK && err == dl::ERROR_OK )
            return dl::ERROR_OK;

        return dl::ERROR_INCONSISTENT;
    }

    return dl::ERROR_UNEXPECTED_VALUE;
}

int find_sul(const char* from,
             long long search_limit,
             long long* offset) {

    static const auto needle = "RECORD";
    const auto to = from + search_limit;
    const auto itr = std::search(from, to, needle, needle + 6);

    if (itr == to)
        return dl::ERROR_NOTFOUND;

    /*
     * Before the structure field of the SUL there should be 9 bytes, i.e.
     * sequence-number and DLIS version.
     */
    const auto structure_offset = 9;
    if (std::distance(from, itr) < structure_offset)
        return dl::ERROR_INCONSISTENT;

    *offset = std::distance(from, itr - structure_offset);
    return dl::ERROR_OK;
}

int find_vrl(const char* from,
             long long search_limit,
             long long* offset) {
    /*
     * The first VRL does sometimes not immediately follow the SUL (or whatever
     * came before it), but according to spec it should be a triple of
     * (len,0xFF,0x01), where len is a UNORM. The second half shouldn't change,
     * so look for the first occurence of that.
     *
     * If that too doesn't work then the file is likely too corrupted to read
     * without manual intervention
     */

    /*
     * reinterpret the bytes as usigned char*. This is compatible and fine.
     *
     * When operator == is ued on the elements, they'll otherwise be promoted
     * to int, so all of a sudden (char)0xFF != (unsigned char)0xFF. Forcing
     * the pointer to be unsigend char fixes this issue.
     *
     * unsigned char is used because the needle includes 0xFF which is an
     * overflowing char literal
     */
    static const unsigned char needle[] = { 0xFF, 0x01 };
    const auto first = reinterpret_cast< const unsigned char* >(from);
    const auto last = first + search_limit;
    const auto itr = std::search(first, last, needle, needle + sizeof(needle));

    if (itr == last)
        return dl::ERROR_NOTFOUND;

    /*
     * Before the 0xFF 0x01 there should be room for at least an unorm
     */
    if (std::distance(first, itr) < dl::SIZEOF_UNORM)
        return dl::ERROR_INCONSISTENT;

    *offset = std::distance(first, itr - dl::SIZEOF_UNORM);
    return dl::ERROR_OK;
}

/*
 * hexdump -vn 12 tif
 * 0000000 00 00 00 00 00 00 00 00 5c 00 00 00
 *
 * Tapemarks are 12 byte long, constituted by three integers:
 * Type (0 or 1)                4
 * Offset of previous tapemark  4
 * Offset of next tapemark      4
 */

int tapemark(const char* buffer, int size) {
    if (size < 12)
        return dl::ERROR_INVALID_ARGS;

    std::uint32_t type;
    std::uint32_t prev;
    std::uint32_t next;

    #ifdef HOST_BIG_ENDIAN
        char tmp[ 12 ];
        std::memcpy(tmp, buffer, 12);

        std::reverse(tmp + 0, tmp + 4);
        std::reverse(tmp + 4, tmp + 8);
        std::reverse(tmp + 8, tmp + 12);

        buffer = tmp;
    #endif

    std::memcpy(&type, buffer + 0, 4);
    std::memcpy(&prev, buffer + 4, 4);
    std::memcpy(&next, buffer + 8, 4);

    if(not (type == 0 or type == 1))
        return dl::ERROR_NOTFOUND;

    if(next <= prev)
        return dl::ERROR_NOTFOUND;

    return dl::ERROR_OK;
}

/*
 * hexdump -vn 4 -s 80 dlis
 * 0000050 0020 01ff
 *
 * The visual record label is only 4 bytes long, all binary:
 * Visible record length    2
 * Padding/FF               1
 * Major version            1
 *
 * The length field is recorded in big-endian. It's a signed 16-bit integer
 * (uses an unsigned type, but the length of a record is limited to 16 384
 * bytes).
 *
 * RP66 requires the value of the padding to be FF (all bits set), but this is
 * not checked currently.
 *
 * The version is a single-byte integer, and should correspond to the major
 * DLIS revision.
 */
int vrl( const char* xs,
         int* length,
         int* version ) {

    std::uint16_t len;
    xs = dl::unorm_frombytes( xs, &len );
    /*
     * for now, ignore the ff. later, this might change the return value to
     * not-ok to flag protocol errors
     *  const auto ff    = dlis::ushort( xs + 2 );
     */
    //for now just advance pointer by 1
    ++xs;

    std::uint8_t major;
    dl::ushort_frombytes( xs, &major );

    *length = len;
    *version = major;
    return dl::ERROR_OK;
}

/*
 * hexdump -vn 4 -s 84 dlis
 * 0000054 7c00 0080
 *
 * The logical record segment header is metadata for the next segment, length,
 * attributes, and type, in total 4 bytes:
 *
 * Segment length 2
 * Attributes     1
 * Type           1
 *
 * The types 0-127 are reserved by the standard, 127-255 seems to be free to
 * use for vendor-specific purposes.
 */

int lrsh( const char* xs,
          int* seglen,
          uint8_t* attrs,
          int* type ) {
    std::uint16_t len;
    std::uint8_t attr;
    std::uint8_t typ;
    xs = dl::unorm_frombytes( xs, &len );
    xs = dl::ushort_frombytes( xs, &attr );
    dl::ushort_frombytes( xs, &typ );

    *seglen = len;
    *attrs = attr;
    *type = typ;

    return dl::ERROR_OK;
}

int segment_attributes( std::uint8_t attrs,
                        int* explicit_formatting,
                        int* has_predecessor,
                        int* has_successor,
                        int* is_encrypted,
                        int* has_encryption_packet,
                        int* has_checksum,
                        int* has_trailing_length,
                        int* has_padding ) {
    *explicit_formatting   = attrs & dl::SEGATTR_EXFMTLR;
    *has_predecessor       = attrs & dl::SEGATTR_PREDSEG;
    *has_successor         = attrs & dl::SEGATTR_SUCCSEG;
    *is_encrypted          = attrs & dl::SEGATTR_ENCRYPT;
    *has_encryption_packet = attrs & dl::SEGATTR_ENCRPKT;
    *has_checksum          = attrs & dl::SEGATTR_CHCKSUM;
    *has_trailing_length   = attrs & dl::SEGATTR_TRAILEN;
    *has_padding           = attrs & dl::SEGATTR_PADDING;
    return dl::ERROR_OK;
}

int encryption_packet_info( const char* xs,
                            int* len,
                            int* companycode ) {
    std::uint16_t ln, cc;
    xs = dl::unorm_frombytes( xs, &ln );
    dl::unorm_frombytes( xs, &cc );

    /*
     * RP66 rqeuires there to be at least 4 bytes, which means the actual
     * encryption packet itself is empty.
     */
    if( ln - 4 < 0 ) return dl::ERROR_INCONSISTENT;
    if( ln % 2 != 0 ) return dl::ERROR_UNEXPECTED_VALUE;

    *len = ln - 4;
    *companycode = cc;

    return dl::ERROR_OK;
}

int component( std::uint8_t comp, int* role ) {
    /* just extract the three high bits for role */
    *role = comp & (1 << 7 | 1 << 6 | 1 << 5);
    return dl::ERROR_OK;
}

int component_set( std::uint8_t desc, int role, int* type, int* name ) {
    switch( role ) {
        case dl::COMP_ROLE_RDSET:
        case dl::COMP_ROLE_RSET:
        case dl::COMP_ROLE_SET:
            break;

        default:
            return dl::ERROR_UNEXPECTED_VALUE;
    }

    *type = desc & (1 << 4);
    *name = desc & (1 << 3);

    return dl::ERROR_OK;
}

int component_object( std::uint8_t desc, int role, int* obname ) {
    if( role != dl::COMP_ROLE_OBJECT )
        return dl::ERROR_UNEXPECTED_VALUE;

    *obname = desc & (1 << 4);
    return dl::ERROR_OK;
}

int component_attrib( std::uint8_t desc,
                      int role,
                      int* label,
                      int* count,
                      int* reprc,
                      int* units,
                      int* value ) {
    switch( role ) {
        case dl::COMP_ROLE_ATTRIB:
        case dl::COMP_ROLE_INVATR:
            break;

        default:
            return dl::ERROR_UNEXPECTED_VALUE;
    }

    *label = desc & (1 << 4);
    *count = desc & (1 << 3);
    *reprc = desc & (1 << 2);
    *units = desc & (1 << 1);
    *value = desc & (1 << 0);

    return dl::ERROR_OK;
}

const char* component_str( int tag ) {
    switch( tag ) {
        case dl::COMP_ROLE_ABSATR: return "absent attribute";
        case dl::COMP_ROLE_ATTRIB: return "attribute";
        case dl::COMP_ROLE_INVATR: return "invariant attribute";
        case dl::COMP_ROLE_OBJECT: return "object";
        case dl::COMP_ROLE_RESERV: return "reserved";
        case dl::COMP_ROLE_RDSET:  return "redundant set";
        case dl::COMP_ROLE_RSET:   return "replacement set";
        case dl::COMP_ROLE_SET:    return "set";
        default:                   return "unknown";
    }
}

int trim_record_segment(uint8_t descriptor,
                        const char* begin,
                        const char* end,
                        int* size) {
    const auto dist = std::distance(begin, end);
    if (dist < 0) return dl::ERROR_INVALID_ARGS;

    int trim = 0;
    if (!(descriptor & dl::SEGATTR_ENCRYPT))
    {
        if (descriptor & dl::SEGATTR_CHCKSUM) trim += 2;
        if (descriptor & dl::SEGATTR_TRAILEN) trim += 2;
        if (descriptor & dl::SEGATTR_PADDING) {
            std::uint8_t pad_len = 0;
            dl::ushort_frombytes((end - 1) - trim, &pad_len);
            trim += pad_len;
        }
    }

    if (size)
        *size = trim;

    if (trim > dist)
        return dl::ERROR_BAD_SIZE;

    return dl::ERROR_OK;
}

} // namespace dl

namespace {

/*
 * The dl::packf function uses a dispatch table for interpreting and expanding
 * raw bytes into native C++ data types. There are 27 primary data types
 * specified by RP66 (Appendix B).
 *
 * Instead of populating the dispatch table by hand, generate it with the
 * interpret function. The interpret() function essentially generates this code
 * for all RP66 data types:
 *
 * float f;
 * src = dl::fsingl_frombytes( src, &f );
 * memcpy( dst, &f, 4 );
 * dst += 4;
 */

struct cursor {
    const char* src;
    char* dst;
    int written;

    void advance(int nbytes) noexcept (true) {
        if (this->dst) this->dst += nbytes;
        this->written += nbytes;
    }

    cursor& invalidate() noexcept (true) {
        this->src = nullptr;
        return *this;
    }

    bool invalid() const noexcept (true) {
        return !this->src;
    }
};

/*
 * Forward-declare the with-string overload so that all packs know to consider
 * it when recursing pack(dst, ptrs, ...)
 */
template < typename... Ts >
int pack(char* dst,
         const std::int32_t* len,
         const char* str,
         const Ts* ... ptrs) noexcept (true);

int pack(char*) noexcept (true) {
    return 0;
}

template < typename T, typename... Ts >
int pack(char* dst, const T* ptr, const Ts* ... ptrs) noexcept (true) {
    constexpr int size = sizeof(T);
    if (dst) {
        std::memcpy(dst, ptr, size);
        dst += size;
    }
    return size + pack(dst, ptrs ...);
}

template < typename... Ts >
int pack(char* dst,
         const std::int32_t* len,
         const char* str,
         const Ts* ... ptrs) noexcept (true)
{
    const auto size = sizeof(*len) + *len;
    if (dst) {
        std::memcpy(dst, len, sizeof(*len));
        std::memcpy(dst + sizeof(*len), str, *len);
        dst += size;
    }
    return size + pack(dst, ptrs ...);
}

using str = std::array< char, 256 >;

char* address( str& t ) noexcept (true) {
    return t.data();
}

template < typename T >
T* address( T& t ) noexcept (true) {
    return std::addressof( t );
}

template < typename T >
T init() noexcept (true) { return T(); }

template < >
str init< str >() noexcept (true) {
    /*
     * initialise a fresh object with {}, otherwise there are complaints on
     * missing-field-initializers when T is a std::array
     */
    return str {{}};
}

/*
 * Map char to std::array<char, 256> (max-len for ident and units), so
 * functions taking char* arguments get big-enough and initialised memory to
 * write to. All integral types just pass through
 */
template < typename T > struct bless { using type = T; };
template <> struct bless< char >     { using type = str; };

template < typename F, typename... Args >
cursor interpret( cursor cur, F func, Args ... args ) noexcept (true) {
    cur.src = func( cur.src, address( args ) ... );
    const auto written = pack(cur.dst, address( args ) ...);
    cur.advance(written);
    return cur;
}

template < typename... Args >
cursor interpret( cursor cur, const char* f(const char*, Args* ...) )
noexcept (true)
{
    /*
     * the inner-interpret takes pointers to initialised variables which serve
     * as buffers for func to write into, and pack to read from. It's
     * essentially creating a tuple< Args ... > by abusing function parameters
     * to statically create function calls with enough space on the stack, and
     * dispatch to the right function reference for the actual byte-to-variable
     * work
     */
    return interpret( cur, f, init< typename bless< Args >::type >() ... );
}

cursor packer(const char* fmt, const char* src, char* dst) noexcept (true) {
    /*
     * The public dl::packf function assumes both src and dst are valid
     * pointers, but the worker packer function has no such restriction. In
     * addition, dl::packflen is *essentially* dl::packf, but it outputs the
     * byte-count, instead of doing writes.
     *
     * This function implements both these operations
     */
    cursor cur = {src, dst, 0};

    std::vector< char > ascii;
    while (true) {
        switch (*fmt++) {
            case dl::FMT_EOL:
                return cur;

            case dl::FMT_FSHORT: cur = interpret(cur, dl::fshort_frombytes); break;
            case dl::FMT_FSINGL: cur = interpret(cur, dl::fsingl_frombytes); break;
            case dl::FMT_FSING1: cur = interpret(cur, dl::fsing1_frombytes); break;
            case dl::FMT_FSING2: cur = interpret(cur, dl::fsing2_frombytes); break;
            case dl::FMT_ISINGL: cur = interpret(cur, dl::isingl_frombytes); break;
            case dl::FMT_VSINGL: cur = interpret(cur, dl::vsingl_frombytes); break;
            case dl::FMT_FDOUBL: cur = interpret(cur, dl::fdoubl_frombytes); break;
            case dl::FMT_FDOUB1: cur = interpret(cur, dl::fdoub1_frombytes); break;
            case dl::FMT_FDOUB2: cur = interpret(cur, dl::fdoub2_frombytes); break;
            case dl::FMT_CSINGL: cur = interpret(cur, dl::csingl_frombytes); break;
            case dl::FMT_CDOUBL: cur = interpret(cur, dl::cdoubl_frombytes); break;
            case dl::FMT_SSHORT: cur = interpret(cur, dl::sshort_frombytes); break;
            case dl::FMT_SNORM:  cur = interpret(cur, dl::snorm_frombytes ); break;
            case dl::FMT_SLONG:  cur = interpret(cur, dl::slong_frombytes ); break;
            case dl::FMT_USHORT: cur = interpret(cur, dl::ushort_frombytes); break;
            case dl::FMT_UNORM:  cur = interpret(cur, dl::unorm_frombytes ); break;
            case dl::FMT_ULONG:  cur = interpret(cur, dl::ulong_frombytes ); break;
            case dl::FMT_UVARI:  cur = interpret(cur, dl::uvari_frombytes ); break;
            case dl::FMT_IDENT:  cur = interpret(cur, dl::ident_frombytes ); break;
            case dl::FMT_DTIME:  cur = interpret(cur, dl::dtime_frombytes ); break;
            case dl::FMT_ORIGIN: cur = interpret(cur, dl::origin_frombytes); break;
            case dl::FMT_OBNAME: cur = interpret(cur, dl::obname_frombytes); break;
            case dl::FMT_OBJREF: cur = interpret(cur, dl::objref_frombytes); break;
            case dl::FMT_ATTREF: cur = interpret(cur, dl::attref_frombytes); break;
            case dl::FMT_STATUS: cur = interpret(cur, dl::status_frombytes); break;
            case dl::FMT_UNITS:  cur = interpret(cur, dl::units_frombytes ); break;

            case dl::FMT_ASCII: {
                /*
                 * ascii is variable-length and practically unbounded, so it
                 * needs dynamic memory to be correct.
                 */
                std::int32_t len;
                dl::ascii_frombytes(cur.src, &len, nullptr);
                ascii.resize(len);
                cur.src = dl::ascii_frombytes(cur.src, &len, ascii.data());
                const auto written = pack(cur.dst, &len, ascii.data());
                cur.advance(written);
                break;
            }

            default:
                return cur.invalidate();
        }
    }
}

} // namespace

namespace dl {

int packf( const char* fmt, const void* src, void* dst ) {
    assert(src);
    assert(dst);

    auto csrc = static_cast< const char* >(src);
    auto cdst = static_cast< char* >(dst);
    const auto cur = packer(fmt, csrc, cdst);

    if (cur.invalid())
        return dl::ERROR_UNEXPECTED_VALUE;

    return dl::ERROR_OK;
}

int packflen(const char* fmt, const void* src, int* nread, int* nwrite) {
    auto csrc = static_cast< const char* >(src);
    const auto cur = packer(fmt, csrc, nullptr);

    if (cur.invalid())
        return dl::ERROR_UNEXPECTED_VALUE;

    if (nread)  *nread  = std::distance(csrc, cur.src);
    if (nwrite) *nwrite = cur.written;
    return dl::ERROR_OK;
}

int pack_varsize(const char* fmt, int* src, int* dst) {
    int srcvar = 0;
    while (true) {
        switch (*fmt++) {
            case dl::FMT_EOL:
                if (src) *src = srcvar;
                if (dst) *dst = 0;
                return dl::ERROR_OK;

            case dl::FMT_FSHORT:
            case dl::FMT_FSINGL:
            case dl::FMT_FSING1:
            case dl::FMT_FSING2:
            case dl::FMT_ISINGL:
            case dl::FMT_VSINGL:
            case dl::FMT_FDOUBL:
            case dl::FMT_FDOUB1:
            case dl::FMT_FDOUB2:
            case dl::FMT_CSINGL:
            case dl::FMT_CDOUBL:
            case dl::FMT_SSHORT:
            case dl::FMT_SNORM:
            case dl::FMT_SLONG:
            case dl::FMT_USHORT:
            case dl::FMT_UNORM:
            case dl::FMT_ULONG:
            case dl::FMT_DTIME:
            case dl::FMT_STATUS:
                break;

            case dl::FMT_ORIGIN:
            case dl::FMT_UVARI:
                srcvar = 1;
                break;

            case dl::FMT_IDENT:
            case dl::FMT_ASCII:
            case dl::FMT_OBNAME:
            case dl::FMT_OBJREF:
            case dl::FMT_ATTREF:
            case dl::FMT_UNITS:
                if (src) *src = 1;
                if (dst) *dst = 1;
                return dl::ERROR_OK;

            default:
                return dl::ERROR_INVALID_ARGS;
        }
    }
}

int pack_size(const char* fmt, int* src, int* dst) {
    bool varsrc = false;
    int correction = 0;
    int size = 0;
    while (true) {
        switch (*fmt++) {
            case dl::FMT_EOL:
                if (varsrc) correction = size;
                if (src) *src = size - correction;
                if (dst) *dst = size;
                return dl::ERROR_OK;

            case dl::FMT_FSHORT:
                correction += sizeof(float) - dl::SIZEOF_FSHORT;
                size += sizeof(float);
                break;

            case dl::FMT_DTIME:
                correction +=  8 * sizeof(int) - dl::SIZEOF_DTIME;
                size +=  8 * sizeof(int);
                break;

            case dl::FMT_FSINGL: size += dl::SIZEOF_FSINGL; break;
            case dl::FMT_FSING1: size += dl::SIZEOF_FSING1; break;
            case dl::FMT_FSING2: size += dl::SIZEOF_FSING2; break;
            case dl::FMT_ISINGL: size += dl::SIZEOF_ISINGL; break;
            case dl::FMT_VSINGL: size += dl::SIZEOF_VSINGL; break;
            case dl::FMT_FDOUBL: size += dl::SIZEOF_FDOUBL; break;
            case dl::FMT_FDOUB1: size += dl::SIZEOF_FDOUB1; break;
            case dl::FMT_FDOUB2: size += dl::SIZEOF_FDOUB2; break;
            case dl::FMT_CSINGL: size += dl::SIZEOF_CSINGL; break;
            case dl::FMT_CDOUBL: size += dl::SIZEOF_CDOUBL; break;
            case dl::FMT_SSHORT: size += dl::SIZEOF_SSHORT; break;
            case dl::FMT_SNORM:  size += dl::SIZEOF_SNORM;  break;
            case dl::FMT_SLONG:  size += dl::SIZEOF_SLONG;  break;
            case dl::FMT_USHORT: size += dl::SIZEOF_USHORT; break;
            case dl::FMT_UNORM:  size += dl::SIZEOF_UNORM;  break;
            case dl::FMT_ULONG:  size += dl::SIZEOF_ULONG;  break;
            case dl::FMT_STATUS: size += dl::SIZEOF_STATUS; break;

            case dl::FMT_ORIGIN:
            case dl::FMT_UVARI:
                varsrc = true;
                size += sizeof(std::int32_t);
                break;

            case dl::FMT_IDENT:
            case dl::FMT_ASCII:
            case dl::FMT_OBNAME:
            case dl::FMT_OBJREF:
            case dl::FMT_ATTREF:
            case dl::FMT_UNITS:
                return dl::ERROR_INCONSISTENT;

            default:
                return dl::ERROR_INVALID_ARGS;
        }
    }
}

int object_fingerprint_size(std::int32_t type_len,
                            const char*,
                            std::int32_t id_len,
                            const char*,
                            std::int32_t origin,
                            std::uint8_t copynum,
                            int* size) {

    if (origin < 0)    return dl::ERROR_INVALID_ARGS;
    if (type_len <= 0) return dl::ERROR_INVALID_ARGS;
    if (id_len < 0)    return dl::ERROR_INVALID_ARGS;

    const auto orig_len = std::to_string(origin).length();
    const auto copy_len = std::to_string(copynum).length();


    // each element, except the last one, add a constant 3 characters currently,
    // so return len*3 this might change in the future, and the contents of
    // type+id might matter, so keep the params around
    *size =  11 + type_len + id_len + orig_len + copy_len;
    return dl::ERROR_OK;
}

int object_fingerprint(std::int32_t type_len,
                       const char* type,
                       std::int32_t id_len,
                       const char* id,
                       std::int32_t origin,
                       std::uint8_t copynum,
                       char* fingerprint) {

    if (type_len <= 0) return dl::ERROR_INVALID_ARGS;
    if (id_len < 0)    return dl::ERROR_INVALID_ARGS;

    fingerprint = std::copy_n("T.", 2,        fingerprint);
    fingerprint = std::copy_n(type, type_len, fingerprint);
    fingerprint = std::copy_n("-",  1,        fingerprint);

    fingerprint = std::copy_n("I.", 2,      fingerprint);
    fingerprint = std::copy_n(id,   id_len, fingerprint);
    fingerprint = std::copy_n("-",  1,      fingerprint);

    // TODO: noexcept this?
    auto orig = std::to_string(origin);
    fingerprint = std::copy_n("O.", 2,      fingerprint);
    fingerprint = std::copy(orig.begin(), orig.end(), fingerprint);
    fingerprint = std::copy_n("-",  1,      fingerprint);

    auto copy = std::to_string(copynum);
    fingerprint = std::copy_n("C.", 2,      fingerprint);
                  std::copy(copy.begin(), copy.end(), fingerprint);

    return dl::ERROR_OK;
}

} // namespace dl
