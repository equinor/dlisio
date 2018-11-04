#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <string>

#include <dlisio/dlisio.h>
#include <dlisio/types.h>

namespace {

/*
 * Until the scope of network <-> host transformation is known, just copy the
 * implementation into the test program to avoid hassle with linking winsock
 */
#ifdef HOST_BIG_ENDIAN

template< typename T > T hton( T value ) noexcept { return value; }
template< typename T > T ntoh( T value ) noexcept { return value; }

#else

template< typename T >
typename std::enable_if< sizeof(T) == 1, T >::type
hton( T value ) noexcept {
    return value;
}

template< typename T >
typename std::enable_if< sizeof(T) == 2, T >::type
hton( T value ) noexcept {
    std::uint16_t v;
    std::memcpy( &v, &value, sizeof( T ) );
    v = ((v & 0x00FF) << 8)
      | ((v & 0xFF00) >> 8)
      ;
    std::memcpy( &value, &v, sizeof( T ) );
    return value;
}

template< typename T >
typename std::enable_if< sizeof(T) == 4, T >::type
hton( T value ) noexcept {
    std::uint32_t v;
    std::memcpy( &v, &value, sizeof( T ) );
    v = ((v & 0x000000FF) << 24)
      | ((v & 0x0000FF00) <<  8)
      | ((v & 0x00FF0000) >>  8)
      | ((v & 0xFF000000) >> 24)
      ;
    std::memcpy( &value, &v, sizeof( T ) );
    return value;
}

template< typename T >
typename std::enable_if< sizeof(T) == 8, T >::type
hton( T value ) noexcept {
    std::uint64_t v;
    std::memcpy( &v, &value, sizeof( T ) );
    v = ((v & 0xFF00000000000000ull) >> 56)
      | ((v & 0x00FF000000000000ull) >> 40)
      | ((v & 0x0000FF0000000000ull) >> 24)
      | ((v & 0x000000FF00000000ull) >>  8)
      | ((v & 0x00000000FF000000ull) <<  8)
      | ((v & 0x0000000000FF0000ull) << 24)
      | ((v & 0x000000000000FF00ull) << 40)
      | ((v & 0x00000000000000FFull) << 56)
      ;
    std::memcpy( &value, &v, sizeof( T ) );
    return value;
}

// preserve the ntoh name for symmetry
template< typename T >
T ntoh( T value ) noexcept {
    return hton( value );
}

#endif

bool is_zero_string( const char* xs ) noexcept {
    /*
     * check if a a string legitimately produced zero as output. If so, then
     * the following holds:
     *
     * * it has zero or more leading spaces (as per isspace)
     * * it has 1 or more zeros
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
        if( *xs != '0' ) return false;
    } while( *++xs );

    return true;
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
        return DLIS_OK;
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
        return DLIS_OK;
    }

    return DLIS_UNEXPECTED_VALUE;

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
    const auto seq = std::atoi( buffer.data() );

    /* skip revision, already parsed and known to be V1.00 */

    /*
     * with 5 digits, maxlen can overflow ints on 16-bit int platforms, but
     * longs are good. The type of output maxlen is int64, however, because
     * later revisions can have huge records overflowing 32bit int
     * (theoretically), and this keeps the two revisions' maxlen uniform in
     * type.
     */
    std::copy_n( xs + 15, 5, std::begin( buffer ) );
    const auto len = std::atol( buffer.data() );

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
    if( layout && rec )     *layout = DLIS_STRUCTURE_RECORD;
    if( id )                std::copy_n( xs + 20, 60, id );

    /* all good? */
    if( seq > 0 && len > 0 && rec ) return DLIS_OK;

    /*
     * a max-length of 0 means "undefined upper limit", but is considered
     * valid. However, sequence-num and rec has to be >= 1 and RECORD/true
     * respectively, so if either of those are wrong, we're in inconsistent
     * territory
     *
     * Only report it as such if output params aren't nullptr, because if they
     * are, caller don't care if they're correct or not
     */
    if( seqnum && seq <= 0 ) return DLIS_INCONSISTENT;
    if( layout && !rec )     return DLIS_INCONSISTENT;

    /*
     * re-read the max-length and check if a correct[1] zero was input
     *
     * [1] correct in the sense it's accepted as explicit zero as input, which
     * includes any leading-spaces leading-zeros optionally-zero terminated
     * strings
     */
    std::copy_n( xs + 15, 5, std::begin( buffer ) );
    buffer[ 5 ] = '\0';
    if( !is_zero_string( buffer.data() ) )
        return DLIS_INCONSISTENT;

    if( maxlen ) *maxlen = 0;
    return DLIS_OK;
}

namespace dlis {

std::uint8_t ushort( const char* xs ) noexcept {
    std::uint8_t x;
    std::memcpy( &x, xs, sizeof( x ) );
    return x;
}

std::uint16_t unorm( const char* xs ) noexcept {
    std::uint16_t x;
    std::memcpy( &x, xs, sizeof( x ) );
    return ntoh( x );
}

}

}

int dlis_sul( const char* xs,
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

    if( err == DLIS_UNEXPECTED_VALUE ) {
        /*
         * version couldn't parse - this is probably either not a DLIS file or
         * it's increadibly corrupted or malformed, but try assuming revision 1
         * and see if the rest parses fine. If it's not a DLIS file, or it's
         * very corrupted, a new protocol violation probably shows up really
         * fast
         */

        vmajor = 1;
        vminor = 0;
    } else if( err != DLIS_OK )
        return err;

    if( vmajor == 1 && vminor == 0 ) {
        *major = 1;
        *minor = 0;
        auto errv1 = sulv1( xs, seqnum, maxlen, layout, id );

        if( errv1 == DLIS_OK && err == DLIS_OK )
            return DLIS_OK;

        return DLIS_INCONSISTENT;
    }

    return DLIS_UNEXPECTED_VALUE;
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
int dlis_vrl( const char* xs,
              int* length,
              int* version ) {
    const auto len   = dlis::unorm( xs );
    /*
     * for now, ignore the ff. later, this might change the return value to
     * not-ok to flag protocol errors
     *  const auto ff    = dlis::ushort( xs + 2 );
     */
    const auto major = dlis::ushort( xs + 3 );

    *length = len;
    *version = major;
    return DLIS_OK;
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

int dlis_lrsh( const char* xs,
               int* seglen,
               uint8_t* attrs,
               int* type ) {
    auto len = dlis::unorm( xs );
    auto atr = dlis::ushort( xs + 2 );
    auto typ = dlis::ushort( xs + 3 );

    *seglen = len;
    *attrs = atr;
    *type = typ;

    return 0;
}

int dlis_segment_attributes( std::uint8_t attrs,
                             int* explicit_formatting,
                             int* has_predecessor,
                             int* has_successor,
                             int* is_encrypted,
                             int* has_encryption_packet,
                             int* has_checksum,
                             int* has_trailing_length,
                             int* has_padding ) {
    *explicit_formatting   = attrs & DLIS_SEGATTR_EXFMTLR;
    *has_predecessor       = attrs & DLIS_SEGATTR_PREDSEG;
    *has_successor         = attrs & DLIS_SEGATTR_SUCCSEG;
    *is_encrypted          = attrs & DLIS_SEGATTR_ENCRYPT;
    *has_encryption_packet = attrs & DLIS_SEGATTR_ENCRPKT;
    *has_checksum          = attrs & DLIS_SEGATTR_CHCKSUM;
    *has_trailing_length   = attrs & DLIS_SEGATTR_TRAILEN;
    *has_padding           = attrs & DLIS_SEGATTR_PADDING;
    return DLIS_OK;
}

int dlis_encryption_packet_info( const char* xs,
                                 int* len,
                                 int* companycode ) {
    const int ln = dlis::unorm( xs );
    const int cc = dlis::unorm( xs + 2 );

    /*
     * RP66 rqeuires there to be at least 4 bytes, which means the actual
     * encryption packet itself is empty.
     */
    if( ln - 4 < 0 ) return DLIS_INCONSISTENT;
    if( ln % 2 != 0 ) return DLIS_UNEXPECTED_VALUE;

    *len = ln - 4;
    *companycode = cc;

    return DLIS_OK;
}

int dlis_component( std::uint8_t comp, int* role ) {
    /* just extract the three high bits for role */
    *role = comp & (1 << 7 | 1 << 6 | 1 << 5);
    return DLIS_OK;
}

int dlis_component_set( std::uint8_t desc, int role, int* type, int* name ) {
    switch( role ) {
        case DLIS_ROLE_RDSET:
        case DLIS_ROLE_RSET:
        case DLIS_ROLE_SET:
            break;

        default:
            return DLIS_UNEXPECTED_VALUE;
    }

    *type = desc & (1 << 4);
    *name = desc & (1 << 3);

    if( !*type ) return DLIS_INCONSISTENT;
    return DLIS_OK;
}

int dlis_component_object( std::uint8_t desc, int role, int* obname ) {
    if( role != DLIS_ROLE_OBJECT ) return DLIS_UNEXPECTED_VALUE;

    *obname = desc & (1 << 4);
    if( !*obname ) return DLIS_INCONSISTENT;
    return DLIS_OK;
}

int dlis_component_attrib( std::uint8_t desc,
                           int role,
                           int* label,
                           int* count,
                           int* reprc,
                           int* units,
                           int* value ) {
    switch( role ) {
        case DLIS_ROLE_ATTRIB:
        case DLIS_ROLE_INVATR:
            break;

        default:
            return DLIS_UNEXPECTED_VALUE;
    }

    *label = desc & (1 << 4);
    *count = desc & (1 << 3);
    *reprc = desc & (1 << 2);
    *units = desc & (1 << 1);
    *value = desc & (1 << 0);

    return DLIS_OK;
}

const char* dlis_component_str( int tag ) {
    switch( tag ) {
        case DLIS_ROLE_ABSATR: return "absent attribute";
        case DLIS_ROLE_ATTRIB: return "attribute";
        case DLIS_ROLE_INVATR: return "invariant attribute";
        case DLIS_ROLE_OBJECT: return "object";
        case DLIS_ROLE_RESERV: return "reserved";
        case DLIS_ROLE_RDSET:  return "redundant set";
        case DLIS_ROLE_RSET:   return "replacement set";
        case DLIS_ROLE_SET:    return "set";
        default:               return "unknown";
    }
}

/* TYPES */

const char* dlis_sshort( const char* xs, std::int8_t* x ) {
    /* assume two's complement platform - insert check to support */
    std::memcpy( x, xs, sizeof( std::int8_t ) );
    return xs + sizeof( std::int8_t );
}

const char* dlis_snorm( const char* xs, std::int16_t* x ) {
    std::uint16_t ux;
    std::memcpy( &ux, xs, sizeof( std::int16_t ) );
    ux = ntoh( ux );
    std::memcpy( x, &ux, sizeof( std::int16_t ) );
    return xs + sizeof( std::int16_t );
}

const char* dlis_slong( const char* xs, std::int32_t* x ) {
    std::uint32_t ux;
    std::memcpy( &ux, xs, sizeof( std::int32_t ) );
    ux = ntoh( ux );
    std::memcpy( x, &ux, sizeof( std::int32_t ) );
    return xs + sizeof( std::int32_t );
}

const char* dlis_ushort( const char* xs, std::uint8_t* x ) {
    std::memcpy( x, xs, sizeof( std::uint8_t ) );
    return xs + sizeof( std::uint8_t );
}

const char* dlis_unorm( const char* xs, std::uint16_t* x ) {
    std::memcpy( x, xs, sizeof( std::uint16_t ) );
    *x = ntoh( *x );
    return xs + sizeof( std::uint16_t );
}

const char* dlis_ulong( const char* xs, std::uint32_t* x ) {
    std::memcpy( x, xs, sizeof( std::uint32_t ) );
    *x = ntoh( *x );
    return xs + sizeof( std::uint32_t );
}

const char* dlis_uvari( const char* xs, int32_t* out ) {
    /*
     * extract the two high bits. (length-encoding)
     * 0x: 1-byte
     * 10: 2-byte
     * 11: 4-byte
     */
    const std::uint8_t high = xs[ 0 ] & 0xC0; // b11000000

    int len = 0;
    switch( high ) {
        case 0xC0: len = 4; break; // 11
        case 0x80: len = 2; break; // 10
        default:   len = 1; break; // 0x
    }

    auto i32 = []( const char* in ) {
        std::uint32_t x = 0;
        std::memcpy( &x, in, sizeof( std::uint32_t ) );
        x = ntoh( x ) & 0x3FFFFFFF;
        return x;
    };

    auto i16 = []( const char* in ) {
        std::uint16_t x = 0;
        std::memcpy( &x, in, sizeof( std::uint16_t ) );
        x = ntoh( x ) & 0x3FFF;
        return x;
    };

    auto i8 = []( const char* in ) {
        std::uint8_t x = 0;
        std::memcpy( &x, in, sizeof( std::int8_t ) );
        return x;
    };

    /*
     * blank out the length encoding if multi-byte, and byteswap as needed
     *
     * no point blanking out in single-byte, because only one bit contributes
     * (the leading zero) and we might lose information, and the leading two
     * zeroes in 2-4 byte uints are effectively zero anyway
     *
     * unsigned -> signed conversion won't overflow, because of the zero'd
     * leading bits
     *
     * 0x3F = b00111111
     *
     */
    switch( len ) {
        case 4:  *out = i32( xs ); break;
        case 2:  *out = i16( xs ); break;
        default: *out =  i8( xs ); break;
    }

    return xs + len;
}

const char* dlis_ident( const char* xs, std::int32_t* len, char* out ) {
    std::uint8_t ln;
    xs = dlis_ushort( xs, &ln );

    if( len ) *len = ln;
    if( out ) std::memcpy( out, xs, ln );
    return xs + ln;
}

const char* dlis_ascii( const char* xs, std::int32_t* len, char* out ) {
    std::int32_t ln;
    xs = dlis_uvari( xs, &ln );

    if( len ) *len = ln;
    if( out ) std::memcpy( out, xs, ln );
    return xs + ln;
}

int dlis_year( int Y ) {
    return Y + DLIS_YEAR_ZERO;
}

const char* dlis_dtime( const char* xs, int* Y,
                                        int* TZ,
                                        int* M,
                                        int* D,
                                        int* H,
                                        int* MN,
                                        int* S,
                                        int* MS ) {
    std::uint8_t x[ 6 ];
    std::memcpy( x, xs, sizeof( x ) );
    *Y  = x[ 0 ];
    *D  = x[ 2 ];
    *H  = x[ 3 ];
    *MN = x[ 4 ];
    *S  = x[ 5 ];

    /*
     * TZ is a half-byte enumeration in the upper 4 bits:
     * 2^3 2^2 2^1 2^0
     *  1   1   1   1
     *
     * So it must be shifted after masking the upper 4 bits to be interepreted
     * as its proper range (0, 1, 2)
     */
    *TZ = (x[ 1 ] & 0xF0) >> 4;
    *M  =  x[ 1 ] & 0x0F;

    xs += sizeof( x );

    std::uint16_t ms;
    std::memcpy( &ms, xs, sizeof( ms ) );
    *MS = ntoh( ms );

    return xs + sizeof( ms );
}

const char* dlis_origin( const char* xs, std::int32_t* out ) {
    return dlis_uvari( xs, out );
}

const char* dlis_obname( const char* xs, std::int32_t* origin,
                                         std::uint8_t* copy_number,
                                         std::int32_t* idlen,
                                         char* identifier ) {
    xs = dlis_origin( xs, origin );
    xs = dlis_ushort( xs, copy_number );
    return dlis_ident( xs, idlen, identifier );
}

const char* dlis_objref( const char* xs, int32_t* ident_len,
                                         char* ident,
                                         int32_t* origin,
                                         uint8_t* copy_number,
                                         int32_t* objname_len,
                                         char* identifier ) {
    xs = dlis_ident( xs, ident_len, ident );
    return dlis_obname( xs, origin, copy_number, objname_len, identifier );
}

const char* dlis_fshort( const char* xs, float* out ) {
    std::uint16_t v;
    const char* newptr = dlis_unorm( xs, &v );

    std::uint16_t sign_bit = v & 0x8000;
    std::uint16_t exp_bits = v & 0x000F;
    std::uint16_t frac_bits = (v & 0xFFF0) >> 4;
    if( sign_bit )
        frac_bits = (~frac_bits & 0x0FFF) + 1;

    float sign = sign_bit ? -1.0 : 1.0;
    float exponent = float( exp_bits );
    float fractional = frac_bits / float( 0x0800 );

    *out = sign * fractional * std::pow( 2.0f, exponent );
    return newptr;
}

const char* dlis_fsingl( const char* xs, float* out ) {
    static_assert(
        std::numeric_limits< float >::is_iec559 && sizeof( float ) == 4,
        "Function assumes IEEE 754 32-bit float" );

    std::memcpy( out, xs, sizeof( float ) );
    *out = ntoh( *out );
    return xs + sizeof( float );
}

const char* dlis_fdoubl( const char* xs, double* out ) {
    static_assert(
        std::numeric_limits< double >::is_iec559 && sizeof( double ) == 8,
        "Function assumes IEEE 754 64-bit float" );

    std::memcpy( out, xs, sizeof( double ) );
    *out = ntoh( *out );
    return xs + sizeof( double );
}

const char* dlis_isingl( const char* xs, float* out ) {
    static const std::uint32_t ieeemax = 0x7FFFFFFF;
    static const std::uint32_t iemaxib = 0x611FFFFF;
    static const std::uint32_t ieminib = 0x21200000;

    static const std::uint32_t it[8] = {
        0x21800000, 0x21400000, 0x21000000, 0x21000000,
        0x20c00000, 0x20c00000, 0x20c00000, 0x20c00000 };
    static const std::uint32_t mt[8] = { 8, 4, 2, 2, 1, 1, 1, 1 };
    std::uint32_t manthi, iexp, inabs;
    std::uint32_t ix;
    std::uint32_t u;

    std::memcpy( &u, xs, sizeof( std::uint32_t ) );
    u = ntoh( u );

    manthi = u & 0X00FFFFFF;
    ix     = manthi >> 21;
    iexp   = ( ( u & 0x7f000000 ) - it[ix] ) << 1;
    manthi = manthi * mt[ix] + iexp;
    inabs  = u & 0X7FFFFFFF;
    if ( inabs > iemaxib ) manthi = ieeemax;
    manthi = manthi | ( u & 0x80000000 );
    u = ( inabs < ieminib ) ? 0 : manthi;

    std::memcpy( out, &u, sizeof( std::uint32_t ) );
    return xs + sizeof( std::uint32_t );
}

const char* dlis_vsingl( const char* xs, float* out ) {
    std::uint8_t x[4];
    std::memcpy( &x, xs, 4 );

    std::uint32_t v = std::uint32_t(x[1]) << 24
                    | std::uint32_t(x[0]) << 16
                    | std::uint32_t(x[3]) << 8
                    | std::uint32_t(x[2]) << 0
                    ;

    std::uint32_t sign_bit = v & 0x80000000;
    std::uint32_t frac_bits = v & 0x007FFFFF;
    std::uint32_t exp_bits = (v & 0x7F800000) >> 23;

    float sign = sign_bit ? -1.0 : 1.0;
    float exponent = float( exp_bits );
    float significand = frac_bits / float( 0x00800000 );

    if (exp_bits)
        *out = sign * (0.5 + significand) * std::pow(2.0f, exponent - 128.0f);
    else if (!sign_bit)
        *out = 0;
    else
        *out = std::nanf("");

    return xs + sizeof( std::uint32_t );
}

const char* dlis_fsing1( const char* xs, float* V, float* A ) {
    const char* ys = dlis_fsingl( xs, V );
    const char* zs = dlis_fsingl( ys, A );
    return zs;
}

const char* dlis_fsing2( const char* xs, float* V, float* A, float* B ) {
    const char* ys = dlis_fsingl( xs, V );
    const char* zs = dlis_fsingl( ys, A );
    const char* ws = dlis_fsingl( zs, B );
    return ws;
}

const char* dlis_csingl( const char* xs, float* R, float* I ) {
    const char* ys = dlis_fsingl( xs, R );
    const char* zs = dlis_fsingl( ys, I );
    return zs;
}

const char* dlis_fdoub1( const char* xs, double* V, double* A ) {
    const char* ys = dlis_fdoubl( xs, V );
    const char* zs = dlis_fdoubl( ys, A );
    return zs;
}

const char* dlis_fdoub2( const char* xs, double* V, double* A, double* B ) {
    const char* ys = dlis_fdoubl( xs, V );
    const char* zs = dlis_fdoubl( ys, A );
    const char* ws = dlis_fdoubl( zs, B );
    return ws;
}

const char* dlis_cdoubl( const char* xs, double* R, double* I ) {
    const char* ys = dlis_fdoubl( xs, R );
    const char* zs = dlis_fdoubl( ys, I );
    return zs;
}

const char* dlis_status( const char* xs, std::uint8_t* x ) {
    return dlis_ushort( xs, x );
}
