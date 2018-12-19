#ifndef DLISIO_EXT_TYPES_HPP
#define DLISIO_EXT_TYPES_HPP

#include <complex>
#include <cstdint>
#include <tuple>
#include <utility>
#include <vector>

#define BOOST_MPL_CFG_NO_PREPROCESSED_HEADERS
#define BOOST_MPL_LIMIT_LIST_SIZE 30
#include <boost/variant.hpp>

#include <dlisio/types.h>

#include "strong-typedef.hpp"

namespace dl {

enum class representation_code : std::uint8_t {
    fshort = DLIS_FSHORT,
    fsingl = DLIS_FSINGL,
    fsing1 = DLIS_FSING1,
    fsing2 = DLIS_FSING2,
    isingl = DLIS_ISINGL,
    vsingl = DLIS_VSINGL,
    fdoubl = DLIS_FDOUBL,
    fdoub1 = DLIS_FDOUB1,
    fdoub2 = DLIS_FDOUB2,
    csingl = DLIS_CSINGL,
    cdoubl = DLIS_CDOUBL,
    sshort = DLIS_SSHORT,
    snorm  = DLIS_SNORM,
    slong  = DLIS_SLONG,
    ushort = DLIS_USHORT,
    unorm  = DLIS_UNORM,
    ulong  = DLIS_ULONG,
    uvari  = DLIS_UVARI,
    ident  = DLIS_IDENT,
    ascii  = DLIS_ASCII,
    dtime  = DLIS_DTIME,
    origin = DLIS_ORIGIN,
    obname = DLIS_OBNAME,
    objref = DLIS_OBJREF,
    attref = DLIS_ATTREF,
    status = DLIS_STATUS,
    units  = DLIS_UNITS,
};

#define DLIS_REGISTER_TYPEALIAS(name, type) \
    struct name : detail::strong_typedef< name, type > { \
        using detail::strong_typedef< name, type >::strong_typedef; \
    }

DLIS_REGISTER_TYPEALIAS(fshort, float);
DLIS_REGISTER_TYPEALIAS(isingl, float);
DLIS_REGISTER_TYPEALIAS(vsingl, float);
DLIS_REGISTER_TYPEALIAS(uvari,  std::int32_t);
DLIS_REGISTER_TYPEALIAS(origin, std::int32_t);
DLIS_REGISTER_TYPEALIAS(ident,  std::string);
DLIS_REGISTER_TYPEALIAS(ascii,  std::string);
DLIS_REGISTER_TYPEALIAS(units,  std::string);
DLIS_REGISTER_TYPEALIAS(status, std::uint8_t);

#undef DLIS_REGISTER_TYPEALIAS

template< typename T, int > struct validated;
template< typename T > struct validated< T, 2 > { T V, A; };
template< typename T > struct validated< T, 3 > { T V, A, B; };

using fsing1 = validated< float, 2 >;
using fsing2 = validated< float, 3 >;
using fdoub1 = validated< double, 2 >;
using fdoub2 = validated< double, 3 >;

using ushort = std::uint8_t;
using unorm  = std::uint16_t;
using ulong  = std::uint32_t;

using sshort = std::int8_t;
using snorm  = std::int16_t;
using slong  = std::int32_t;

using fsingl = float;
using fdoubl = double;

using csingl = std::complex< fsingl >;
using cdoubl = std::complex< fdoubl >;

struct dtime {
    int Y, TZ, M, D, H, MN, S, MS;
};

struct obname {
    dl::origin origin;
    dl::ushort copy;
    dl::ident  id;

    bool operator == ( const obname& rhs ) const noexcept (true) {
        return this->origin == rhs.origin
            && this->copy == rhs.copy
            && this->id == rhs.id;
    }
};

struct objref {
    dl::ident  type;
    dl::obname name;

    bool operator == ( const objref& rhs ) const noexcept( true ) {
        return this->type == rhs.type
            && this->name == rhs.name;
    }
};

struct attref {
    dl::ident  type;
    dl::obname name;
    dl::ident  label;

    bool operator == ( const attref& rhs ) const noexcept( true ) {
        return this->type == rhs.type
            && this->name == rhs.name
            && this->label== rhs.label;
    }
};

using value_vector = boost::variant<
    std::vector< fshort >,
    std::vector< fsingl >,
    std::vector< fsing1 >,
    std::vector< fsing2 >,
    std::vector< isingl >,
    std::vector< vsingl >,
    std::vector< fdoubl >,
    std::vector< fdoub1 >,
    std::vector< fdoub2 >,
    std::vector< csingl >,
    std::vector< cdoubl >,
    std::vector< sshort >,
    std::vector< snorm  >,
    std::vector< slong  >,
    std::vector< ushort >,
    std::vector< unorm  >,
    std::vector< ulong  >,
    std::vector< uvari  >,
    std::vector< ident  >,
    std::vector< ascii  >,
    std::vector< dtime  >,
    std::vector< origin >,
    std::vector< obname >,
    std::vector< objref >,
    std::vector< attref >,
    std::vector< status >,
    std::vector< units  >
>;

struct object_attribute {
    dl::ident           label = {};
    dl::uvari           count = dl::uvari{ 1 };
    representation_code reprc = representation_code::ident;
    dl::units           units = {};
    dl::value_vector    value = {};
    bool invariant            = false;
};

using object_template = std::vector< object_attribute >;

const char* parse_template( const char*,
                            const char*,
                            object_template& ) noexcept (false);


/*
 * implementations
 */
template < typename T >
void object_attribute::into( T& x, bool allow_empty ) const noexcept (false) {
    // TODO: catch boost-get error,
    // then re-throw as something suitable with a better message
    // ?

    if (this->reprc != dl::typeinfo< T >::reprc) {
        throw std::invalid_argument( "mismatching reprc" );
    }

    if (this->value.which() == 0 && allow_empty) {
        /*
         * set to default-constructed of correct type
         *
         * this might need to change if ABSENT is important enough to
         * distinguish between default-constructed values and explicitly unset
         * values
         */
        x = T();
        return;
    }

    // TODO: if count > 1, fail with warning?
    using Vec = std::vector< T >;
    x = boost::get< Vec >( this->value ).front();
}

template <>
void object_attribute::into( dl::representation_code& x, bool allow_empty )
const noexcept (false) {
    if (this->value.which() == 0 && allow_empty)
        return;

    dl::ushort tmp;
    this->into( tmp, allow_empty );
    x = static_cast< dl::representation_code >( tmp );
}

template < typename T >
void object_attribute::into( std::vector< T >& v, bool allow_empty )
const noexcept (false)
{
    // TODO: catch boost-get error,
    // then re-throw as something suitable with a better message
    if (this->reprc != dl::typeinfo< T >::reprc) {
        throw std::invalid_argument( "mismatching reprc" );
    }

    if (this->value.which() == 0 && allow_empty) {
        return;
    }

    using Vec = std::vector< T >;
    v = boost::get< Vec >( this->value );
}

object_set parse_eflr( const char*, const char*, int ) noexcept (false);

}

#endif //DLISIO_EXT_TYPES_HPP
