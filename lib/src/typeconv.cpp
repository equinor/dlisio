#include <complex>
#include <tuple>
#include <utility>
#include <vector>

#include <dlisio/types.h>

#include <dlisio/ext/types.hpp>

namespace dl {

int sshort( const char*& xs ) noexcept {
    std::int8_t x;
    xs = dlis_sshort( xs, &x );
    return x;
}

int snorm( const char*& xs ) noexcept {
    std::int16_t x;
    xs = dlis_snorm( xs, &x );
    return x;
}

long slong( const char*& xs ) noexcept {
    std::int32_t x;
    xs = dlis_slong( xs, &x );
    return x;
}

int ushort( const char*& xs ) noexcept {
    std::uint8_t x;
    xs = dlis_ushort( xs, &x );
    return x;
}

int unorm( const char*& xs ) noexcept {
    std::uint16_t x;
    xs = dlis_unorm( xs, &x );
    return x;
}

long ulong( const char*& xs ) noexcept {
    std::uint32_t x;
    xs = dlis_ulong( xs, &x );
    return x;
}

float fshort( const char*& xs ) noexcept {
    float x;
    xs = dlis_fshort( xs, &x );
    return x;
}

float fsingl(  const char*& xs ) noexcept {
    float x;
    xs = dlis_fsingl( xs, &x );
    return x;
}

double fdoubl( const char*& xs ) noexcept {
    double x;
    xs = dlis_fdoubl( xs, &x );
    return x;
}

float isingl(  const char*& xs ) noexcept {
    float x;
    xs = dlis_isingl( xs, &x );
    return x;
}

float vsingl(  const char*& xs ) noexcept {
    float x;
    xs = dlis_vsingl( xs, &x );
    return x;
}

std::pair< float, float > fsing1( const char*& xs ) noexcept {
    float V, A;
    xs = dlis_fsing1( xs, &V, &A );
    return { V, A };
}

std::tuple< float, float, float > fsing2( const char*& xs ) noexcept {
    float V, A, B;
    xs = dlis_fsing2( xs, &V, &A, &B );
    return std::make_tuple( V, A, B );
}

std::complex< float > csingl( const char*& xs ) noexcept {
    float R, I;
    xs = dlis_csingl( xs, &R, &I );
    return { R, I };
}

std::pair< double, double > fdoub1( const char*& xs ) noexcept {
    double V, A;
    xs = dlis_fdoub1( xs, &V, &A );
    return std::make_pair( V, A );
}

std::tuple< double, double, double > fdoub2( const char*& xs ) noexcept {
    double V, A, B;
    xs = dlis_fdoub2( xs, &V, &A, &B );
    return std::make_tuple( V, A, B );
}

std::complex< double > cdoubl( const char*& xs ) noexcept {
    double R, I;
    xs = dlis_cdoubl( xs, &R, &I );
    return { R, I };
}

long uvari( const char*& xs ) noexcept {
    std::int32_t x;
    xs = dlis_uvari( xs, &x );
    return x;
}

std::string ident( const char*& xs ) {
    char str[ 256 ];
    std::int32_t len;

    dlis_ident( xs, &len, nullptr );
    xs = dlis_ident( xs, &len, str );

    return { str, str + len };
}

std::string ascii( const char*& xs ) {
    std::vector< char > str;
    std::int32_t len;

    dlis_ascii( xs, &len, nullptr );
    str.resize( len );
    xs = dlis_ascii( xs, &len, str.data() );

    return { str.begin(), str.end() };
}

datetime dtime( const char*& xs ) noexcept {
    datetime dt;
    xs = dlis_dtime( xs, &dt.Y,
                         &dt.TZ,
                         &dt.M,
                         &dt.D,
                         &dt.H,
                         &dt.MN,
                         &dt.S,
                         &dt.MS );
    dt.Y = dlis_year( dt.Y );
    return dt;
}

long origin( const char*& xs ) noexcept {
    std::int32_t x;
    xs = dlis_origin( xs, &x );
    return x;
}

object_name obname( const char*& xs ) {
    char str[ 256 ];
    std::int32_t len;

    std::int32_t orig;
    std::uint8_t copy;

    xs = dlis_obname( xs, &orig, &copy, &len, str );
    return { orig, copy, std::string( str, str + len ) };
}

object_name obname( const char*& xs, int nmemb ) {
    if( nmemb < 4 ) {
        /*
         * safeguard against too-few-bytes to read the integer parts of the obname
         */
        std::string msg = "obname is minimum 5 bytes, nmemb was "
                        + std::to_string( nmemb );
        throw std::length_error( msg );
    }

    char str[ 256 ] = {};
    std::int32_t orig;
    std::uint8_t copy;
    std::int32_t len;
    std::uint8_t name_len;

    const auto* ptr = xs;
    ptr = dlis_origin( ptr, &orig );
    ptr = dlis_ushort( ptr, &copy );
    ptr = dlis_ushort( ptr, &name_len );
    const auto int_len = std::distance( xs, ptr );

    if( int_len + name_len > nmemb ) {
        std::string msg = "expected obname length (= "
                        + std::to_string(int_len + name_len) + ") < nmemb ("
                        + "= " + std::to_string( nmemb ) + ")";
        throw std::length_error( msg );
    }

    // TODO: stronger exception guarantee?
    xs = dlis_ident( ptr - 1, &len, str );
    return { orig, copy, str };
}

std::tuple< std::string, long, int, std::string > objref( const char*& xs ) {
    char strid[ 256 ];
    char strobj[ 256 ];
    std::int32_t lenid;
    std::int32_t lenobj;

    std::int32_t orig;
    std::uint8_t copy;

    xs = dlis_objref( xs,
                      &lenid, strid,
                      &orig, &copy, &lenobj, strobj );

    return std::make_tuple(
        std::string( strid, strid + lenid ),
        orig, copy, std::string( strobj, strobj + lenobj )
    );
}

int status( const char*& xs ) noexcept {
    std::uint8_t x;
    xs = dlis_status( xs, &x );
    return x;
}

}
