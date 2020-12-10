#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <type_traits>

#include <endianness/endianness.h>

#include <dlisio/types.hpp>

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
    v = bswap16( v );
    std::memcpy( &value, &v, sizeof( T ) );
    return value;
}

template< typename T >
typename std::enable_if< sizeof(T) == 4, T >::type
hton( T value ) noexcept {
    std::uint32_t v;
    std::memcpy( &v, &value, sizeof( T ) );
    v = bswap32( v );
    std::memcpy( &value, &v, sizeof( T ) );
    return value;
}

template< typename T >
typename std::enable_if< sizeof(T) == 8, T >::type
hton( T value ) noexcept {
    std::uint64_t v;
    std::memcpy( &v, &value, sizeof( T ) );
    v = bswap64( v );
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

namespace dl {

const char* sshort_frombytes( const char* xs, std::int8_t* x ) {
    /* assume two's complement platform - insert check to support */
    std::memcpy( x, xs, sizeof( std::int8_t ) );
    return xs + sizeof( std::int8_t );
}

const char* snorm_frombytes( const char* xs, std::int16_t* x ) {
    std::uint16_t ux;
    std::memcpy( &ux, xs, sizeof( std::int16_t ) );
    ux = ntoh( ux );
    std::memcpy( x, &ux, sizeof( std::int16_t ) );
    return xs + sizeof( std::int16_t );
}

const char* slong_frombytes( const char* xs, std::int32_t* x ) {
    std::uint32_t ux;
    std::memcpy( &ux, xs, sizeof( std::int32_t ) );
    ux = ntoh( ux );
    std::memcpy( x, &ux, sizeof( std::int32_t ) );
    return xs + sizeof( std::int32_t );
}

const char* ushort_frombytes( const char* xs, std::uint8_t* x ) {
    std::memcpy( x, xs, sizeof( std::uint8_t ) );
    return xs + sizeof( std::uint8_t );
}

const char* unorm_frombytes( const char* xs, std::uint16_t* x ) {
    std::memcpy( x, xs, sizeof( std::uint16_t ) );
    *x = ntoh( *x );
    return xs + sizeof( std::uint16_t );
}

const char* ulong_frombytes( const char* xs, std::uint32_t* x ) {
    std::memcpy( x, xs, sizeof( std::uint32_t ) );
    *x = ntoh( *x );
    return xs + sizeof( std::uint32_t );
}

const char* uvari_frombytes( const char* xs, std::int32_t* out ) {
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

const char* ident_frombytes( const char* xs, std::int32_t* len, char* out ) {
    std::uint8_t ln;
    xs = ushort_frombytes( xs, &ln );

    if( len ) *len = ln;
    if( out ) std::memcpy( out, xs, ln );
    return xs + ln;
}

const char* ascii_frombytes( const char* xs, std::int32_t* len, char* out ) {
    std::int32_t ln;
    xs = uvari_frombytes( xs, &ln );

    if( len ) *len = ln;
    if( out ) std::memcpy( out, xs, ln );
    return xs + ln;
}

const char* dtime_frombytes( const char* xs, int* Y,
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

const char* origin_frombytes( const char* xs, std::int32_t* out ) {
    return uvari_frombytes( xs, out );
}

const char* obname_frombytes( const char* xs, std::int32_t* origin,
                                              std::uint8_t* copy_number,
                                              std::int32_t* idlen,
                                              char* identifier ) {
    xs = origin_frombytes( xs, origin );
    xs = ushort_frombytes( xs, copy_number );
    return ident_frombytes( xs, idlen, identifier );
}

const char* objref_frombytes( const char* xs, std::int32_t* ident_len,
                                              char* ident,
                                              std::int32_t* origin,
                                              std::uint8_t* copy_number,
                                              std::int32_t* objname_len,
                                              char* identifier ) {
    xs = ident_frombytes( xs, ident_len, ident );
    return obname_frombytes( xs, origin, copy_number, objname_len, identifier );
}

const char* attref_frombytes( const char* xs, std::int32_t* ident_len,
                                              char* ident,
                                              std::int32_t* origin,
                                              std::uint8_t* copy_number,
                                              std::int32_t* objname_len,
                                              char* identifier,
                                              std::int32_t* ident2_len,
                                              char* ident2 ) {
    xs = ident_frombytes( xs, ident_len, ident );
    xs = obname_frombytes( xs, origin, copy_number, objname_len, identifier );
    return ident_frombytes( xs, ident2_len, ident2 );
}

const char* fshort_frombytes( const char* xs, float* out ) {
    std::uint16_t v;
    const char* newptr = unorm_frombytes( xs, &v );

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

const char* fsingl_frombytes( const char* xs, float* out ) {
    static_assert(
        std::numeric_limits< float >::is_iec559 && sizeof( float ) == 4,
        "Function assumes IEEE 754 32-bit float" );

    std::memcpy( out, xs, sizeof( float ) );
    *out = ntoh( *out );
    return xs + sizeof( float );
}

const char* fdoubl_frombytes( const char* xs, double* out ) {
    static_assert(
        std::numeric_limits< double >::is_iec559 && sizeof( double ) == 8,
        "Function assumes IEEE 754 64-bit float" );

    std::memcpy( out, xs, sizeof( double ) );
    *out = ntoh( *out );
    return xs + sizeof( double );
}

const char* isingl_frombytes( const char* xs, float* out ) {
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

const char* vsingl_frombytes( const char* xs, float* out ) {
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
    float exponent = float( exp_bits ) - 128.0f;

    /* VAX floats have a 24 bit normalized mantissa where the MSB is hidden.
     * That is, the normalized mantissa takes the form 0.1m where m is the 23
     * bits on disk, and 1 is the hidden bit that is _not_ present on disk [1].
     *
     * This is similar to the 24 bit normalized mantissa of the IEEE 754 float,
     * but the difference being that IEEE float defines the hidden bit before
     * the point (1.m).
     *
     * The implicit hidden bit must be explicitly masked in before calculating
     * the value of the mantissa.
     *
     * [1] https://pubs.usgs.gov/of/2005/1424/of2005-1424_v1.2.pdf
     */

    float significand = (float)(frac_bits | 0x00800000) / std::pow(2.0f, 24);

    if (exp_bits)
        *out = sign * significand * std::pow(2.0f, exponent);
    else if (!sign_bit)
        /* Unlike a IEEE 754 float there is no denormalized form in VAX floats.
         * if e=0, s=0  -> v = 0, or if e=0, s=1 -> v = undefined
         */
        *out = 0;
    else
        *out = std::nanf("");

    return xs + sizeof( std::uint32_t );
}

const char* fsing1_frombytes( const char* xs, float* V, float* A ) {
    const char* ys = fsingl_frombytes( xs, V );
    const char* zs = fsingl_frombytes( ys, A );
    return zs;
}

const char* fsing2_frombytes( const char* xs, float* V, float* A, float* B ) {
    const char* ys = fsingl_frombytes( xs, V );
    const char* zs = fsingl_frombytes( ys, A );
    const char* ws = fsingl_frombytes( zs, B );
    return ws;
}

const char* csingl_frombytes( const char* xs, float* R, float* I ) {
    const char* ys = fsingl_frombytes( xs, R );
    const char* zs = fsingl_frombytes( ys, I );
    return zs;
}

const char* fdoub1_frombytes( const char* xs, double* V, double* A ) {
    const char* ys = fdoubl_frombytes( xs, V );
    const char* zs = fdoubl_frombytes( ys, A );
    return zs;
}

const char* fdoub2_frombytes( const char* xs, double* V, double* A, double* B ) {
    const char* ys = fdoubl_frombytes( xs, V );
    const char* zs = fdoubl_frombytes( ys, A );
    const char* ws = fdoubl_frombytes( zs, B );
    return ws;
}

const char* cdoubl_frombytes( const char* xs, double* R, double* I ) {
    const char* ys = fdoubl_frombytes( xs, R );
    const char* zs = fdoubl_frombytes( ys, I );
    return zs;
}

const char* status_frombytes( const char* xs, std::uint8_t* x ) {
    return ushort_frombytes( xs, x );
}

const char* units_frombytes( const char* xs, std::int32_t* len, char* out ) {
    std::uint8_t ln;
    xs = ushort_frombytes( xs, &ln );

    if( len ) *len = ln;
    if( out ) std::memcpy( out, xs, ln );
    return xs + ln;
}

/*
 * output functions
 */

void* sshort_tobytes( void* xs, std::int8_t x ) {
    return ushort_tobytes( xs, x );
}

void* snorm_tobytes( void* xs, std::int16_t x ) {
    return unorm_tobytes( xs, x );
}

void* slong_tobytes( void* xs, std::int32_t x ) {
    return ulong_tobytes( xs, x );
}

void* ushort_tobytes( void* xs, std::uint8_t x ) {
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );
}

void* unorm_tobytes( void* xs, std::uint16_t x ) {
    x = hton( x );
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );;
}

void* ulong_tobytes( void* xs, std::uint32_t x ) {
    x = hton( x );
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );
}

void* fsingl_tobytes( void* xs, float x ) {
    x = hton( x );
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );
}

void* fdoubl_tobytes( void* xs, double x ) {
    x = hton( x );
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );
}

void* isingl_tobytes( void* xs, float x ) {
    static int it[4] = { 0x21200000, 0x21400000, 0x21800000, 0x22100000 };
    static int mt[4] = { 2, 4, 8, 1 };
    unsigned int manthi, iexp, ix;
    std::uint32_t u;

    memcpy( &u, &x, sizeof( u ) );

    ix     = ( u & 0x01800000 ) >> 23;
    iexp   = ( ( u & 0x7e000000 ) >> 1 ) + it[ix];
    manthi = ( mt[ix] * ( u & 0x007fffff) ) >> 3;
    manthi = ( manthi + iexp ) | ( u & 0x80000000 );
    u      = ( u & 0x7fffffff ) ? manthi : 0;

    u = hton( u );
    memcpy( xs, &u, sizeof( u ) );
    return (char*)xs + sizeof( x );
}

void* vsingl_tobytes( void* xs, float x ) {
    std::uint32_t u;
    std::memcpy( &u, &x, sizeof( x ) );

    std::uint32_t sign_bit = (u & 0x80000000);
    std::uint32_t exp_bits = (u & 0x7F800000) >> 23;
    std::uint32_t frac_bits = (u & 0x007FFFFF);

    if( !exp_bits ){
        std::uint32_t zeros = 0;
        std::memcpy( xs, &zeros, sizeof( std::uint32_t ) );
        return (char*)xs + sizeof( std::uint32_t );
    }

    exp_bits += 2;
    exp_bits = exp_bits << 23;
    std::uint32_t v = sign_bit | exp_bits | frac_bits;

    std::uint32_t w[ 4 ];
    w[ 0 ] = ( v & 0x00FF0000 ) << 8;
    w[ 1 ] = ( v & 0xFF000000 ) >> 8;
    w[ 2 ] = ( v & 0x000000FF ) << 8;
    w[ 3 ] = ( v & 0x0000FF00 ) >> 8;
    std::uint32_t z = w[ 0 ] | w[ 1 ]| w[ 2 ] | w[ 3 ];

    z = hton( z );
    std::memcpy( xs, &z, sizeof( v ) );
    return (char*)xs + sizeof( v );
}

void* fsing1_tobytes( void* xs, float v, float a ) {
    void* ys = fsingl_tobytes( xs, v );
    void* zs = fsingl_tobytes( ys, a );
    return zs;
}

void* fsing2_tobytes( void* xs, float V, float A, float B ) {
    void* ys = fsingl_tobytes( xs, V );
    void* zs = fsingl_tobytes( ys, A );
    void* ws = fsingl_tobytes( zs, B );
    return ws;
}

void* csingl_tobytes( void* xs, float R, float I ) {
    void* ys = fsingl_tobytes( xs, R );
    void* zs = fsingl_tobytes( ys, I );
    return zs;
}

void* fdoub1_tobytes( void* xs, double V, double A ) {
    void* ys = fdoubl_tobytes( xs, V );
    void* zs = fdoubl_tobytes( ys, A );
    return zs;
}

void* fdoub2_tobytes( void* xs, double V, double A, double B ) {
    void* ys = fdoubl_tobytes( xs, V );
    void* zs = fdoubl_tobytes( ys, A );
    void* ws = fdoubl_tobytes( zs, B );
    return ws;
}

void* cdoubl_tobytes( void* xs, double R, double I ) {
    void* ys = fdoubl_tobytes( xs, R );
    void* zs = fdoubl_tobytes( ys, I );
    return zs;
}

void* uvari_tobytes( void* xs, std::int32_t x, int width ) {
    if( x <= 0x7F && width <= 1 ) {
        std::int8_t v = x;
        std::memcpy( xs, &v, sizeof( v ) );
        return (char*)xs + sizeof( v );
    }

    if( x <= 0xBFFF && width <= 2 ) {
        std::uint16_t v = x;
        v |= 0x8000;
        v = hton( v );
        std::memcpy( xs, &v, sizeof( v ) );
        return (char*)xs + sizeof( v );
    }

    std::int32_t v = x;
    v |= 0xC0000000;
    v = hton( v );
    std::memcpy( xs, &v, sizeof( v ) );
    return (char*)xs + sizeof( v );
}

void* ident_tobytes( void* xs, std::uint8_t len, const char* in ) {
    void* ys = ushort_tobytes( xs, len );
    std::memcpy( ys, in, (size_t)len );
    return (char*)ys + len;
}

void* ascii_tobytes( void* xs, std::int32_t len,
                             const char* in,
                             std::uint8_t l ) {
    void* ys = uvari_tobytes( xs, len, l );
    std::memcpy( ys, in, (size_t)len );
    return (char*)ys + len;
}

void* origin_tobytes( void* xs, std::int32_t x ) {
    return uvari_tobytes( xs, x, 4 );
}

void* status_tobytes( void* xs, std::uint8_t x ) {
    return ushort_tobytes( xs, x );
}

void* dtime_tobytes( void* xs, int Y,
                               int TZ,
                               int M,
                               int D,
                               int H,
                               int MN,
                               int S,
                               int MS ) {

    // OBS: no overflow protection
    std::uint8_t tz = TZ;
    std::uint8_t m = M;

    std::uint8_t x[ 6 ];
    x[ 0 ] = Y;
    x[ 1 ] = tz << 4 | m;
    x[ 2 ] = D;
    x[ 3 ] = H;
    x[ 4 ] = MN;
    x[ 5 ] = S;

    std::memcpy( xs, &x, sizeof( x ) );
    void* ys = (char*)xs + sizeof( x );

    std::uint16_t ms = MS;
    ms = ntoh( ms );
    std::memcpy( ys, &ms, sizeof( ms ) );
    return (char*)ys + sizeof( ms );
}

void* obname_tobytes( void* xs, std::int32_t origin,
                                std::uint8_t copy_number,
                                std::uint8_t idlen,
                                const char* identifier ) {
    void* ys = origin_tobytes( xs, origin );
    void* zs = ushort_tobytes( ys, copy_number );
    void* ws = ident_tobytes( zs, idlen, identifier );
    return ws;
}

void* objref_tobytes( void* xs, std::uint8_t ident_len,
                                const char* ident,
                                std::int32_t origin,
                                std::uint8_t copy_number,
                                std::uint8_t objname_len,
                                const char* identifier ) {

    void* ys = ident_tobytes( xs, ident_len, ident );
    void* zs = obname_tobytes( ys, origin,
                                   copy_number,
                                   objname_len,
                                   identifier );
    return zs;
}

void* attref_tobytes( void* xs, std::uint8_t ident1_len,
                                const char* ident1,
                                std::int32_t origin,
                                std::uint8_t copy_number,
                                std::uint8_t objname_len,
                                const char* identifier,
                                std::uint8_t ident2_len,
                                const char* ident2 ) {

    void* ys = ident_tobytes( xs, ident1_len, ident1 );
    void* zs = obname_tobytes( ys, origin,
                                   copy_number,
                                   objname_len,
                                   identifier );

    void* ws = ident_tobytes( zs, ident2_len, ident2 );
    return ws;
}

void* units_tobytes( void* xs, std::uint8_t len, const char* in ) {
    void* ys = ushort_tobytes( xs, len );
    std::memcpy( ys, in, (size_t)len );
    return (char*)ys + len;
}

int sizeof_type( int x ) {
    if ( x < FSHORT || x > UNITS ) return -1;

    constexpr const int sizes[] = {
        dl::SIZEOF_FSHORT,
        dl::SIZEOF_FSINGL,
        dl::SIZEOF_FSING1,
        dl::SIZEOF_FSING2,
        dl::SIZEOF_ISINGL,
        dl::SIZEOF_VSINGL,
        dl::SIZEOF_FDOUBL,
        dl::SIZEOF_FDOUB1,
        dl::SIZEOF_FDOUB2,
        dl::SIZEOF_CSINGL,
        dl::SIZEOF_CDOUBL,
        dl::SIZEOF_SSHORT,
        dl::SIZEOF_SNORM,
        dl::SIZEOF_SLONG,
        dl::SIZEOF_USHORT,
        dl::SIZEOF_UNORM,
        dl::SIZEOF_ULONG,
        dl::SIZEOF_UVARI,
        dl::SIZEOF_IDENT,
        dl::SIZEOF_ASCII,
        dl::SIZEOF_DTIME,
        dl::SIZEOF_ORIGIN,
        dl::SIZEOF_OBNAME,
        dl::SIZEOF_OBJREF,
        dl::SIZEOF_ATTREF,
        dl::SIZEOF_STATUS,
        dl::SIZEOF_UNITS,
    };

    return sizes[ x - 1 ];
}

} // namespace dl
