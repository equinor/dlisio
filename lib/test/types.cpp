#include <array>
#include <cstdint>
#include <limits>
#include <string>

#include <catch2/catch.hpp>

#include <dlisio/types.h>

TEST_CASE("signed short (8-bit)", "[type]") {
    const std::array< unsigned char[1], 7 > inputs = {{
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
        dlis_sshort( (char*)inputs[ i ], &v );
        CHECK( int(v) == int(expected[ i ]) );
    }
}

TEST_CASE("signed normal (16-bit)", "[type]") {
    const std::array< unsigned char[2], 8 > inputs = {{
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
        dlis_snorm( (char*)inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("signed long (32-bit)", "[type]") {
    const std::array< unsigned char[4], 8 > inputs = {{
        { 0x00, 0x00, 0x00, 0x00, }, // 0
        { 0x00, 0x00, 0x00, 0x01, }, // 1
        { 0x00, 0x00, 0x00, 0x59, }, // 89
        { 0x00, 0x00, 0x00, 0x99, }, // 153
        { 0x7F, 0xFF, 0xFF, 0xFF, }, // ~2.3b (int-max)
        { 0xFF, 0xFF, 0xFF, 0x67, }, // -153
        { 0xFF, 0xFF, 0xFF, 0xFF, }, // -1
        { 0x80, 0x00, 0x00, 0x00, }, // ~-2.3b (int-min)
    }};

    const std::array< std::int32_t, inputs.size() > expected = {
        0,
        1,
        89,
        153,
        std::numeric_limits< std::int32_t >::max(),
        -153,
        -1,
        std::numeric_limits< std::int32_t >::min(),
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        std::int32_t v;
        dlis_slong( (char*)inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("unsigned short (8-bit)", "[type]") {
    const std::array< unsigned char[1], 7 > inputs = {{
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
        dlis_ushort( (char*)inputs[ i ], &v );
        CHECK( int(v) == int(expected[ i ]) );
    }
}

TEST_CASE("unsigned normal (16-bit)", "[type]") {
    const std::array< unsigned char[2], 8 > inputs = {{
        { 0x00, 0x00 }, // 0
        { 0x00, 0x01 }, // 1
        { 0x00, 0x59 }, // 89
        { 0x00, 0x99 }, // 153
        { 0x7F, 0xFF }, // 32767
        { 0x80, 0x00 }, // 32768
        { 0xFF, 0x67 }, // 65383
        { 0xFF, 0xFF }, // uint-max
    }};

    const std::array< std::uint16_t, inputs.size() > expected = {
        0,
        1,
        89,
        153,
        32767,
        32768,
        65383,
        std::numeric_limits< std::uint16_t >::max(),
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        std::uint16_t v;
        dlis_unorm( (char*)inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("unsigned long (32-bit)", "[type]") {
    const std::array< unsigned char[4], 8 > inputs = {{
        { 0x00, 0x00, 0x00, 0x00, }, // 0
        { 0x00, 0x00, 0x00, 0x01, }, // 1
        { 0x00, 0x00, 0x00, 0x59, }, // 89
        { 0x00, 0x00, 0x00, 0x99, }, // 153
        { 0x7F, 0xFF, 0xFF, 0xFF, }, // 2147483647
        { 0x80, 0x00, 0x00, 0x00, }, // 2147483648
        { 0xFF, 0xFF, 0xFF, 0x67, }, // 4294967143
        { 0xFF, 0xFF, 0xFF, 0xFF, }, // uint-max
    }};

    const std::array< std::uint32_t, inputs.size() > expected = {
        0,
        1,
        89,
        153,
        2147483647,
        2147483648,
        4294967143,
        std::numeric_limits< std::uint32_t >::max(),
    };

    for( std::size_t i = 0; i < expected.size(); ++i ) {
        std::uint32_t v;
        dlis_ulong( (char*)inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("identifier (var-length string)", "[type]") {
    std::int32_t len;

    SECTION("empty string has zero length") {
        dlis_ident( "\0", &len, nullptr );
        CHECK( len == 0 );
    }

    SECTION("empty string does not affect output") {
        char str[] = "foobar";
        dlis_ident( "\0", &len, str );
        CHECK( str == std::string("foobar") );
    }

    SECTION("single-char string has length 1") {
        char str[] = "    ";
        dlis_ident( "\x01""a", &len, str );
        CHECK( str == std::string("a   ") );
        CHECK( len == 1 );
    }

    SECTION("single-char string has length 1") {
        char str[] = "    ";
        dlis_ident( "\x01""a", &len, str );
        CHECK( str == std::string("a   ") );
        CHECK( len == 1 );
    }

    SECTION("can be 255 chars long") {
        std::vector< char > str( 255, ' ' );
        const std::string expected =
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc "
            "tristique enim ac leo tristique, eu finibus enim pharetra. "
            "Donec ac elit congue, viverra mauris nec, maximus mauris. "
            "Integer molestie non mi eget bibendum. Nam dolor nibh, tincidunt "
            "quis metus.";

        const std::string in = "\xFF" + expected;

        dlis_ident( in.c_str(), &len, nullptr );
        CHECK( len == 255 );
        dlis_ident( in.c_str(), &len, str.data() );
        CHECK( std::string( str.begin(), str.end() ) == expected );
    }

    SECTION("returns pointer past read data") {
        const char in[] = "\x32"
                          "Lorem ipsum dolor sit amet, consectetur adipiscing";

        const char* noread = dlis_ident( in, &len, nullptr );
        CHECK( len == 50 );
        CHECK( std::intptr_t(noread) == std::intptr_t(in + sizeof( in ) - 1) );

        char out[ 50 ] = {};
        const char* withread = dlis_ident( in, &len, out );
        CHECK( len == 50 );
        CHECK( std::intptr_t(withread) == std::intptr_t(noread) );
    }
}
