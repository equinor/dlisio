#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <type_traits>

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

}


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

