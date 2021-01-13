#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <type_traits>

#include <endianness/endianness.h>

#include <dlisio/dlis/types.h>

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

const char* dlis_uvari( const char* xs, std::int32_t* out ) {
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

const char* dlis_objref( const char* xs, std::int32_t* ident_len,
                                         char* ident,
                                         std::int32_t* origin,
                                         std::uint8_t* copy_number,
                                         std::int32_t* objname_len,
                                         char* identifier ) {
    xs = dlis_ident( xs, ident_len, ident );
    return dlis_obname( xs, origin, copy_number, objname_len, identifier );
}

const char* dlis_attref( const char* xs, std::int32_t* ident_len,
                                         char* ident,
                                         std::int32_t* origin,
                                         std::uint8_t* copy_number,
                                         std::int32_t* objname_len,
                                         char* identifier,
                                         std::int32_t* ident2_len,
                                         char* ident2 ) {
    xs = dlis_ident( xs, ident_len, ident );
    xs = dlis_obname( xs, origin, copy_number, objname_len, identifier );
    return dlis_ident( xs, ident2_len, ident2 );
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

const char* dlis_units( const char* xs, std::int32_t* len, char* out ) {
    std::uint8_t ln;
    xs = dlis_ushort( xs, &ln );

    if( len ) *len = ln;
    if( out ) std::memcpy( out, xs, ln );
    return xs + ln;
}

/*
 * output functions
 */

void* dlis_sshorto( void* xs, std::int8_t x ) {
    return dlis_ushorto( xs, x );
}

void* dlis_snormo( void* xs, std::int16_t x ) {
    return dlis_unormo( xs, x );
}

void* dlis_slongo( void* xs, std::int32_t x ) {
    return dlis_ulongo( xs, x );
}

void* dlis_ushorto( void* xs, std::uint8_t x ) {
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );
}

void* dlis_unormo( void* xs, std::uint16_t x ) {
    x = hton( x );
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );;
}

void* dlis_ulongo( void* xs, std::uint32_t x ) {
    x = hton( x );
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );
}

void* dlis_fsinglo( void* xs, float x ) {
    x = hton( x );
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );
}

void* dlis_fdoublo( void* xs, double x ) {
    x = hton( x );
    std::memcpy( xs, &x, sizeof( x ) );
    return (char*)xs + sizeof( x );
}

void* dlis_isinglo( void* xs, float x ) {
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

void* dlis_vsinglo( void* xs, float x ) {
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

void* dlis_fsing1o( void* xs, float v, float a ) {
    void* ys = dlis_fsinglo( xs, v );
    void* zs = dlis_fsinglo( ys, a );
    return zs;
}

void* dlis_fsing2o( void* xs, float V, float A, float B ) {
    void* ys = dlis_fsinglo( xs, V );
    void* zs = dlis_fsinglo( ys, A );
    void* ws = dlis_fsinglo( zs, B );
    return ws;
}

void* dlis_csinglo( void* xs, float R, float I ) {
    void* ys = dlis_fsinglo( xs, R );
    void* zs = dlis_fsinglo( ys, I );
    return zs;
}

void* dlis_fdoub1o( void* xs, double V, double A ) {
    void* ys = dlis_fdoublo( xs, V );
    void* zs = dlis_fdoublo( ys, A );
    return zs;
}

void* dlis_fdoub2o( void* xs, double V, double A, double B ) {
    void* ys = dlis_fdoublo( xs, V );
    void* zs = dlis_fdoublo( ys, A );
    void* ws = dlis_fdoublo( zs, B );
    return ws;
}

void* dlis_cdoublo( void* xs, double R, double I ) {
    void* ys = dlis_fdoublo( xs, R );
    void* zs = dlis_fdoublo( ys, I );
    return zs;
}

void* dlis_uvario( void* xs, std::int32_t x, int width ) {
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

void* dlis_idento( void* xs, std::uint8_t len, const char* in ) {
    void* ys = dlis_ushorto( xs, len );
    std::memcpy( ys, in, (size_t)len );
    return (char*)ys + len;
}

void* dlis_asciio( void* xs, std::int32_t len,
                             const char* in,
                             std::uint8_t l ) {
    void* ys = dlis_uvario( xs, len, l );
    std::memcpy( ys, in, (size_t)len );
    return (char*)ys + len;
}

void* dlis_origino( void* xs, std::int32_t x ) {
    return dlis_uvario( xs, x, 4 );
}

void* dlis_statuso( void* xs, std::uint8_t x ) {
    return dlis_ushorto( xs, x );
}

int dlis_yearo( int Y ) {
    return Y - DLIS_YEAR_ZERO;
}

void* dlis_dtimeo( void* xs, int Y,
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

void* dlis_obnameo( void* xs, std::int32_t origin,
                              std::uint8_t copy_number,
                              std::uint8_t idlen,
                              const char* identifier ) {
    void* ys = dlis_origino( xs, origin );
    void* zs = dlis_ushorto( ys, copy_number );
    void* ws = dlis_idento( zs, idlen, identifier );
    return ws;
}

void* dlis_objrefo( void* xs, std::uint8_t ident_len,
                              const char* ident,
                              std::int32_t origin,
                              std::uint8_t copy_number,
                              std::uint8_t objname_len,
                              const char* identifier ) {

    void* ys = dlis_idento( xs, ident_len, ident );
    void* zs = dlis_obnameo( ys, origin,
                                 copy_number,
                                 objname_len,
                                 identifier );
    return zs;
}

void* dlis_attrefo( void* xs, std::uint8_t ident1_len,
                              const char* ident1,
                              std::int32_t origin,
                              std::uint8_t copy_number,
                              std::uint8_t objname_len,
                              const char* identifier,
                              std::uint8_t ident2_len,
                              const char* ident2 ) {

    void* ys = dlis_idento( xs, ident1_len, ident1 );
    void* zs = dlis_obnameo( ys, origin,
                                 copy_number,
                                 objname_len,
                                 identifier );

    void* ws = dlis_idento( zs, ident2_len, ident2 );
    return ws;
}

void* dlis_unitso( void* xs, std::uint8_t len, const char* in ) {
    void* ys = dlis_ushorto( xs, len );
    std::memcpy( ys, in, (size_t)len );
    return (char*)ys + len;
}

int dlis_sizeof_type( int x ) {
    if ( x < DLIS_FSHORT || x > DLIS_UNITS ) return -1;

    constexpr const int sizes[] = {
        DLIS_SIZEOF_FSHORT,
        DLIS_SIZEOF_FSINGL,
        DLIS_SIZEOF_FSING1,
        DLIS_SIZEOF_FSING2,
        DLIS_SIZEOF_ISINGL,
        DLIS_SIZEOF_VSINGL,
        DLIS_SIZEOF_FDOUBL,
        DLIS_SIZEOF_FDOUB1,
        DLIS_SIZEOF_FDOUB2,
        DLIS_SIZEOF_CSINGL,
        DLIS_SIZEOF_CDOUBL,
        DLIS_SIZEOF_SSHORT,
        DLIS_SIZEOF_SNORM,
        DLIS_SIZEOF_SLONG,
        DLIS_SIZEOF_USHORT,
        DLIS_SIZEOF_UNORM,
        DLIS_SIZEOF_ULONG,
        DLIS_SIZEOF_UVARI,
        DLIS_SIZEOF_IDENT,
        DLIS_SIZEOF_ASCII,
        DLIS_SIZEOF_DTIME,
        DLIS_SIZEOF_ORIGIN,
        DLIS_SIZEOF_OBNAME,
        DLIS_SIZEOF_OBJREF,
        DLIS_SIZEOF_ATTREF,
        DLIS_SIZEOF_STATUS,
        DLIS_SIZEOF_UNITS,
    };

    return sizes[ x - 1 ];
}
