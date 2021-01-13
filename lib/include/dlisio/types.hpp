#ifndef DLISIO_TYPES_HPP
#define DLISIO_TYPES_HPP

#include <complex>
#include <cstdint>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

#include <dlisio/types.h>

#include "strong-typedef.hpp"

namespace dlisio { namespace dlis {

namespace dl = dlisio::dlis;

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
    undef  = DLIS_UNDEF,
};

/*
 * It's _very_ often necessary to access the raw underlying type of the strong
 * type aliases for comparisons, literals, or conversions. dlis::decay inspects
 * the argument type and essentially static casts it, regardless of which dl
 * type comes in - it's an automation of static_cast<const value_type&>(x)
 * which otherwise would be repeated a million times
 *
 * The stong typedef's using from detail::strong_typedef has a more specific
 * overload available - the templated version is for completeness.
 */
template < typename T >
T& decay( T& x ) noexcept (true) {
    return x;
}

#define DLIS_REGISTER_TYPEALIAS(name, type) \
    struct name : detail::strong_typedef< name, type > { \
        name() = default; \
        name( const name& ) = default; \
        name( name&& )      = default; \
        name& operator = ( const name& ) = default; \
        name& operator = ( name&& )      = default; \
        using detail::strong_typedef< name, type >::strong_typedef; \
        using detail::strong_typedef< name, type >::operator =; \
        using detail::strong_typedef< name, type >::operator ==; \
        using detail::strong_typedef< name, type >::operator !=; \
    }; \
    inline const type& decay(const name& x) noexcept (true) { \
        return static_cast< const type& >(x); \
    } \
    inline type& decay(name& x) noexcept (true) { \
        return static_cast< type& >(x); \
    }

DLIS_REGISTER_TYPEALIAS(fshort, float)
DLIS_REGISTER_TYPEALIAS(isingl, float)
DLIS_REGISTER_TYPEALIAS(vsingl, float)
DLIS_REGISTER_TYPEALIAS(uvari,  std::int32_t)
DLIS_REGISTER_TYPEALIAS(origin, std::int32_t)
DLIS_REGISTER_TYPEALIAS(ident,  std::string)
DLIS_REGISTER_TYPEALIAS(ascii,  std::string)
DLIS_REGISTER_TYPEALIAS(units,  std::string)
DLIS_REGISTER_TYPEALIAS(status, std::uint8_t)

#undef DLIS_REGISTER_TYPEALIAS

template< typename T, int > struct validated;
template< typename T >
struct validated< T, 2 > {
    T V, A;

    bool operator == (const validated& o) const noexcept (true) {
        return this->V == o.V && this->A == o.A;
    }

    bool operator != (const validated& o) const noexcept (true) {
        return !(*this == o);
    }
};
template< typename T > struct validated< T, 3 > {
    T V, A, B;

    bool operator == (const validated& o) const noexcept (true) {
        return this->V == o.V && this->A == o.A && this->B == o.B;
    }

    bool operator != (const validated& o) const noexcept (true) {
        return !(*this == o);
    }
};

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

    bool operator == (const dtime& o) const noexcept (true) {
        return this->Y  == o.Y
            && this->TZ == o.TZ
            && this->M  == o.M
            && this->D  == o.D
            && this->H  == o.H
            && this->MN == o.MN
            && this->S  == o.S
            && this->MS == o.MS
        ;
    }

    bool operator != (const dtime& o) const noexcept (true) {
        return !(*this == o);
    }
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

    bool operator != (const obname& o) const noexcept (true) {
        return !(*this == o);
    }

    dl::ident fingerprint(const std::string& type) const noexcept (false) {
        const auto& origin = dl::decay(this->origin);
        const auto& copy = dl::decay(this->copy);
        const auto& id = dl::decay(this->id);

        int size;
        auto err = dlis_object_fingerprint_size(type.size(),
                                                type.data(),
                                                id.size(),
                                                id.data(),
                                                origin,
                                                copy,
                                                &size);

        if (err)
            throw std::invalid_argument("invalid argument");

        auto str = std::vector< char >(size);
        err = dlis_object_fingerprint(type.size(),
                                    type.data(),
                                    id.size(),
                                    id.data(),
                                    origin,
                                    copy,
                                    str.data());

        if (err)
            throw std::runtime_error("fingerprint: something went wrong");

        return dl::ident( std::string(str.begin(), str.end()) );
    }
};

struct objref {
    dl::ident  type;
    dl::obname name;

    bool operator == ( const objref& rhs ) const noexcept( true ) {
        return this->type == rhs.type
            && this->name == rhs.name;
    }

    bool operator != (const objref& o) const noexcept (true) {
        return !(*this == o);
    }

    dl::ident fingerprint() const noexcept (false) {
        return this->name.fingerprint(dl::decay(this->type));
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

    bool operator != (const attref& o) const noexcept (true) {
        return !(*this == o);
    }
};

/*
 * Register useful compile time information on the types for other template
 * functions to hook into
 */

template < typename T > struct typeinfo;
template <> struct typeinfo< dl::fshort > {
    static const representation_code reprc = dl::representation_code::fshort;
    constexpr static const char name[] = "fshort";
};
template <> struct typeinfo< dl::fsingl > {
    static const representation_code reprc = dl::representation_code::fsingl;
    constexpr static const char name[] = "fsingl";
};
template <> struct typeinfo< dl::fsing1 > {
    static const representation_code reprc = dl::representation_code::fsing1;
    constexpr static const char name[] = "fsing1";
};
template <> struct typeinfo< dl::fsing2 > {
    static const representation_code reprc = dl::representation_code::fsing2;
    constexpr static const char name[] = "fsing2";
};
template <> struct typeinfo< dl::isingl > {
    static const representation_code reprc = dl::representation_code::isingl;
    constexpr static const char name[] = "isingl";
};
template <> struct typeinfo< dl::vsingl > {
    static const representation_code reprc = dl::representation_code::vsingl;
    constexpr static const char name[] = "vsingl";
};
template <> struct typeinfo< dl::fdoubl > {
    static const representation_code reprc = dl::representation_code::fdoubl;
    constexpr static const char name[] = "fdoubl";
};
template <> struct typeinfo< dl::fdoub1 > {
    static const representation_code reprc = dl::representation_code::fdoub1;
    constexpr static const char name[] = "fdoub1";
};
template <> struct typeinfo< dl::fdoub2 > {
    static const representation_code reprc = dl::representation_code::fdoub2;
    constexpr static const char name[] = "fdoub2";
};
template <> struct typeinfo< dl::csingl > {
    static const representation_code reprc = dl::representation_code::csingl;
    constexpr static const char name[] = "csingl";
};
template <> struct typeinfo< dl::cdoubl > {
    static const representation_code reprc = dl::representation_code::cdoubl;
    constexpr static const char name[] = "cdoubl";
};
template <> struct typeinfo< dl::sshort > {
    static const representation_code reprc = dl::representation_code::sshort;
    constexpr static const char name[] = "sshort";
};
template <> struct typeinfo< dl::snorm > {
    static const representation_code reprc = dl::representation_code::snorm;
    constexpr static const char name[] = "snorm";
};
template <> struct typeinfo< dl::slong > {
    static const representation_code reprc = dl::representation_code::slong;
    constexpr static const char name[] = "slong";
};
template <> struct typeinfo< dl::ushort > {
    static const representation_code reprc = dl::representation_code::ushort;
    constexpr static const char name[] = "ushort";
};
template <> struct typeinfo< dl::unorm > {
    static const representation_code reprc = dl::representation_code::unorm;
    constexpr static const char name[] = "unorm";
};
template <> struct typeinfo< dl::ulong > {
    static const representation_code reprc = dl::representation_code::ulong;
    constexpr static const char name[] = "ulong";
};
template <> struct typeinfo< dl::uvari > {
    static const representation_code reprc = dl::representation_code::uvari;
    constexpr static const char name[] = "uvari";
};
template <> struct typeinfo< dl::ident > {
    static const representation_code reprc = dl::representation_code::ident;
    constexpr static const char name[] = "ident";
};
template <> struct typeinfo< dl::ascii > {
    static const representation_code reprc = dl::representation_code::ascii;
    constexpr static const char name[] = "ascii";
};
template <> struct typeinfo< dl::dtime > {
    static const representation_code reprc = dl::representation_code::dtime;
    constexpr static const char name[] = "dtime";
};
template <> struct typeinfo< dl::origin > {
    static const representation_code reprc = dl::representation_code::origin;
    constexpr static const char name[] = "origin";
};
template <> struct typeinfo< dl::obname > {
    static const representation_code reprc = dl::representation_code::obname;
    constexpr static const char name[] = "obname";
};
template <> struct typeinfo< dl::objref > {
    static const representation_code reprc = dl::representation_code::objref;
    constexpr static const char name[] = "objref";
};
template <> struct typeinfo< dl::attref > {
    static const representation_code reprc = dl::representation_code::attref;
    constexpr static const char name[] = "attref";
};
template <> struct typeinfo< dl::status > {
    static const representation_code reprc = dl::representation_code::status;
    constexpr static const char name[] = "status";
};
template <> struct typeinfo< dl::units > {
    static const representation_code reprc = dl::representation_code::units;
    constexpr static const char name[] = "units";
};

} // namespace dlis

} // namespace dlisio

#endif //DLISIO_TYPES_HPP
