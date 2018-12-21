#ifndef DLISIO_EXT_TYPES_HPP
#define DLISIO_EXT_TYPES_HPP

#include <complex>
#include <cstdint>
#include <tuple>
#include <type_traits>
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

/*
 * It's _very_ often needed to access the raw underlying type of the strong
 * type aliases for comparisons, literals, or conversions. dl::decay inspects
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
        using detail::strong_typedef< name, type >::strong_typedef; \
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

/*
 * Register useful compile time information on the types, such as mapping to
 * representation code
 */
template< typename T > struct typeinfo;
template<> struct typeinfo< dl::fshort > {
    static const representation_code reprc = dl::representation_code::fshort;
};
template<> struct typeinfo< dl::fsingl > {
    static const representation_code reprc = dl::representation_code::fsingl;
};
template<> struct typeinfo< dl::fsing1 > {
    static const representation_code reprc = dl::representation_code::fsing1;
};
template<> struct typeinfo< dl::fsing2 > {
    static const representation_code reprc = dl::representation_code::fsing2;
};
template<> struct typeinfo< dl::isingl > {
    static const representation_code reprc = dl::representation_code::isingl;
};
template<> struct typeinfo< dl::vsingl > {
    static const representation_code reprc = dl::representation_code::vsingl;
};
template<> struct typeinfo< dl::fdoubl > {
    static const representation_code reprc = dl::representation_code::fdoubl;
};
template<> struct typeinfo< dl::fdoub1 > {
    static const representation_code reprc = dl::representation_code::fdoub1;
};
template<> struct typeinfo< dl::fdoub2 > {
    static const representation_code reprc = dl::representation_code::fdoub2;
};
template<> struct typeinfo< dl::csingl > {
    static const representation_code reprc = dl::representation_code::csingl;
};
template<> struct typeinfo< dl::cdoubl > {
    static const representation_code reprc = dl::representation_code::cdoubl;
};
template<> struct typeinfo< dl::sshort > {
    static const representation_code reprc = dl::representation_code::sshort;
};
template<> struct typeinfo< dl::snorm > {
    static const representation_code reprc = dl::representation_code::snorm;
};
template<> struct typeinfo< dl::slong > {
    static const representation_code reprc = dl::representation_code::slong;
};
template<> struct typeinfo< dl::ushort > {
    static const representation_code reprc = dl::representation_code::ushort;
};
template<> struct typeinfo< dl::unorm > {
    static const representation_code reprc = dl::representation_code::unorm;
};
template<> struct typeinfo< dl::ulong > {
    static const representation_code reprc = dl::representation_code::ulong;
};
template<> struct typeinfo< dl::uvari > {
    static const representation_code reprc = dl::representation_code::uvari;
};
template<> struct typeinfo< dl::ident > {
    static const representation_code reprc = dl::representation_code::ident;
};
template<> struct typeinfo< dl::ascii > {
    static const representation_code reprc = dl::representation_code::ascii;
};
template<> struct typeinfo< dl::dtime > {
    static const representation_code reprc = dl::representation_code::dtime;
};
template<> struct typeinfo< dl::origin > {
    static const representation_code reprc = dl::representation_code::origin;
};
template<> struct typeinfo< dl::obname > {
    static const representation_code reprc = dl::representation_code::obname;
};
template<> struct typeinfo< dl::objref > {
    static const representation_code reprc = dl::representation_code::objref;
};
template<> struct typeinfo< dl::attref > {
    static const representation_code reprc = dl::representation_code::attref;
};
template<> struct typeinfo< dl::status > {
    static const representation_code reprc = dl::representation_code::status;
};
template<> struct typeinfo< dl::units > {
    static const representation_code reprc = dl::representation_code::units;
};

/*
 * Parsing and parsing input
 *
 * the strategy is to first parse the EFLR template and build a parsing guide,
 * expressed as the object_template. Later, this template instantiates the
 * default object in the set, and edits the fields as it goes along. The value
 * field can be zero or more values, so it's neatly stored as a vector, but the
 * *type* is indeterminate until the representation code is understood.
 *
 * The variant is a perfect fit for this.
 *
 * A variant-of-vector seems a better fit than vector-of-variants, both because
 * the max-size-overhead isn't so bad (all vectors are the same size), but the
 * type-resolution only has to be done once, and the unstructuring of the
 * vector can be contained inside the visitor.
 */
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

/*
 * The structure of an attribute as described in 3.2.2.1
 */
struct object_attribute {
    dl::ident           label = {};
    dl::uvari           count = dl::uvari{ 1 };
    representation_code reprc = representation_code::ident;
    dl::units           units = {};
    dl::value_vector    value = {};
    bool invariant            = false;

    /*
     * Into is a convenience function for extracting the value from an
     * attribute (during parsing), and writing into stricter objects,
     * modelled after the descriptions in chapter 5
     *
     * They also automate checking representation code underlying value
     * mismatch.
     */
    template < typename T >
    void into( T&, bool allow_empty ) const noexcept (false);
    template < typename T >
    void into( std::vector< T >&, bool allow_empty ) const noexcept (false);
};

/*
 * The template is just an ordered series of attributes, so just use a vector
 */
using object_template = std::vector< object_attribute >;

/*
 * All objects have an object name (3.2.2.1 figure 3-4)
 */
struct basic_object {
    dl::obname object_name;

    const std::string& get_name() const noexcept (true);
    void set_name( std::string ) noexcept (false);
};

/*
 * All objects should have a method set, that checks a property against the
 * labels defined by the standard, and sets the right member variable. It must
 * be named set with a compatible signature because it will be invoked from a
 * templated function
 */
struct file_header : basic_object {
    dl::ascii sequence_number;
    dl::ascii id;
    file_header& set( const object_attribute&, bool = false ) noexcept (false);
};

struct origin_object : basic_object {
    dl::ascii file_id;
    dl::ident file_set_name;
    dl::uvari file_set_number;
    dl::uvari file_number;
    dl::ident file_type;
    dl::ascii product;
    dl::ascii version;
    std::vector< dl::ascii > programs;
    /* descent - run nr */
    /* well-id */
    dl::ascii well_name;
    dl::ascii field_name;
    dl::unorm producer_code;
    dl::ascii producer_name;
    dl::ascii company;
    dl::ident namespace_name;
    dl::uvari namespace_version;

    origin_object&
    set( const object_attribute&, bool = false )
    noexcept (false);
};

struct channel : basic_object {
    boost::variant< dl::obname, dl::ascii > name;
    dl::representation_code reprc;
    dl::units units;
    std::vector< dl::ident > properties;
    std::vector< dl::uvari > dimension;
    std::vector< dl::uvari > element_limit;
    std::vector< dl::obname > axis;
    dl::objref source;

    channel& set( const object_attribute&, bool = false ) noexcept (false);
};

/*
 * The fall-through object - RP66 opens for private or company specific
 * records, or otherwise broken entries, that we don't want to discard.
 * Instead, just store the attributes in what is essentially a dictionary
 */
struct unknown_object : basic_object {
    std::vector< object_attribute > attributes;

    unknown_object&
    set( const object_attribute&, bool = false )
    noexcept (false);
};

/*
 * The object set, after parsing, is an (unordered?) collection of objects. In
 * parsing, more information is added through creating custom types, but the
 * fundamental restriction is one type per set.
 *
 * The variant-of-vectors is wells suited for this
 */
using object_vector = boost::variant<
    std::vector< file_header >,
    std::vector< origin_object >,
    std::vector< channel >,
    std::vector< unknown_object >
>;

struct object_set {
    int role; // TODO: enum class?
    dl::ident type;
    dl::ident name;
    dl::object_template tmpl;
    dl::object_vector objects;
};

const char* parse_template( const char* begin,
                            const char* end,
                            object_template& ) noexcept (false);


object_set parse_eflr( const char*, const char*, int ) noexcept (false);

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

}

#endif //DLISIO_EXT_TYPES_HPP
