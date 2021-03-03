#include <vector>
#include <array>
#include <cstring>
#include <sstream>
#include <iomanip>
#include <bitset>

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
    const std::array< unsigned char[2], 7 > inputs = {{
        { 0x00, 0x00 }, // 0
        { 0x7F, 0xF0 }, // 1
        { 0x19, 0x24 }, // ~3.14
        { 0x4C, 0x88 }, // 153
        { 0xB3, 0x88 }, // -153
        { 0x7F, 0xFF }, // max
        { 0x80, 0x0F }, // min
    }};

    const std::array< float, inputs.size() > expected = {
        0,
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
        CHECK( v == Approx( expected[ i ] ).epsilon(0.001) );
    }
}

TEST_CASE("32-bit floating point", "[type]") {
    const std::array< bytes<4>, 4 > inputs = {{
        { 0x00, 0x00, 0x00, 0x00 }, // 0
        /* S = 0, E != 0, M == 0 */
        { 0x2A, 0x00, 0x00, 0x00 }, // 0
        { 0x44, 0x4C, 0x80, 0x00 }, // 153
        { 0xBB, 0xB3, 0x80, 0x00 }, // -153
    }};

    const std::array< float, inputs.size() > expected = {
        0,
        0,
        153,
        -153,
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        float v;
        lis_f32( inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("32-bit low-res floating point", "[type]") {
    const std::array< bytes<4>, 3 > inputs = {{
        { 0x00, 0x00, 0x00, 0x00 }, // 0
        { 0x00, 0x08, 0x4C, 0x80 }, // 153
        { 0x00, 0x08, 0xB3, 0x80 }, // -153
    }};

    const std::array< float, inputs.size() > expected = {
        0,
        153,
        -153,
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        float v;
        lis_f32low( inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("32-bit fixed point", "[type]") {
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

