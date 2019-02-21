#ifndef DLISIO_EXT_TYPES_HPP
#define DLISIO_EXT_TYPES_HPP

#include <complex>
#include <cstdint>
#include <exception>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

#include <mpark/variant.hpp>

#include <dlisio/types.h>

#include "strong-typedef.hpp"

namespace dl {

struct not_implemented : public std::logic_error {
    explicit not_implemented( const std::string& msg ) :
        logic_error( "Not implemented yet: " + msg )
    {}
};

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
 * It's _very_ often necessary to access the raw underlying type of the strong
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
 * Register useful compile time information on the types for other template
 * functions to hook into
 */

template < typename T > struct typeinfo;
template <> struct typeinfo< dl::fshort > {
    static const representation_code reprc = dl::representation_code::fshort;
    constexpr static const char* name = "fshort";
};
template <> struct typeinfo< dl::fsingl > {
    static const representation_code reprc = dl::representation_code::fsingl;
    constexpr static const char* name = "fsingl";
};
template <> struct typeinfo< dl::fsing1 > {
    static const representation_code reprc = dl::representation_code::fsing1;
    constexpr static const char* name = "fsing1";
};
template <> struct typeinfo< dl::fsing2 > {
    static const representation_code reprc = dl::representation_code::fsing2;
    constexpr static const char* name = "fsing2";
};
template <> struct typeinfo< dl::isingl > {
    static const representation_code reprc = dl::representation_code::isingl;
    constexpr static const char* name = "isingl";
};
template <> struct typeinfo< dl::vsingl > {
    static const representation_code reprc = dl::representation_code::vsingl;
    constexpr static const char* name = "vsingl";
};
template <> struct typeinfo< dl::fdoubl > {
    static const representation_code reprc = dl::representation_code::fdoubl;
    constexpr static const char* name = "fdoubl";
};
template <> struct typeinfo< dl::fdoub1 > {
    static const representation_code reprc = dl::representation_code::fdoub1;
    constexpr static const char* name = "fdoub1";
};
template <> struct typeinfo< dl::fdoub2 > {
    static const representation_code reprc = dl::representation_code::fdoub2;
    constexpr static const char* name = "fdoub2";
};
template <> struct typeinfo< dl::csingl > {
    static const representation_code reprc = dl::representation_code::csingl;
    constexpr static const char* name = "csingl";
};
template <> struct typeinfo< dl::cdoubl > {
    static const representation_code reprc = dl::representation_code::cdoubl;
    constexpr static const char* name = "cdoubl";
};
template <> struct typeinfo< dl::sshort > {
    static const representation_code reprc = dl::representation_code::sshort;
    constexpr static const char* name = "sshort";
};
template <> struct typeinfo< dl::snorm > {
    static const representation_code reprc = dl::representation_code::snorm;
    constexpr static const char* name = "snorm";
};
template <> struct typeinfo< dl::slong > {
    static const representation_code reprc = dl::representation_code::slong;
    constexpr static const char* name = "slong";
};
template <> struct typeinfo< dl::ushort > {
    static const representation_code reprc = dl::representation_code::ushort;
    constexpr static const char* name = "ushort";
};
template <> struct typeinfo< dl::unorm > {
    static const representation_code reprc = dl::representation_code::unorm;
    constexpr static const char* name = "unorm";
};
template <> struct typeinfo< dl::ulong > {
    static const representation_code reprc = dl::representation_code::ulong;
    constexpr static const char* name = "ulong";
};
template <> struct typeinfo< dl::uvari > {
    static const representation_code reprc = dl::representation_code::uvari;
    constexpr static const char* name = "uvari";
};
template <> struct typeinfo< dl::ident > {
    static const representation_code reprc = dl::representation_code::ident;
    constexpr static const char* name = "ident";
};
template <> struct typeinfo< dl::ascii > {
    static const representation_code reprc = dl::representation_code::ascii;
    constexpr static const char* name = "ascii";
};
template <> struct typeinfo< dl::dtime > {
    static const representation_code reprc = dl::representation_code::dtime;
    constexpr static const char* name = "dtime";
};
template <> struct typeinfo< dl::origin > {
    static const representation_code reprc = dl::representation_code::origin;
    constexpr static const char* name = "origin";
};
template <> struct typeinfo< dl::obname > {
    static const representation_code reprc = dl::representation_code::obname;
    constexpr static const char* name = "obname";
};
template <> struct typeinfo< dl::objref > {
    static const representation_code reprc = dl::representation_code::objref;
    constexpr static const char* name = "objref";
};
template <> struct typeinfo< dl::attref > {
    static const representation_code reprc = dl::representation_code::attref;
    constexpr static const char* name = "attref";
};
template <> struct typeinfo< dl::status > {
    static const representation_code reprc = dl::representation_code::status;
    constexpr static const char* name = "status";
};
template <> struct typeinfo< dl::units > {
    static const representation_code reprc = dl::representation_code::units;
    constexpr static const char* name = "units";
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
using value_vector = mpark::variant<
    mpark::monostate,
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
 * Some records (e.g. the Frame Logical Record in 5.7 FRAME) have a
 * representation restriction, but in the wild other compatible data types are
 * used as well. Furthermore, some attributes such as the SPACING attribute of
 * the FRAME record are non-sensical if not numeric.
 *
 * To accomodate this, represent these values as a variant of either integral
 * or numeric types.
 *
 * The representation restriction is denoted as R= in Chapter 5 - Static and
 * Frame Data
 */
using numeric = mpark::variant<
    dl::fshort,
    dl::fsingl,
    dl::fsing1,
    dl::fsing2,
    dl::isingl,
    dl::vsingl,
    dl::fdoubl,
    dl::fdoub1,
    dl::fdoub2,
    dl::csingl,
    dl::cdoubl,
    dl::sshort,
    dl::snorm,
    dl::slong,
    dl::ushort,
    dl::unorm,
    dl::ulong,
    dl::uvari
>;

using integral = mpark::variant<
    dl::sshort,
    dl::snorm,
    dl::slong,
    dl::ushort,
    dl::unorm,
    dl::ulong,
    dl::uvari
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
     * into is a convenience function for extracting the value from an
     * attribute (during parsing), and writing into stricter objects,
     * modelled after the descriptions in chapter 5.
     *
     * The into helper automates the checking and unpacking of optionals,
     * variants, and vectors, into the various members of the object types.
     * This allows unpacking objects from attributes to look like this:
     *
     * void read( const object_attribute& attr ) {
     *          if (label == "LABEL1") attr.into( this->label1 );
     *     else if (label == "LABEL2") attr.into( this->label2 );
     *     ...
     *     else throw;
     * }
     *
     * attr.into picks the right conversion depending on label being a variant,
     * vector, raw value, or optional.
     *
     * They also automate checking representation code underlying value
     * mismatch.
     *
     * TODO: give decent error messages and exceptions on expected and actual
     * representation code mismatch
     */
    template < typename T >
    void into( T& )                      const noexcept (false);
    template < typename... T >
    void into( mpark::variant< T... >& ) const noexcept (false);
    template < typename T >
    void into( std::vector< T >& )       const noexcept (false);

    /*
     * Sometimes the variant or optional is unset, which means forming a
     * reference to the underlying object will throw a mpark::get exception. In
     * these cases, and for exception safety, read from the attribute into a
     * temporary, and return that, to help invoke the variant/optional-assign
     * semantics
     */
    template < typename T >
    T into() const noexcept (false);

};

/*
 * The Object Set Template (3.2.1 EFLR: General layout) is just an ordered set
 * of attributes, so just alias a vector
 */
using object_template = std::vector< object_attribute >;

/*
 * Parsing output and semantic objects
 *
 * C++ representation of the set of logical record types (listed in Appendix A
 * - Logical Record Types, described in Chapter 5 - Static and Frame Data)
 *
 * They all derive from basic_object, but that's just a low-syntactical
 * overhead way of adding the object-name field, which is present in every
 * object. In fact, this object-name preceeds the attributes and is introduced
 * by the component descriptor (3.2.2.1 Component Descriptor figure 3-4). It
 * carries no other semantic or operational significance and should be
 * considered an implementation detail.
 *
 * While not very clear on the matter, in practice every attribute of even
 * well-specified object types (such as CHANNEL) can be absent. Because of
 * this, every attribute is an Optional. The lack of a value in the optional
 * means either that the attribute is explicitly marked absent (see
 * DLIS_ROLE_ABSATR), or not present at all in the object template. It is
 * impossible to distinguish these cases without consulting the template
 * itself.
 *
 * The member variables are designed and enriched with the intention that
 * member variables are set with the object_attribute::into functions. Other
 * code expects that all objects have the two methods set and remove:
 *
 * void set( const object_attribute& );
 * void remove( const object_attribute& );
 *
 * These should map object attribute label to the right member variable, and
 * set/unset respectively - remove is called when encoutering ABSATR, set
 * otherwise.
 */

/*
 * All objects have an object name (3.2.2.1 Component Descriptor figure 3-4)
 */
struct basic_object {
    void set( const object_attribute& )    noexcept (false);
    void remove( const object_attribute& ) noexcept (false);

    std::size_t len() const noexcept (true);
    const dl::object_attribute&
    at( const std::string& ) const noexcept (false);

    dl::obname object_name;
    std::vector< object_attribute > attributes;
};

/*
 * The object set, after parsing, is an (unordered?) collection of objects. In
 * parsing, more information is added through creating custom types, but the
 * fundamental restriction is one type per set.
 *
 * The variant-of-vectors is wells suited for this
 */
using object_vector = std::vector< basic_object >;

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


object_set parse_objects( const char*, const char* ) noexcept (false);

/*
 * implementations
 */
template < typename T >
void object_attribute::into( T& x ) const noexcept (false) {
    // TODO: catch variant::get error,
    // then re-throw as something suitable with a better message
    // ?
    if (this->reprc != dl::typeinfo< T >::reprc) {
        std::string msg = std::to_string( static_cast< int >( this->reprc ) )
                        + " is not " + dl::typeinfo< T >::name
                        ;
        throw std::invalid_argument( "[x] mismatching reprc: " + msg );
    }

    if (mpark::holds_alternative< mpark::monostate >(this->value))
        return;

    using Vec = std::vector< T >;
    x = mpark::get< Vec >( this->value ).front();
}

template <>
inline void object_attribute::into( dl::representation_code& x )
const noexcept (false) {
    x = static_cast< dl::representation_code >( this->into< dl::ushort >() );
}

template < typename ... T >
void object_attribute::into( mpark::variant< T... >& x ) const noexcept (false)
{
    if (mpark::holds_alternative< mpark::monostate >(this->value))
        return;

    /*
     * "for-each-argument"
     *
     * https://isocpp.org/blog/2015/01/for-each-argument-sean-parent
     *
     * compile-time generate a series of if-expressions which is conceptually a
     * switch over the variadic template T, mapped to every type's
     * representation code.
     *
     * This is to avoid having one overload of the into function for every
     * unique variant.
     *
     * essentially boils down to
     *
     *      if (reprc == typeinfo< T1 >::reprc) {}
     * else if (reprc == typeinfo< T2 >::reprc) {}
     * else if (reprc == typeinfo< T3 >::reprc) {}
     * ...
     *
     * for all combinations of valid variants
     */

    bool found = false;
    using sequencer = int[];
    static_cast< void >( sequencer {
        ((this->reprc == dl::typeinfo< T >::reprc)
        ? x = this->into< T >(), found = true, 0
        : 0) ...
    });

    if (!found)
        throw std::invalid_argument("{} requested, but variant held {}");
}

template < typename T >
void object_attribute::into( std::vector< T >& v )
const noexcept (false)
{
    // TODO: catch variant::get error,
    // then re-throw as something suitable with a better message
    if (this->reprc != dl::typeinfo< T >::reprc) {
        throw std::invalid_argument( "[vec] mismatching reprc" );
    }

    if (mpark::holds_alternative< mpark::monostate >(this->value))
        return;

    using Vec = std::vector< T >;
    v = mpark::get< Vec >( this->value );
}

template < typename T >
T object_attribute::into() const noexcept (false) {
    T tmp;
    this->into( tmp );
    return tmp;
}

}

#endif //DLISIO_EXT_TYPES_HPP
