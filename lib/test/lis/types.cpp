#include <vector>
#include <array>
#include <cstring>
#include <sstream>
#include <iomanip>
#include <bitset>
#include <limits>

#include <catch2/catch.hpp>

#include <dlisio/lis/types.h>

#include "../bytes.hpp"

using namespace Catch::Matchers;

TEST_CASE("8-bit signed integer", "[type]") {
    const std::array< bytes< 1 >, 7 > inputs = {{
        { 0x00 }, // 0
        { 0x01 }, // 1
        { 0x59 }, // 89
        { 0x7F }, // 127 (int-max)
        { 0xA7 }, // -89
        { 0x80 }, // -128 (int-min)
        { 0xFF }, // -1
    }};

    const std::array< std::int8_t, inputs.size() > expected = {
        0,
        1,
        89,
        std::numeric_limits< std::int8_t >::max(),
        -89,
        std::numeric_limits< std::int8_t >::min(),
        -1,
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        std::int8_t v;
        lis_i8( inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("16-bit signed integer", "[type]") {
    const std::array< bytes< 2 >, 8 > inputs = {{
        { 0x00, 0x00 }, // 0
        { 0x00, 0x01 }, // 1
        { 0x00, 0x59 }, // 89
        { 0x00, 0x99 }, // 153
        { 0x7F, 0xFF }, // ~32k (int-max)
        { 0xFF, 0x67 }, // -153
        { 0xFF, 0xFF }, // -1
        { 0x80, 0x00 }, // ~-32k (int-min)
    }};

    const std::array< std::int16_t, inputs.size() > expected = {
        0,
        1,
        89,
        153,
        std::numeric_limits< std::int16_t >::max(),
        -153,
        -1,
        std::numeric_limits< std::int16_t >::min(),
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        std::int16_t v;
        lis_i16( inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("32-bit signed integer", "[type]") {
    const std::array< bytes< 4 >, 8 > inputs = {{
        { 0x00, 0x00, 0x00, 0x00 }, // 0
        { 0x00, 0x00, 0x00, 0x01 }, // 1
        { 0x00, 0x00, 0x00, 0x59 }, // 89
        { 0x00, 0x00, 0x00, 0x99 }, // 153
        { 0x7F, 0xFF, 0xFF, 0xFF }, // ~2.3b (int-max)
        { 0xFF, 0xFF, 0xFF, 0x67 }, // -153
        { 0xFF, 0xFF, 0xFF, 0xFF }, // -1
        { 0x80, 0x00, 0x00, 0x00 }, // ~-2.3b (int-min)
    }};

    const std::array< std::int32_t, inputs.size() > expected = {
        0,
        1,
        89,
        153,
        std::numeric_limits< std::int32_t >::max(),
        -153,
        -1,
        std::numeric_limits< ::int32_t >::min(),
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        std::int32_t v;
        lis_i32( inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("16-bit floating point", "[type]") {
    const std::array< unsigned char[2], 9 > inputs = {{
        { 0x00, 0x00 }, // 0
        { 0x40, 0x01 }, // 1
        { 0x00, 0x1B }, // 1
        { 0x7F, 0xF0 }, // ~1
        { 0x19, 0x24 }, // ~3.14
        { 0x4C, 0x88 }, // 153
        { 0xB3, 0x88 }, // -153
        { 0x7F, 0xFF }, // max
        { 0x80, 0x0F }, // min
    }};

    /* type fits well inside float boundaries, so no limit tests required */
    const std::array< float, inputs.size() > expected = {
        0,
        1,
        1,
        1,
        3.14,
        153,
        -153,
        32752,
        -32768,
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        float v;
        lis_f16( (char*)inputs[ i ], &v );
        CHECK_THAT(v, WithinRel(expected[ i ], 0.01f));
    }
}

TEST_CASE("32-bit floating point", "[type]") {

    SECTION("standard floats") {
        const std::array< bytes<4>, 8 > inputs = {{
            { 0x00, 0x00, 0x00, 0x00 }, // 0
            /* S = 0, E != 0, M == 0 */
            { 0x2A, 0x00, 0x00, 0x00 }, // 0
            /* S = 1, E (adjusted)== 0, M (bytes)== 0 */
            { 0xBF, 0x80, 0x00, 0x00 }, // -1
            { 0xBF, 0x40, 0x00, 0x00 }, // -1
            { 0x40, 0xC0, 0x00, 0x00 }, // 1
            { 0x41, 0x20, 0x00, 0x00 }, // 1
            { 0x44, 0x4C, 0x80, 0x00 }, // 153
            { 0xBB, 0xB3, 0x80, 0x00 }, // -153
        }};

        const std::array< float, inputs.size() > expected = {
            0,
            0,
            -1,
            -1,
            1,
            1,
            153,
            -153,
        };

        for( std::size_t i = 0; i < expected.size(); ++i ) {
            float v;
            lis_f32( inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    SECTION(" maximum LIS-stored positive number ") {
        /* S = 0, E (adjusted) == 127, M == 2^23 - 1 */
        const float expected = (1 - std::pow(2.0f, -23)) * std::pow(2.0f, 127);
        const bytes<4> input = { 0x7F, 0xFF, 0xFF, 0xFF };

        float v;
        lis_f32( input, &v );
        CHECK( v == expected );
        CHECK (v <= std::numeric_limits<float>::max());
    }

    SECTION(" minimum LIS-stored negative number ") {
        /* S = 1, E (adjusted) == 127, M == 2^23 */
        const float expected = -1 * std::pow(2.0f, 127);
        const bytes<4> input = { 0x80, 0x00, 0x00, 0x00 };

        float v;
        lis_f32( input, &v );
        CHECK( v == expected );
        CHECK (v > std::numeric_limits<float>::lowest());
    }

    SECTION(" near-smallest architecture-represented positive number ") {
        /* suspected to be the smallest, but no guarantee */
        /* S = 0, E (adjusted) == -126, M == 1, denormalized */
        const float expected = std::pow(2.0f, -23) * std::pow(2.0f, -126);
        const bytes<4> input = { 0x01, 0x00, 0x00, 0x01 };

        float v;
        lis_f32( input, &v );
        CHECK( v == expected );
        CHECK (v > 0);
        /* debug: the following works, but not asserting due to possible
           architecture differences */
        // CHECK (v == std::numeric_limits<float>::denorm_min());
    }

    SECTION(" smallest LIS-stored positive number: acceptable precision loss ") {
        /* Precision loss seems to happen because
         * in lis_f32 E has range [-128, 127]
         * in IEEE 754 float E has effective range [-126, 127]
         */

        /*  S = 0, E (adjusted) == -128, M == 1, denormalized */
        const float expected = std::pow(2.0f, -23) * std::pow(2.0f, -128);
        const bytes<4> input = { 0x00, 0x00, 0x00, 0x01 };

        float v;
        lis_f32( input, &v );
        CHECK( v == expected );

        // Failing: data is not 0, but due to precision loss is reported as 0
        // CHECK (v > 0);
    }
}

TEST_CASE("32-bit low-res floating point", "[type]") {

    SECTION("standard floats") {
        const std::array< bytes<4>, 5 > inputs = {{
            { 0x00, 0x00, 0x00, 0x00 }, // 0
            { 0x00, 0x08, 0x4C, 0x80 }, // 153
            { 0x00, 0x08, 0xB3, 0x80 }, // -153
            { 0xFF, 0xFF, 0x40, 0x00 }, // 0.25
            { 0xFF, 0xFF, 0xC0, 0x00 }, // -0.25
        }};

        const std::array< float, inputs.size() > expected = {
            0,
            153,
            -153,
            0.25,
            -0.25,
        };

        for( std::size_t i = 0; i < expected.size(); ++i ) {
            float v;
            lis_f32low( inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    /*
     * Low-resolution float numbers do not fit under float (or even double).
     * Tests below attempt to define the boundaries of that discrepancy.
     *
     * It's difficult to assure that presented numbers are actually
     * the max/min/smallest architecture-represented ones, not last due to
     * differences in space assigned to exponent and fraction, but they
     * should be somewhere near.
     *
     * Commented out tests are here to define the boundaries and substitute
     * ability to mark sections as 'shouldfail' in catch2.
     */

    SECTION(" near-maximum architecture-represented positive number ") {
        /* E = 2^7, M = 2^15 - 1 */

        /*
         * Expected is stored explicitly because some compilers overflow float
         * when calculating.
         *
         * (1 - std::pow(2.0f, -15)) * std::pow(2.0f, std::pow(2.0f, 7))
         */
        const float expected = 340271982327221393808117546439109771264.0f;
        const bytes<4> input = { 0x00, 0x80, 0x7F, 0xFF };

        float v;
        lis_f32low( input, &v );
        CHECK( v == expected );
        CHECK (v <= std::numeric_limits<float>::max());
    }

    SECTION(" near-minimum architecture-represented negative number ") {
        /* E = 2^7, M = -(2^15 - 1) */

        /*
         * Expected is stored explicitly because some compilers overflow float
         * when calculating.
         *
         * -(1 - std::pow(2.0f, -15)) * std::pow(2.0f, std::pow(2.0f, 7))
         */
        const float expected = -340271982327221393808117546439109771264.0f;
        const bytes<4> input = { 0x00, 0x80, 0x80, 0x01 };

        float v;
        lis_f32low( input, &v );
        CHECK( v == expected );
        CHECK (v >= std::numeric_limits<float>::lowest());
    }

    SECTION(" maximum LIS-stored positive number (data loss)") {
        /* E = 2^15 - 1, M = 2^15 - 1 */
        const float expected =
            (1 - std::pow(2.0f, -15)) * std::pow(2.0f, std::pow(2.0f, 15) - 1);
        const bytes<4> input = { 0x7F, 0xFF, 0x7F, 0xFF };

        float v;
        lis_f32low( input, &v );
        CHECK( v == expected );
        // Failing: too big number, can't be represented by float
        // CHECK (v <= std::numeric_limits<float>::max());
    }

    SECTION(" minimum LIS-stored negative number (data loss) ") {
        /* E = 2^15 - 1, M = -2^15*/
        const float expected = -1 * std::pow(2.0f, std::pow(2.0f, 15) - 1);
        const bytes<4> input = { 0x7F, 0xFF, 0x80, 0x00 };

        float v;
        lis_f32low( input, &v );
        CHECK( v == expected );
        // Failing: too big (modulo) number, can't be represented by float
        // CHECK (v >= std::numeric_limits<float>::lowest());
    }

    SECTION(" near-smallest architecture-represented positive number ") {
        /* E = -2^7, M = 1 */
        // Note: even smaller number seems to be with E = -2^7 - 6, which
        // shows that real boundaries are a bit bigger
        const float expected =
            std::pow(2.0f, -15) * std::pow(2.0f, -std::pow(2.0f, 7));
        const bytes<4> input = { 0xFF, 0x80, 0x00, 0x01 };

        float v;
        lis_f32low( input, &v );
        CHECK( v == expected );
        CHECK (v > 0);
    }

    SECTION(" smallest LIS-stored positive number (data loss) ") {
        /* E = -2^15, M = 1 */
        const float expected =
            std::pow(2.0f, -15) * std::pow(2.0f, -std::pow(2.0f, 15) );
        const bytes<4> input = { 0x80, 0x00, 0x00, 0x01 };

        float v;
        lis_f32low( input, &v );
        CHECK( v == expected );
        // Failing: data is not 0, but due to precision loss is reported as 0
        // CHECK (v > 0);
    }
}

TEST_CASE("32-bit fixed point", "[type]") {

    SECTION("standard floats") {
        const std::array< bytes<4>, 4 > inputs = {{
            { 0x00, 0x00, 0x00, 0x00 }, // 0
            { 0x00, 0x00, 0x80, 0x00 }, // 0.5
            { 0x00, 0x99, 0x40, 0x00 }, // 153.25
            { 0xFF, 0x66, 0xC0, 0x00 }, // -153.25
        }};

        const std::array< float, inputs.size() > expected = {
            0,
            0.5,
            153.25,
            -153.25,
        };

        for( std::size_t i = 0; i < expected.size(); ++i ) {
            float v;
            lis_f32fix( inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    SECTION(" Additional precision loss due to available bits number ") {
        /* Looks like we lose some precision due to type having 31 significant
         * digits and float having just 23 places in fraction. So, for example,
         * 2^9 - 2^(-16) already loses precision.
         *
         * This, however, shouldn't be a problem if doubles were used as their
         * fraction is 52 bits
         */
        SECTION(" No precision loss ") {
            /* 2^8 - 2^(-16) */
            const float expected1 = std::pow(2.0f, 8) - std::pow(2.0f, -16);
            const bytes<4> input1 = { 0x00, 0xFF, 0xFF, 0xFF };

            /* 2^8 */
            const float expected2 = std::pow(2.0f, 8);
            const bytes<4> input2 = { 0x01, 0x00, 0x00, 0x00 };

            float v1;
            lis_f32fix( input1, &v1 );
            CHECK( v1 == expected1 );

            float v2;
            lis_f32fix( input2, &v2 );
            CHECK( v2 == expected2 );

            CHECK( v1 != v2 );
        }

        SECTION(" Precision loss ") {
            /* 2^9 - 2^(-16) */
            const float expected1 = std::pow(2.0f, 9) - std::pow(2.0f, -16);
            const bytes<4> input1 = { 0x01, 0xFF, 0xFF, 0xFF };

            /* 2^9 */
            const float expected2 = std::pow(2.0f, 9);
            const bytes<4> input2 = { 0x02, 0x00, 0x00, 0x00 };

            float v1;
            lis_f32fix( input1, &v1 );
            CHECK( v1 == expected1 );

            float v2;
            lis_f32fix( input2, &v2 );
            CHECK( v2 == expected2 );

            // precision loss: different numbers get represented by same float
            // CHECK( v1 != v2 );
        }
    }

    SECTION(" maximum LIS-stored positive number (precision loss) ") {
        /* 2^15 - 2^(-16) */
        const float expected = 32768; // actually 2^15 - 2^(-16)
        const bytes<4> input = { 0x7F, 0xFF, 0xFF, 0xFF };

        float v;
        lis_f32fix( input, &v );
        CHECK( v == expected );
    }

    SECTION(" minimum LIS-stored negative number ") {
        /* -2^15 */
        const float expected = -32768;
        const bytes<4> input = { 0x80, 0x00, 0x00, 0x00 };

        float v;
        lis_f32fix( input, &v );
        CHECK( v == expected );
    }
}


TEST_CASE("String (Alphanumeric)", "[type]") {

    SECTION("empty string does not affect output") {
        char str[] = "foobar";

        const char ptr[] = "\0";
        std::uint8_t len = 0;

        lis_string( ptr, len, str );
        CHECK( str == std::string("foobar") );
    }

    SECTION("single-char string has length 1") {
        char str[] = "    ";

        std::uint8_t len = 1;
        const char ptr[] = "a";

        lis_string( ptr, len, str );
        CHECK( str == std::string("a   ") );
    }

    SECTION("can be 255 chars long") {
        std::vector< char > str( 255, ' ' );
        const char in[] =
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc "
            "tristique enim ac leo tristique, eu finibus enim pharetra. "
            "Donec ac elit congue, viverra mauris nec, maximus mauris. "
            "Integer molestie non mi eget bibendum. Nam dolor nibh, tincidunt "
            "quis metus.";

        const auto expected = std::string(reinterpret_cast< const char* >(in));

        std::uint8_t len = 255;
        lis_string( in, len, str.data() );
        CHECK( std::string( str.begin(), str.end() ) == expected );

    }

    SECTION("returns pointer past read data") {
        const char in[] = "Lorem ipsum dolor sit amet, consectetur adipiscing";

        std::uint8_t len = 50;
        const char* noread = lis_string( in, len, nullptr );
        CHECK( std::intptr_t(noread) == std::intptr_t(in + sizeof( in ) - 1) );

        char out[ 50 ] = {};
        const auto* withread = lis_string( in, len, out );
        CHECK( std::intptr_t(withread) == std::intptr_t(noread) );
    }
}

TEST_CASE("Byte - unsigned 8-bit integer", "[type]") {
    const std::array< bytes< 1 >, 7 > inputs = {{
        { 0x00 }, // 0
        { 0x01 }, // 1
        { 0x59 }, // 89
        { 0x7F }, // 127
        { 0xA7 }, // 167
        { 0x80 }, // 128
        { 0xFF }, // uint-max
    }};

    const std::array< std::uint8_t, inputs.size() > expected = {
        0,
        1,
        89,
        127,
        167,
        128,
        std::numeric_limits< std::uint8_t >::max(),
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        std::uint8_t v;
        lis_byte( inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("Mask - n-byte bitmask", "[type]") {

    SECTION("1 byte bitmask") {
        const char input = 0xAC;
        constexpr std::uint8_t len = 1;
        char out[len];

        lis_mask( &input, len, out );
        CHECK( (out[0] & 0x02) >> 1 == 0 );
        CHECK( (out[0] & 0x04) >> 2 == 1 );
    }

    SECTION("Process Indicators bitmask") {
        /* Note: in specification mask type is used only for
         * 4.1.6 (l) Process Indicators. */

        constexpr std::uint8_t len = 5;
        const bytes<len> input = { 0x41, 0x42, 0x43, 0x44, 0x45};
        char out[len];

        lis_mask( input, len, out );
        CHECK_THAT( out, BytesEquals(input) );
    }

}

TEST_CASE("Size of type", "[protocol]") {
    SECTION("8-bit signed integer (lis::i8)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_I8) == LIS_SIZEOF_I8 );
    }
    SECTION("16-bit signed integer (lis::i16)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_I16) == LIS_SIZEOF_I16 );
    }
    SECTION("32-bit signed integer (lis::i32)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_I32) == LIS_SIZEOF_I32 );
    }
    SECTION("16-bit floating point (lis::f16)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_F16) == LIS_SIZEOF_F16 );
    }
    SECTION("32-bit floating point (lis::f32)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_F32) == LIS_SIZEOF_F32 );
    }
    SECTION("32-bit low resolution floating point (lis::f32low)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_F32LOW) == LIS_SIZEOF_F32LOW );
    }
    SECTION("32-bit fixed point (lis::f32fix)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_F32FIX) == LIS_SIZEOF_F32FIX );
    }
    SECTION("Alphanumeric (lis::string)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_STRING) == LIS_SIZEOF_STRING );
    }
    SECTION("Byte (lis::byte)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_BYTE) == LIS_SIZEOF_BYTE );
    }
    SECTION("Mask - bitmask (lis::mask)", "[protocol]") {
        CHECK( lis_sizeof_type(LIS_MASK) == LIS_SIZEOF_MASK );
    }
    SECTION("Undefined code", "[protocol]") {
        CHECK( lis_sizeof_type(34) == -1 );
    }
}
