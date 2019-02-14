#include <algorithm>
#include <bitset>
#include <cstdlib>
#include <cstring>
#include <string>

#include <dlisio/dlisio.h>
#include <dlisio/ext/types.hpp>

namespace {

void user_warning( const std::string& ) noexcept (true) {
    // TODO:
}

struct set_descriptor {
    int role;
    bool type;
    bool name;
};

set_descriptor parse_set_descriptor( const char* cur ) noexcept (false) {
    std::uint8_t attr;
    std::memcpy( &attr, cur, DLIS_DESCRIPTOR_SIZE );

    set_descriptor flags;
    dlis_component( attr, &flags.role );

    switch (flags.role) {
        case DLIS_ROLE_RDSET:
        case DLIS_ROLE_RSET:
        case DLIS_ROLE_SET:
            break;

        default: {
            const auto bits = std::bitset< 8 >{ attr }.to_string();
            const auto msg = std::string("expected SET, RSET or RDSET, was ")
                           + dlis_component_str( flags.role )
                           + "(" + bits + ")"
                           ;
            throw std::invalid_argument( msg );
        }
    }

    int type, name;
    const auto err = dlis_component_set( attr, flags.role, &type, &name );
    flags.type = type;
    flags.name = name;

    switch (err) {
        case DLIS_OK:
            break;

        case DLIS_INCONSISTENT:
            /*
             * 3.2.2.2 Component usage
             *  The Set Component contains the Set Type, which is not optional
             *  and must not be null, and the Set Name, which is optional.
             */
            user_warning( "SET:type not set, but must be non-null." );
            flags.type = true;
            break;

        default:
            throw std::runtime_error("unhandled error in dlis_component_set");
    }

    return flags;
}

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

struct object_descriptor {
    bool name;
};

object_descriptor parse_object_descriptor( const char* cur ) {
    std::uint8_t attr;
    std::memcpy( &attr, cur, DLIS_DESCRIPTOR_SIZE );

    int role;
    dlis_component( attr, &role );

    if (role != DLIS_ROLE_OBJECT) {
        const auto bits = std::bitset< 8 >{ attr }.to_string();
        const auto msg = std::string("expected OBJECT, was ")
                       + dlis_component_str( role )
                       + "(" + bits + ")"
                       ;
        throw std::invalid_argument( msg );
    }

    int name;
    const auto err = dlis_component_object( attr, role, &name );
    if (err) user_warning( "OBJECT:name was not set, but must be non-null" );

    return { true };
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

template < typename T >
const char* extract( std::int32_t count,
                     std::vector< T >& vec,
                     const char* xs ) noexcept (false) {

    T elem;
    std::vector< T > tmp;
    for( std::int32_t i = 0; i < count; ++i ) {
        xs = cast( xs, elem );
        tmp.push_back( std::move( elem ) );
    }

    vec.swap( tmp );
    return xs;
}

template < typename Monostate, typename... T >
const char* elements( const char* xs,
                      dl::uvari count,
                      dl::representation_code reprc,
                      mpark::variant< Monostate, T ... >& vec ) {
    using Vec = typename std::decay< decltype (vec) >::type;
    static_assert(
        std::is_same< Vec, dl::value_vector >::value,
        "element-extraction is only intended to work with vaule_vector "
        "as source"
    );

    const auto n = dl::decay( count );
    /*
     * use the same trick as object_attribute::into<variant>
     *
     * In short, generate an if-else-if sequence and for the matching
     * representation code, construct the right vector for the variant and
     * populate it
     */
    using sequencer = int[];
    static_cast< void >( sequencer {
        ((reprc == dl::typeinfo< typename T::value_type >::reprc)
        ? xs = extract( n, vec.template emplace< T >(), xs ), 0
        : 0) ...
    });

    return xs;
}

}

namespace dl {

void basic_object::set( const object_attribute& attr ) noexcept (false) {
    /*
     * This is essentially map::insert-or-update
     */
    const auto eq = [&]( const object_attribute& x ) {
        return attr.label == x.label;
    };

    auto itr = std::find_if( this->attributes.begin(),
                             this->attributes.end(),
                             eq );

    if (itr == this->attributes.end())
        this->attributes.push_back(attr);
    else
        *itr = attr;
}

void basic_object::remove( const object_attribute& attr ) noexcept (false) {
    /*
     * This is essentially map::remove
     */
    const auto eq = [&]( const object_attribute& x ) {
        return attr.label == x.label;
    };

    auto itr = std::remove_if( this->attributes.begin(),
                               this->attributes.end(),
                               eq );

    this->attributes.erase( itr, this->attributes.end() );
}

std::size_t basic_object::len() const noexcept (true) {
    return this->attributes.size();
}

const object_attribute&
basic_object::at( const std::string& key )
const noexcept (false)
{
    auto eq = [&key]( const dl::object_attribute& attr ) {
        return dl::decay( attr.label ) == key;
    };

    auto itr = std::find_if( this->attributes.begin(),
                             this->attributes.end(),
                             eq );

    if (itr == this->attributes.end())
        throw std::out_of_range( key );

    return *itr;
}

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
        attr.invariant = flags.invariant;

        tmp.push_back( std::move( attr ) );
    }
}


namespace {

basic_object defaulted_object( const object_template& tmpl ) noexcept (false) {
    basic_object def;
    for (const auto& attr : tmpl)
        def.set( attr );

    return def;
}

object_vector parse_objects( const object_template& tmpl,
                             const char* cur,
                             const char* end ) noexcept (false) {

    object_vector objs;
    const auto default_object = defaulted_object( tmpl );

    while (true) {
        if (std::distance( cur, end ) <= 0)
            throw std::out_of_range( "unexpected end-of-record" );

        auto object_flags = parse_object_descriptor( cur );
        cur += DLIS_DESCRIPTOR_SIZE;

        auto current = default_object;
        if (object_flags.name) cur = cast( cur, current.object_name );

        for (const auto& template_attr : tmpl) {
            if (template_attr.invariant) continue;
            if (cur == end) break;

            const auto flags = parse_attribute_descriptor( cur );
            if (flags.object) break;


            /*
             * only advance after this is surely not a new object, because if
             * it's the next object we want to read it again
             */
            cur += DLIS_DESCRIPTOR_SIZE;

            auto attr = template_attr;
            // absent means no meaning, so *unset* whatever is there
            if (flags.absent) {
                current.remove( attr );
                continue;
            }

            if (flags.label) {
                user_warning( "ATTRIB:label set, but must be null");
            }

            if (flags.count) cur = cast( cur, attr.count );
            if (flags.reprc) cur = cast( cur, attr.reprc );
            if (flags.units) cur = cast( cur, attr.units );
            if (flags.value) cur = elements( cur, attr.count,
                                                  attr.reprc,
                                                  attr.value );

            current.set(attr);
        }

        objs.push_back( std::move( current ) );

        if (cur == end) break;
    }

    return objs;
}

}

object_set parse_objects( const char* cur, const char* end ) {
    if (std::distance( cur, end ) <= 0)
        throw std::out_of_range( "eflr must be non-empty" );

    object_set set;

    const auto flags = parse_set_descriptor( cur );
    cur += DLIS_DESCRIPTOR_SIZE;

    if (std::distance( cur, end ) <= 0) {
        const auto msg = "unexpected end-of-record after SET descriptor";
        throw std::out_of_range( msg );
    }

    /*
     * TODO: check for every read that inside [begin,end)?
     */
    set.role = flags.role;
    if (flags.type) cur = cast( cur, set.type );
    if (flags.name) cur = cast( cur, set.name );

    cur = parse_template( cur, end, set.tmpl );

    if (std::distance( cur, end ) <= 0)
        throw std::out_of_range( "unexpected end-of-record after template" );

    std::string type = dl::decay( set.type );
    set.objects = parse_objects( set.tmpl, cur, end );
    return set;
}

}
