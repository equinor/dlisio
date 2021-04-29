#ifndef DLISIO_LIS_TYPES_HPP
#define DLISIO_LIS_TYPES_HPP

#include <complex>
#include <cstdint>
#include <type_traits>
#include <utility>

#include <dlisio/lis/types.h>

#include "../strong-typedef.hpp"

namespace dlisio { namespace lis79 {
namespace lis = dlisio::lis79;

enum class representation_code : std::uint8_t {
    i8     = LIS_I8,
    i16    = LIS_I16,
    i32    = LIS_I32,
    f16    = LIS_F16,
    f32    = LIS_F32,
    f32low = LIS_F32LOW,
    f32fix = LIS_F32FIX,
    string = LIS_STRING,
    byte   = LIS_BYTE,
    mask   = LIS_MASK,
};

enum class fmtchr : std::uint8_t {
    eol      = LIS_FMT_EOL     ,
    i8       = LIS_FMT_I8      ,
    i16      = LIS_FMT_I16     ,
    i32      = LIS_FMT_I32     ,
    f16      = LIS_FMT_F16     ,
    f32      = LIS_FMT_F32     ,
    f32low   = LIS_FMT_F32LOW  ,
    f32fix   = LIS_FMT_F32FIX  ,
    string   = LIS_FMT_STRING  ,
    byte     = LIS_FMT_BYTE    ,
    mask     = LIS_FMT_MASK    ,
    suppress = LIS_FMT_SUPPRESS,
};

/* It's _very_ often necessary to access the raw underlying type of the strong
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

#define LIS_REGISTER_TYPEALIAS(name, type) \
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

LIS_REGISTER_TYPEALIAS(i8,     std::int8_t)
LIS_REGISTER_TYPEALIAS(i16,    std::int16_t)
LIS_REGISTER_TYPEALIAS(i32,    std::int32_t)
LIS_REGISTER_TYPEALIAS(f16,    float)
LIS_REGISTER_TYPEALIAS(f32,    float)
LIS_REGISTER_TYPEALIAS(f32low, float)
LIS_REGISTER_TYPEALIAS(f32fix, float)
LIS_REGISTER_TYPEALIAS(string, std::string)
LIS_REGISTER_TYPEALIAS(byte,   std::uint8_t)
//TODO what type matches best for mask?
LIS_REGISTER_TYPEALIAS(mask,   std::string)

#undef LIS_REGISTER_TYPEALIAS

/*
 * Register useful compile time information on the types for other template
 * functions to hook into
 */
template < typename T > struct typeinfo;
template <> struct typeinfo< lis::i8 > {
    static const representation_code reprc = lis::representation_code::i8;
    constexpr static const char name[] = "i8";
};
template <> struct typeinfo< lis::i16 > {
    static const representation_code reprc = lis::representation_code::i16;
    constexpr static const char name[] = "i16";
};
template <> struct typeinfo< lis::i32 > {
    static const representation_code reprc = lis::representation_code::i32;
    constexpr static const char name[] = "i32";
};
template <> struct typeinfo< lis::f16 > {
    static const representation_code reprc = lis::representation_code::f16;
    constexpr static const char name[] = "f16";
};
template <> struct typeinfo< lis::f32 > {
    static const representation_code reprc = lis::representation_code::f32;
    constexpr static const char name[] = "f32";
};
template <> struct typeinfo< lis::f32low > {
    static const representation_code reprc = lis::representation_code::f32low;
    constexpr static const char name[] = "f32low";
};
template <> struct typeinfo< lis::f32fix > {
    static const representation_code reprc = lis::representation_code::f32fix;
    constexpr static const char name[] = "f32fix";
};
template <> struct typeinfo< lis::string > {
    static const representation_code reprc = lis::representation_code::string;
    constexpr static const char name[] = "string";
};
template <> struct typeinfo< lis::byte > {
    static const representation_code reprc = lis::representation_code::byte;
    constexpr static const char name[] = "byte";
};
template <> struct typeinfo< lis::mask > {
    static const representation_code reprc = lis::representation_code::mask;
    constexpr static const char name[] = "mask";
};

} // namespace lis79

} // namespace dlisio

#endif // DLISIO_LIS_TYPES_HPP
