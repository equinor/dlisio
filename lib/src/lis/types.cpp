#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <cassert>
#include <type_traits>

#include <endianness/endianness.h>

#include <dlisio/lis/types.h>

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

void assert_architecture() {
    /* While it's extremly unlikely that dlisio is run on
     * non 2's complement platform, nothing prevents us from
     * assuring it first
     */
    static_assert(~0 == -1, "Platform is not 2's complement");
}

template< typename T >
T twos_complement(bool sign, T number, std::uint8_t len) {
    /* Count 2's complement
     *
     * 2's complement of x can be counted as
     *   x, for x>=0
     *   ~x + 1, for x<0
     *
     * Note: when len < sizeof(T), ~ might cause type promotion to signed
     * (negative) int because not all existing bits belong to the number itself.
     * Thus when counting 2'complement we must assure unused significant bits
     * are set to 0 by applying the length mask.
     *
     * \param sign True if number is negative, false otherwise
     * \param number Unsigned value representing number bits: 0..0V..V
     * \param len Amount of valid bits in the number: len(V..V)
     */

    /* T should be of corresponding size with respect to len.
     * T must also have at least one bit more than len because sign is not
     * included into number bits pattern and overflow is expected for lowest
     * possible represented number (aka 00 with negative sign overflow to 100).
     */
    assert (sizeof(T) * 8 > len);

    T complement;
    if( sign ) {
        /* 0..01..1 where len(1..1) == len */
        const T mask = (1 << len) - 1;
        /* 0..0V..V -> 1..1N..N */
        const auto negation = ~number;
        /* 1..1N..N -> 0..1N..N */
        const auto ones_complement = negation & mask;
        complement = ones_complement + 1;
    } else {
        complement = number;
    }
    return complement;
}

} // namespace

const char* lis_i8(const char* xs, std::int8_t* x) {
    /* B.3. Code 56: 8-bit 2's complement Integer */
    assert_architecture();
    if (x) std::memcpy( x, xs, sizeof( std::int8_t ) );
    return xs + sizeof( std::int8_t );
}

const char* lis_i16(const char* xs, std::int16_t* x) {
    /* B.9. Code 79: 16-bit 2's complement Integer */
    assert_architecture();
    std::uint16_t ux;
    std::memcpy( &ux, xs, sizeof( std::int16_t ) );
    ux = ntoh( ux );
    if (x) std::memcpy( x, &ux, sizeof( std::int16_t ) );
    return xs + sizeof( std::int16_t );
}

const char* lis_i32(const char* xs, std::int32_t* x) {
    /* B.7. Code 73: 32-bit 2's complement Integer */
    assert_architecture();
    std::uint32_t ux;
    std::memcpy( &ux, xs, sizeof( std::int32_t ) );
    ux = ntoh( ux );
    if (x) std::memcpy( x, &ux, sizeof( std::int32_t ) );
    return xs + sizeof( std::int32_t );
}

const char* lis_f16(const char* xs, float* x) {
    /* B.1. Code 49: 16-bit Floating Point
     * Counting value of float number knowing sign, exponent and fraction.
     * - 1-bit sign
     * - 4-bit exponent, stored as unsigned int
     * - 11-bit fraction, 0.m, where m is 11-bit, sign is not included,
     *   stored as 2'complement
     */
    assert_architecture();

    std::uint16_t v;
    std::memcpy( &v, xs, sizeof( std::uint16_t ) );
    v = ntoh( v );

    /* Vxxxxxxx xxxxxxxx -> 0000000V */
    std::uint8_t sign_bit  = (v & 0x8000) >> 15;
    /* xxxxxxxx xxxxVVVV -> 0000VVVV */
    std::uint8_t exp_bits  = (v & 0x000F) >> 0;
    /* xVVVVVVV VVVVxxxx -> 00000VVV VVVVVVVV */
    std::uint16_t frac_bits = (v & 0x7FF0) >> 4;


    float sign = sign_bit ? -1.0 : 1.0;
    /* 0000VVVV -> VVVV.0 */
    float exponent = float( exp_bits );

    std::uint16_t frac_2_complement = twos_complement(sign_bit, frac_bits, 11);
    /* 00000VVV VVVVVVVV -> 0.VVVVVVVVVVV00000 */
    float fraction = frac_2_complement * std::pow( 2, -11 );

    if (x) *x = sign * fraction * std::pow( 2.0f, exponent );
    return xs + sizeof( std::uint16_t );
}

const char* lis_f32(const char* xs, float* x) {
    static_assert(
        std::numeric_limits< float >::is_iec559 && sizeof( float ) == 4,
        "Function assumes IEEE 754 32-bit float" );

    /** Calculating the value of a lis 32bit float [1]
     *
     * The sign (S) and the exponent (E) is trivial. The mantissa is in theory
     * easy too, but a couple of optimizations can be applied:
     *
     * The straightforward way of calculating the value of the mantissa (which
     * is a binary fraction) is to take the sum of all bits, each multiplied
     * by 2^n, where n = [-1, -nbits]:
     *
     *      std::uint8_t bf = 10100000 (binary fraction)
     *
     *      mantissa = 1 * 2^-1
     *               + 0 * 2^-2
     *               + 1 * 2^-3
     *               + 0 * 2^-4 ... 0 * 2^8
     *               = 0.5 + 0.125 = 0.625
     *
     * This is the same as reading the binary fraction as a signed 2's
     * compliment [2][3] and multiplying it by the precision/resolution, where
     * the precision is the value of rightmost bit in the fraction:
     *
     *      mantissa = (std::int8_t)bf * precision
     *               = 160 * 2^-8
     *               = 0.625;
     *
     * This is a bit more convoluted, but should be more performant as we
     * do a simple cast, compared to looping all 23 bits. Which would involve
     * 23 multiplications and a sum operation.
     *
     * The value of a lis' 32bit float is defined as [1]:
     *
     *      value = M * 2^(E - 128)   if S = 0
     *      value = M * 2^(127-E)     if S = 1
     *
     * We can now expand the mantissa (M) and factor in the precision into the
     * exponent part, which reduces the expression to:
     *
     *      value = bf * 2^-23 * 2^(E - 128) = bf * 2^(E-151)   if S = 0
     *      value = bf * 2^-23 * 2^(127-E)   = bf * 2^(104-E)   if S = 1
     *
     * [1] spec ref: LIS79 Appendix B.5
     *
     * [2] https://en.wikipedia.org/wiki/Floating-point_arithmetic#Floating-point_numbers
     *
     * [3] Note that the mantissa is only 23 bytes, while we work on 32bit
     * buffers. When trying to interpret the _value_ of the buffer as a signed
     * 2'compliments integer we need to be a bit cautious.
     *
     * For positive 2's compliment numbers, leading zeros do not count towards
     * the value so just make sure all excess bits are set to zero.
     *
     * For negative 2's compliment numbers the opposite is true. Leading ones
     * does not count towards the final value. Hence the excess bytes in the
     * buffer must be set to 1 before interpreting it as a signed 2's
     * compliment.
     */

    static constexpr std::uint8_t precision = 23;

    std::uint32_t u;
    std::memcpy( &u, xs, sizeof( std::uint32_t ) );
    u = ntoh( u );

    std::uint32_t sign_bit  = (u & 0x80000000);
    std::uint32_t frac_bits = (u & 0x007FFFFF);
    std::uint8_t  exp_bits  = (u & 0x7F800000) >> 23;

    std::uint32_t exponent = sign_bit ? (127 - exp_bits) : (exp_bits - 128);
    exponent -= precision;

    std::int32_t mask = sign_bit ? 0xFF800000 : 0;
    std::int32_t fraction = mask | frac_bits;

    float out = std::ldexp(fraction, exponent);

    if (x) *x = out;
    return xs + sizeof( float );
}

const char* lis_f32low(const char* xs, float* x) {
    static_assert(
        std::numeric_limits< float >::is_iec559 && sizeof( float ) == 4,
        "Function assumes IEEE 754 32-bit float" );

    /** Calculating mantissa (M) and final value:
     *
     *  M = F * precision = fraction * 2^(-15)
     *
     *  value = M * 2^E                     [1]
     *        = fraction * 2^(-15) * 2^E
     *        = fraction * 2^(E-15);
     *
     * [1] spec ref: LIS79 Appendix B.5
     */

    static constexpr std::uint8_t precision = 15;

    std::uint32_t u;
    std::memcpy( &u, xs, sizeof( std::uint32_t ) );
    u = ntoh( u );

    std::int16_t  fraction = (u & 0x0000FFFF);
    std::uint16_t exp_bits = (u & 0xFFFF0000) >> 16;

    float out = std::ldexp(fraction, exp_bits - precision);

    if (x) *x = out;
    return xs + sizeof( float );
}

const char* lis_f32fix(const char* xs, float*) {
    static_assert(
        std::numeric_limits< float >::is_iec559 && sizeof( float ) == 4,
        "Function assumes IEEE 754 32-bit float" );

    bool lis_f32fix_is_implemented = false;
    assert( lis_f32fix_is_implemented );

    return xs + sizeof( float );
}

const char* lis_string(const char* xs, const std::int32_t len, char* x) {
    /* Appendix B. Code 65: Alphanumeric */
    if (x) std::memcpy( x, xs, len );
    return xs + len;
}

const char* lis_byte(const char* xs, std::uint8_t* x) {
    /* B.4. Code 66: Byte Format */
    if (x) std::memcpy( x, xs, sizeof(std::uint8_t) );
    return xs + sizeof(std::uint8_t);
}

const char* lis_mask(const char* xs, const std::int32_t len, char* x) {
    /* B.8. Code 77: Mask */
    if (x) std::memcpy( x, xs, len );
    return xs + len;
}

