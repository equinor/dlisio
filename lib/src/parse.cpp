#include <algorithm>
#include <bitset>
#include <cstdlib>
#include <cstring>
#include <string>

#include <dlisio/dlisio.h>
#include <dlisio/ext/types.hpp>

namespace {

struct attribute_descriptor {
    bool label;
    bool count;
    bool reprc;
    bool units;
    bool value;
    bool object = false;
    bool absent = false;
    bool invariant = false;
};

attribute_descriptor parse_attribute_descriptor( const char* cur ) {
    std::uint8_t attr;
    std::memcpy( &attr, cur, DLIS_DESCRIPTOR_SIZE );

    int role;
    dlis_component( attr, &role );

    attribute_descriptor flags;
    switch (role) {
        case DLIS_ROLE_ABSATR:
            flags.absent = true;
            break;

        case DLIS_ROLE_OBJECT:
            flags.object = true;
            break;

        case DLIS_ROLE_INVATR:
            flags.invariant = true;

        case DLIS_ROLE_ATTRIB:
            break;

        default:
            throw std::invalid_argument(
                std::string("expected ATTRIB, INVATR, or OBJECT, was ")
                + dlis_component_str( role )
                + "(" + std::bitset< 8 >( role ).to_string() + ")"
            );
    }

    if (flags.object || flags.absent) return flags;

    int label, count, reprc, units, value;
    const auto err = dlis_component_attrib( attr, role, &label,
                                                        &count,
                                                        &reprc,
                                                        &units,
                                                        &value );
    flags.label = label;
    flags.count = count;
    flags.reprc = reprc;
    flags.units = units;
    flags.value = value;

    if (!err) return flags;

    // all sources for this error should've been checked, so
    // something is REALLY wrong if we end up here
    throw std::runtime_error( "unhandled error in dlis_component_attrib" );
}

void user_warning( const std::string& ) noexcept (true) {
    // TODO:
}

using std::swap;
const char* cast( const char* xs, dl::sshort& i ) noexcept (true) {
    std::int8_t x;
    xs = dlis_sshort( xs, &x );

    dl::sshort tmp{ x };
    swap( i, tmp );

    return xs;
}

const char* cast( const char* xs, dl::snorm& i ) noexcept (true) {
    std::int16_t x;
    xs = dlis_snorm( xs, &x );

    dl::snorm tmp{ x };
    swap( i, tmp );

    return xs;
}

const char* cast( const char* xs, dl::slong& i ) noexcept (true) {
    std::int32_t x;
    xs = dlis_slong( xs, &x );

    dl::slong tmp{ x };
    swap( i, tmp );
    return xs;
}

const char* cast( const char* xs, dl::ushort& i ) noexcept (true) {
    std::uint8_t x;
    xs = dlis_ushort( xs, &x );

    dl::ushort tmp{ x };
    swap( tmp, i );
    return xs;
}


const char* cast( const char* xs, dl::unorm& i ) noexcept (true) {
    std::uint16_t x;
    xs = dlis_unorm( xs, &x );

    dl::unorm tmp{ x };
    swap( tmp, i );
    return xs;
}

const char* cast( const char* xs, dl::ulong& i ) noexcept (true) {
    std::uint32_t x;
    xs = dlis_ulong( xs, &x );
    i = dl::ulong{ x };
    return xs;
}

const char* cast( const char* xs, dl::uvari& i ) noexcept (true) {
    std::int32_t x;
    xs = dlis_uvari( xs, &x );
    i = dl::uvari{ x };
    return xs;
}

const char* cast( const char* xs, dl::fshort& f ) noexcept (true) {
    float x;
    xs = dlis_fshort( xs, &x );
    f = dl::fshort{ x };
    return xs;
}

const char* cast( const char* xs, dl::fsingl& f ) noexcept (true) {
    float x;
    xs = dlis_fsingl( xs, &x );
    f = dl::fsingl{ x };
    return xs;
}

const char* cast( const char* xs, dl::fdoubl& f ) noexcept (true) {
    double x;
    xs = dlis_fdoubl( xs, &x );
    f = dl::fdoubl{ x };
    return xs;
}

const char* cast( const char* xs, dl::fsing1& f ) noexcept (true) {
    float v, a;
    xs = dlis_fsing1( xs, &v, &a );
    f = dl::fsing1{ v, a };
    return xs;
}

const char* cast( const char* xs, dl::fsing2& f ) noexcept (true) {
    float v, a, b;
    xs = dlis_fsing2( xs, &v, &a, &b );
    f = dl::fsing2{ v, a, b };
    return xs;
}

const char* cast( const char* xs, dl::fdoub1& f ) noexcept (true) {
    double v, a;
    xs = dlis_fdoub1( xs, &v, &a );
    f = dl::fdoub1{ v, a };
    return xs;
}

const char* cast( const char* xs, dl::fdoub2& f ) noexcept (true) {
    double v, a, b;
    xs = dlis_fdoub2( xs, &v, &a, &b );
    f = dl::fdoub2{ v, a, b };
    return xs;
}

const char* cast( const char* xs, dl::csingl& f ) noexcept (true) {
    float re, im;
    xs = dlis_csingl( xs, &re, &im );
    f = dl::csingl{ std::complex< float >{ re, im } };
    return xs;
}

const char* cast( const char* xs, dl::cdoubl& f ) noexcept (true) {
    double re, im;
    xs = dlis_cdoubl( xs, &re, &im );
    f = dl::cdoubl{ std::complex< double >{ re, im } };
    return xs;
}

const char* cast( const char* xs, dl::isingl& f ) noexcept (true) {
    float x;
    xs = dlis_isingl( xs, &x );
    f = dl::isingl{ x };
    return xs;
}

const char* cast( const char* xs, dl::vsingl& f ) noexcept (true) {
    float x;
    xs = dlis_vsingl( xs, &x );
    f = dl::vsingl{ x };
    return xs;
}

const char* cast( const char* xs, dl::status& s ) noexcept (true) {
    dl::status::value_type x;
    xs = dlis_status( xs, &x );
    s = dl::status{ x };
    return xs;
}

template <typename T>
const char* parse_ident( const char* xs, T& out ) noexcept (false) {
    char str[ 256 ];
    std::int32_t len;

    dlis_ident( xs, &len, nullptr );
    xs = dlis_ident( xs, &len, str );

    T tmp{ std::string{ str, str + len } };
    swap( out, tmp );
    return xs;
}

const char* cast( const char* xs, dl::ident& id ) {
    return parse_ident( xs, id );
}

const char* cast( const char* xs, dl::units& id ) {
    return parse_ident( xs, id );
}

const char* cast( const char* xs, dl::ascii& ascii ) noexcept (false) {
    std::vector< char > str;
    std::int32_t len;

    dlis_ascii( xs, &len, nullptr );
    str.resize( len );
    xs = dlis_ascii( xs, &len, str.data() );

    dl::ascii tmp{ std::string{ str.begin(), str.end() } };
    swap( ascii, tmp );
    return xs;
}

const char* cast( const char* xs, dl::origin& origin ) noexcept (true) {
    dl::origin::value_type x;
    xs = dlis_origin( xs, &x );
    origin = dl::origin{ x };
    return xs;
}

const char* cast( const char* xs, dl::obname& obname ) noexcept (false) {
    char str[ 256 ];
    std::int32_t len;

    std::int32_t orig;
    std::uint8_t copy;

    xs = dlis_obname( xs, &orig, &copy, &len, str );

    dl::obname tmp{ dl::origin{ orig },
                    dl::ushort{ copy },
                    dl::ident{ std::string{ str, str + len } } };
    swap( obname, tmp );
    return xs;
}

const char* cast( const char* xs, dl::objref& objref ) noexcept (false) {
    char iden[ 256 ];
    char name[ 256 ];
    std::int32_t ident_len;
    std::int32_t origin;
    std::uint8_t copy_number;
    std::int32_t obname_len;

    xs = dlis_objref( xs, &ident_len,
                          iden,
                          &origin,
                          &copy_number,
                          &obname_len,
                          name );

    dl::objref tmp{ dl::ident{ std::string{ iden, iden + ident_len } },
                    dl::obname{
                        dl::origin{ origin },
                        dl::ushort{ copy_number },
                        dl::ident{ std::string{ name, name + obname_len } }
                    }
    };

    swap( objref, tmp );
    return xs;
}

const char* cast( const char* xs, dl::attref& attref ) noexcept (false) {
    char id1[ 256 ];
    char obj[ 256 ];
    char id2[ 256 ];
    std::int32_t ident1_len;
    std::int32_t origin;
    std::uint8_t copy_number;
    std::int32_t obname_len;
    std::int32_t ident2_len;

    xs = dlis_attref( xs, &ident1_len,
                          id1,
                          &origin,
                          &copy_number,
                          &obname_len,
                          obj,
                          &ident2_len,
                          id2 );

    dl::attref tmp{ dl::ident{ std::string{ id1, id1 + ident1_len } },
                    dl::obname{
                        dl::origin{ origin },
                        dl::ushort{ copy_number },
                        dl::ident{ std::string{ obj, obj + obname_len } }
                    },
                    dl::ident{ std::string{ id1, id1 + ident1_len } }
    };

    swap( attref, tmp );
    return xs;
}


const char* cast( const char* xs, dl::dtime& dtime ) noexcept (true) {
    dl::dtime dt;
    xs = dlis_dtime( xs, &dt.Y,
                         &dt.TZ,
                         &dt.M,
                         &dt.D,
                         &dt.H,
                         &dt.MN,
                         &dt.S,
                         &dt.MS );
    dt.Y = dlis_year( dt.Y );
    swap( dtime, dt );
    return xs;
}

const char* cast( const char* xs,
                  dl::representation_code& reprc ) noexcept (false) {

    dl::ushort x{ 0 };
    xs = cast( xs, x );

    if (x < DLIS_FSHORT || x > DLIS_UNITS) {
        const auto msg = "invalid representation code (reprc = "
                       + std::to_string( x )
                       + "), expected 1 <= reprc <= 27"
                       ;
        throw std::invalid_argument(msg);
    }

    reprc = static_cast< dl::representation_code >( x );
    return xs;
}

struct elements_visitor : boost::static_visitor< const char* > {
    const char* begin;
    long count;

    elements_visitor( const char* xs, long n ) :
        begin( xs ), count( n )
    {}

    template< typename T >
    const char* operator()( std::vector< T >& out ) {

        T elem;
        std::vector< T > tmp;
        auto xs = this->begin;

        for( std::int32_t i = 0; i < this->count; ++i ) {
            xs = cast( xs, elem );
            tmp.push_back( elem );
        }

        out.swap( tmp );
        return xs;
    }

};

dl::value_vector values_from_reprc( dl::representation_code reprc ) {
    using rep = dl::representation_code;
    switch (reprc) {
        case rep::fshort: return std::vector< dl::fshort >{};
        case rep::fsingl: return std::vector< dl::fsingl >{};
        case rep::fsing1: return std::vector< dl::fsing1 >{};
        case rep::fsing2: return std::vector< dl::fsing2 >{};
        case rep::isingl: return std::vector< dl::isingl >{};
        case rep::vsingl: return std::vector< dl::vsingl >{};
        case rep::fdoubl: return std::vector< dl::fdoubl >{};
        case rep::fdoub1: return std::vector< dl::fdoub1 >{};
        case rep::fdoub2: return std::vector< dl::fdoub2 >{};
        case rep::csingl: return std::vector< dl::csingl >{};
        case rep::cdoubl: return std::vector< dl::cdoubl >{};
        case rep::sshort: return std::vector< dl::sshort >{};
        case rep::snorm : return std::vector< dl::snorm  >{};
        case rep::slong : return std::vector< dl::slong  >{};
        case rep::ushort: return std::vector< dl::ushort >{};
        case rep::unorm : return std::vector< dl::unorm  >{};
        case rep::ulong : return std::vector< dl::ulong  >{};
        case rep::uvari : return std::vector< dl::uvari  >{};
        case rep::ident : return std::vector< dl::ident  >{};
        case rep::ascii : return std::vector< dl::ascii  >{};
        case rep::dtime : return std::vector< dl::dtime  >{};
        case rep::origin: return std::vector< dl::origin >{};
        case rep::obname: return std::vector< dl::obname >{};
        case rep::objref: return std::vector< dl::objref >{};
        case rep::attref: return std::vector< dl::attref >{};
        case rep::status: return std::vector< dl::status >{};
        case rep::units : return std::vector< dl::units  >{};

    }

    const auto msg = "unknown representation code "
                   + std::to_string( static_cast< std::uint8_t >( reprc ) )
                   ;
    throw std::runtime_error( msg );
}

const char* elements( const char* xs, dl::uvari count,
                                      dl::representation_code reprc,
                                      dl::value_vector& vec ) {
    const auto n = static_cast< dl::uvari::value_type >( count );
    dl::value_vector tmp = values_from_reprc( reprc );
    elements_visitor vs{ xs, n };
    xs = boost::apply_visitor( vs, tmp );
    swap( vec, tmp );
    return xs;
}

}

namespace dl {

const char* parse_template( const char* cur,
                            const char* end,
                            object_template& out ) noexcept (false) {
    object_template tmp;

    while (true) {
        if (cur >= end)
            throw std::out_of_range( "unexpected end-of-record" );

        const auto flags = parse_attribute_descriptor( cur );
        if (flags.object) {
            swap( tmp, out );
            return cur;
        }

        /* decriptor read, so advance the cursor */
        cur += DLIS_DESCRIPTOR_SIZE;

        if (flags.absent) {
            user_warning( "ABSATR in object template - skipping" );
            continue;
        }

        object_attribute attr;

        if (!flags.label) {
            /*
             * 3.2.2.2 Component usage
             *  All Components in the Template must have distinct, non-null
             *  Labels.
             *
             *  Assume that if this isn't set properly it's a corrupted
             *  descriptor, so just try to read the label anyway
             */
            user_warning( "Label not set, but must be non-null" );
        }

                         cur = cast( cur, attr.label );
        if (flags.count) cur = cast( cur, attr.count );
        if (flags.reprc) cur = cast( cur, attr.reprc );
        if (flags.units) cur = cast( cur, attr.units );
        if (flags.value) cur = elements( cur, attr.count,
                                              attr.reprc,
                                              attr.value );

        tmp.push_back( std::move( attr ) );
    }
}

}
