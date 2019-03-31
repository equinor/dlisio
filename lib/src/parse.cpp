#include <algorithm>
#include <bitset>
#include <cstdlib>
#include <cstring>
#include <string>

#include <fmt/core.h>

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
            const auto role = dlis_component_str(flags.role);
            const auto msg  = "error parsing object set descriptor: "
                              "expected SET, RSET or RDSET, was {} ({})"
                            ;
            throw std::invalid_argument(fmt::format(msg, role, bits));
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

        default: {
            const auto bits = std::bitset< 8 >(role).to_string();
            const auto was  = dlis_component_str(role);
            const auto msg  = "error parsing attribute descriptor: "
                              "expected ATTRIB, INVATR, or OBJECT, was {} ({})"
                            ;
            throw std::invalid_argument(fmt::format(msg, was, bits));
        }
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
        const auto was  = dlis_component_str(role);
        const auto msg  = "error parsing object descriptor: "
                          "expected OBJECT, was {} ({})"
                        ;
        throw std::invalid_argument(fmt::format(msg, was, bits));
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
        const auto msg = "invalid representation code {}, "
                         "expected 1 <= reprc <= 27"
                       ;
        throw std::invalid_argument(fmt::format(msg, x));
    }

    reprc = static_cast< dl::representation_code >( x );
    return xs;
}

template < typename T >
const char* extract( std::vector< T >& vec,
                     std::int32_t count,
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

template < typename T >
std::vector< T >& reset( dl::value_vector& value ) noexcept (false) {
    return value.emplace< std::vector< T > >();
}

const char* elements( const char* xs,
                      dl::uvari count,
                      dl::representation_code reprc,
                      dl::value_vector& vec ) {

    const auto n = dl::decay( count );

    if (n == 0) {
        vec = mpark::monostate{};
        return xs;
    }

    using rpc = dl::representation_code;
    switch (reprc) {
        case rpc::fshort: return extract( reset< dl::fshort >( vec ), n, xs );
        case rpc::fsingl: return extract( reset< dl::fsingl >( vec ), n, xs );
        case rpc::fsing1: return extract( reset< dl::fsing1 >( vec ), n, xs );
        case rpc::fsing2: return extract( reset< dl::fsing2 >( vec ), n, xs );
        case rpc::isingl: return extract( reset< dl::isingl >( vec ), n, xs );
        case rpc::vsingl: return extract( reset< dl::vsingl >( vec ), n, xs );
        case rpc::fdoubl: return extract( reset< dl::fdoubl >( vec ), n, xs );
        case rpc::fdoub1: return extract( reset< dl::fdoub1 >( vec ), n, xs );
        case rpc::fdoub2: return extract( reset< dl::fdoub2 >( vec ), n, xs );
        case rpc::csingl: return extract( reset< dl::csingl >( vec ), n, xs );
        case rpc::cdoubl: return extract( reset< dl::cdoubl >( vec ), n, xs );
        case rpc::sshort: return extract( reset< dl::sshort >( vec ), n, xs );
        case rpc::snorm : return extract( reset< dl::snorm  >( vec ), n, xs );
        case rpc::slong : return extract( reset< dl::slong  >( vec ), n, xs );
        case rpc::ushort: return extract( reset< dl::ushort >( vec ), n, xs );
        case rpc::unorm : return extract( reset< dl::unorm  >( vec ), n, xs );
        case rpc::ulong : return extract( reset< dl::ulong  >( vec ), n, xs );
        case rpc::uvari : return extract( reset< dl::uvari  >( vec ), n, xs );
        case rpc::ident:  return extract( reset< dl::ident  >( vec ), n, xs );
        case rpc::ascii : return extract( reset< dl::ascii  >( vec ), n, xs );
        case rpc::dtime : return extract( reset< dl::dtime  >( vec ), n, xs );
        case rpc::origin: return extract( reset< dl::origin >( vec ), n, xs );
        case rpc::obname: return extract( reset< dl::obname >( vec ), n, xs );
        case rpc::objref: return extract( reset< dl::objref >( vec ), n, xs );
        case rpc::attref: return extract( reset< dl::attref >( vec ), n, xs );
        case rpc::status: return extract( reset< dl::status >( vec ), n, xs );
        case rpc::units : return extract( reset< dl::units  >( vec ), n, xs );
        default: {
            const auto msg = "unable to interpret attribute: "
                             "unknown representation code {}";
            const auto code = static_cast< int >(reprc);
            throw std::runtime_error(fmt::format(msg, code));
        }
    }

    return xs;
}

struct variant_equal {
    template < typename T, typename U >
    bool operator () (T&&, U&&) const noexcept (true) {
        return false;
    }

    template < typename T >
    bool operator () (const std::vector< T >& lhs,
                      const std::vector< T >& rhs)
    const noexcept (true) {
        return (lhs.size() == rhs.size())
            && std::equal(lhs.begin(), lhs.end(), rhs.begin());
    }
};

bool value_variant_eq(const dl::value_vector& lhs,
                      const dl::value_vector& rhs)
noexcept (true) {
    return mpark::visit(variant_equal{}, lhs, rhs);
}

}

namespace dl {

bool object_attribute::operator == (const object_attribute& o)
const noexcept (true) {
    return this->label == o.label
        && this->count == o.count
        && this->reprc == o.reprc
        && this->units == o.units
        // invariant doesn't matter for attribute equality,
        // so ignore it
        && value_variant_eq(this->value, o.value);
}

std::string obname::fingerprint(const std::string& type)
const noexcept (false) {
    const auto& origin = dl::decay(this->origin);
    const auto& copy = dl::decay(this->copy);
    const auto& id = dl::decay(this->id);

    auto len = dlis_object_fingerprint_len(type.size(),
                                           type.data(),
                                           id.size(),
                                           id.data(),
                                           origin,
                                           copy);

    // TODO: investigate what went wrong here
    if (len <= 0)
        throw std::invalid_argument("fingerprint");

    auto str = std::vector< char >(len);
    auto err = dlis_object_fingerprint(type.size(),
                                       type.data(),
                                       id.size(),
                                       id.data(),
                                       origin,
                                       copy,
                                       str.data());

    if (err) throw std::runtime_error("fingerprint: something went wrong");

    return std::string(str.begin(), str.end());
}

std::string objref::fingerprint() const noexcept (false) {
    return this->name.fingerprint(dl::decay(this->type));
}

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

bool basic_object::operator == (const basic_object& o) const noexcept (true) {
    return this->object_name       == o.object_name
        && this->attributes.size() == o.attributes.size()
        && std::equal(this->attributes.begin(),
                      this->attributes.end(),
                      o.attributes.begin());
}

bool basic_object::operator != (const basic_object& o) const noexcept (true) {
    return !(*this == o);
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

struct len {
    template < typename Vec >
    std::size_t operator () ( const Vec& vec ) const {
        return vec.size();
    }

    std::size_t operator () ( const mpark::monostate& ) const {
        throw std::invalid_argument( "patch: len() called on monostate" );
    }
};

struct shrink {
    std::size_t size;
    explicit shrink( std::size_t sz ) : size( sz ) {}

    template < typename Vec >
    std::size_t operator () ( const Vec& vec ) const {
        return vec.size();
    }

    std::size_t operator () ( const mpark::monostate& ) const {
        throw std::invalid_argument( "patch: len() called on monostate" );
    }
};

void patch_missing_value( dl::value_vector& value,
                          std::size_t count,
                          dl::representation_code reprc )
noexcept (false)
{
    /*
     * value is *NOT* monostate, i.e. there is a default value.  if count !=
     * values.size(), resize it.
     */
    if (!mpark::holds_alternative< mpark::monostate >(value)) {
        const auto size = mpark::visit( len(), value );
        /* same size, so return */
        if (size == count) return;

        /* smaller, shrink and all is fine */
        if (size < count) {
            mpark::visit( shrink( count ), value );
            return;
        }

        /*
         * count is larger, so insert default values, maybe? for now, throw
         * exception and consider what to do when a file actually uses this
         * behaviour
         */
        const auto msg = "object attribute without no value value, but count "
                         "(which is {}) >= size (which is {})"
        ;
        throw dl::not_implemented(fmt::format(msg, count, size));
    }

    /*
     * value *is* monstate, so initialize a default value that corresponds to
     * whatever type is there.
     *
     * 3.2.2 EFLR: Component Structure declares ident with the empty string as
     * a default type, but this is already stored in the defaulted reprc,
     * making this switch work in the general case
     */

    using rpc = dl::representation_code;
    switch (reprc) {
        case rpc::fshort: reset< dl::fshort >(value).resize(count); return;
        case rpc::fsingl: reset< dl::fsingl >(value).resize(count); return;
        case rpc::fsing1: reset< dl::fsing1 >(value).resize(count); return;
        case rpc::fsing2: reset< dl::fsing2 >(value).resize(count); return;
        case rpc::isingl: reset< dl::isingl >(value).resize(count); return;
        case rpc::vsingl: reset< dl::vsingl >(value).resize(count); return;
        case rpc::fdoubl: reset< dl::fdoubl >(value).resize(count); return;
        case rpc::fdoub1: reset< dl::fdoub1 >(value).resize(count); return;
        case rpc::fdoub2: reset< dl::fdoub2 >(value).resize(count); return;
        case rpc::csingl: reset< dl::csingl >(value).resize(count); return;
        case rpc::cdoubl: reset< dl::cdoubl >(value).resize(count); return;
        case rpc::sshort: reset< dl::sshort >(value).resize(count); return;
        case rpc::snorm:  reset< dl::snorm  >(value).resize(count); return;
        case rpc::slong:  reset< dl::slong  >(value).resize(count); return;
        case rpc::ushort: reset< dl::ushort >(value).resize(count); return;
        case rpc::unorm:  reset< dl::unorm  >(value).resize(count); return;
        case rpc::ulong:  reset< dl::ulong  >(value).resize(count); return;
        case rpc::uvari:  reset< dl::uvari  >(value).resize(count); return;
        case rpc::ident:  reset< dl::ident  >(value).resize(count); return;
        case rpc::ascii:  reset< dl::ascii  >(value).resize(count); return;
        case rpc::dtime:  reset< dl::dtime  >(value).resize(count); return;
        case rpc::origin: reset< dl::origin >(value).resize(count); return;
        case rpc::obname: reset< dl::obname >(value).resize(count); return;
        case rpc::objref: reset< dl::objref >(value).resize(count); return;
        case rpc::attref: reset< dl::attref >(value).resize(count); return;
        case rpc::status: reset< dl::status >(value).resize(count); return;
        case rpc::units:  reset< dl::units  >(value).resize(count); return;
        default: {
            const auto msg = "unable to patch attribute with no value: "
                             "unknown representation code {}";
            const auto code = static_cast< int >(reprc);
            throw std::runtime_error(fmt::format(msg, code));
        }
    }
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

            const auto count = dl::decay( attr.count );

            /*
             * 3.2.2.1 Component Descriptor
             * When an object attribute count is zero, the value is explicitly
             * undefined, even if a default exists.
             *
             * This is functionally equivalent to the value being marked absent
             */
            if (count == 0)
                attr.value = mpark::monostate{};

            /*
             * Count is non-zero, but there's no value for this attribute.
             * Expand what's already defaulted, and if it is monostate, set the
             * default of that value
             */
            if (!flags.value)
                patch_missing_value( attr.value, count, attr.reprc );

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

    set.objects = parse_objects( set.tmpl, cur, end );
    return set;
}

}
