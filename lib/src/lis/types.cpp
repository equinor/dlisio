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
    /* B.5. Code 68: 32-bit Floating Point
     * Counting value of float number knowing sign, exponent and fraction.
     * - 1-bit sign
     * - 8-bit exponent, stored as excess of 128 for positive numbers
     *   [real_exponet = stored_exponent_as_unsigned_int - 128]
     *   and as 1-complement excess of 128 for negatives
     *   [real_exponet = ~stored_exponent_as_unsigned_int - 128]
     * - 23-bit fraction (0.m, where m is 23-bit, sign is not included)
     *   stored as 2-complelement
     */
    assert_architecture();

    std::uint32_t v;
    std::memcpy( &v, xs, sizeof( std::uint32_t ) );
    v = ntoh( v );

    /* Vxxxxxxx 0xXX 0xXX 0xXX -> 0000000V */
    std::uint8_t sign_bit  = (v & 0x80000000) >> 31;
    /* xVVVVVVV Vxxxxxxx 0xXX 0xXX -> VVVVVVVV */
    std::uint8_t exp_bits  = (v & 0x7F800000) >> 23;
    /* 0xXX xVVVVVVV VVVVVVVV VVVVVVVV -> 0x00 0VVVVVVV VVVVVVVV VVVVVVVV */
    std::uint32_t frac_bits = (v & 0x007FFFFF) >> 0;

    float sign = sign_bit ? -1.0 : 1.0;

    std::uint8_t exponent_1_complement;
    if( sign_bit ) {
        exponent_1_complement = ~exp_bits;
        /* No "unused bits" adjustments are required for exponent because
         * exponent bits use all assigned for them space - 8 bits */
    } else {
        exponent_1_complement = exp_bits;
    }
    /* VVVVVVVV -> EEEEEEEE.0 */
    float exponent = float( exponent_1_complement ) - 128;

    std::uint32_t frac_2_complement = twos_complement(sign_bit, frac_bits, 23);
    /* 0x00 0VVVVVVV VVVVVVVV VVVVVVVV -> 0.VVVVVVVVVVVVVVVVVVVVVVV0 */
    float fraction = frac_2_complement * std::pow( 2, -23 );

    if (x) *x = sign * fraction * std::pow( 2.0f, exponent );
    return xs + sizeof( std::uint32_t );
}

const char* lis_f32low(const char* xs, float* x) {
    /* B.2. Code 50: 32-bit Low Resolution Floating Point
     * Counting value of float number knowing sign, exponent and fraction.
     * - 1-bit fraction sign
     * - 1-bit exponent sign
     * - 15-bit exponent (e, where e is 15-bit, sign is not included),
     *   stored as 2'complelement
     * - 15-bit fraction (0.m, where m is 15-bit, sign is not included)
     *   stored as 2'complelement
     */
    assert_architecture();

    std::uint32_t v;
    std::memcpy( &v, xs, sizeof( std::uint32_t ) );
    v = ntoh( v );

    /* 0xXX 0xXX Vxxxxxxx 0xXX -> 0000000V */
    std::uint8_t fraction_sign_bit  = (v & 0x00008000) >> 15;
    /* Vxxxxxxx 0xXX 0xXX 0xXX -> 0000000V */
    std::uint8_t exponent_sign_bit  = (v & 0x80000000) >> 31;
    /* xVVVVVVV VVVVVVVV 0xXX 0xXX -> 0VVVVVVV VVVVVVVV */
    std::uint16_t exp_bits  = (v & 0x7FFF0000) >> 16;
    /* 0xXX 0xXX xVVVVVVV VVVVVVVV -> 0VVVVVVV VVVVVVVV */
    std::uint16_t frac_bits = (v & 0x00007FFF) >> 0;

    float fraction_sign = fraction_sign_bit ? -1.0 : 1.0;
    float exponent_sign = exponent_sign_bit ? -1.0 : 1.0;

    std::uint16_t exp_2_complement =
        twos_complement(exponent_sign_bit, exp_bits, 15);
    /* 0VVVVVVVV VVVVVVVV -> VVVVVVVVVVVVVVV.0 */
    float exponent = exponent_sign * float( exp_2_complement );

    std::uint16_t frac_2_complement =
        twos_complement(fraction_sign_bit, frac_bits, 15);

    /* Expected logic:
     *    // 0VVVVVVV VVVVVVVV -> 0.VVVVVVVVVVVVVVV0
     *    float fraction = frac_2_complement * std::pow( 2.0, -15 );
     *    if (x) *x = fraction_sign * fraction * std::pow( 2.0f, exponent );
     * Problem is that in doing so we lose a bit of precision. Hence we need
     * to optimize calculations. Other types do not have this issue because
     * their boundary values are not near float boundaries.
     */
    if (x)
        *x = fraction_sign * frac_2_complement * std::pow(2.0f, exponent - 15);

    return xs + sizeof( std::uint32_t );
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

