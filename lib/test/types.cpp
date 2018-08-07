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

TEST_CASE("variable-length unsigned int", "[type]") {
    SECTION("1-byte") {
        const std::array< unsigned char[1], 4 > in = {{
            { 0x00 }, // 0
            { 0x01 }, // 1
            { 0x2E }, // 46
            { 0x7F }, // 127
        }};

        const std::array< std::int32_t, in.size() > expected = {
            0,
            1,
            46,
            127
        };

        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::int32_t v;
            const char* end = dlis_uvari( (char*)in[ i ], &v );
            CHECK( v == expected[ i ] );
            CHECK( std::intptr_t(end) == std::intptr_t((char*)in[ i ] + 1) );
        }
    }

    SECTION("2-byte") {
        const std::array< unsigned char[2], 7 > in = {{
            { 0x80, 0x00 }, // 0
            { 0x80, 0x01 }, // 1
            { 0x80, 0x2E }, // 46
            { 0x80, 0x7F }, // 127
            { 0x81, 0x00 }, // 256
            { 0x8F, 0xFF }, // 4095
            { 0xBF, 0xFF }, // 16383 (int-max)
        }};

        const std::array< std::int32_t, in.size() > expected = {
            0,
            1,
            46,
            127,
            256,
            4095,
            16383,
        };

        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::int32_t v;
            const char* end = dlis_uvari( (char*)in[ i ], &v );
            CHECK( v == expected[ i ] );
            CHECK( std::intptr_t(end) == std::intptr_t((char*)in[ i ] + 2) );
        }
    }

    SECTION("4-byte") {
        const std::array< unsigned char[4], 9 > in = {{
            { 0xC0, 0x00, 0x00, 0x00 }, // 0
            { 0xC0, 0x00, 0x00, 0x01 }, // 1
            { 0xC0, 0x00, 0x00, 0x2E }, // 46
            { 0xC0, 0x00, 0x00, 0x7F }, // 127
            { 0xC0, 0x00, 0x01, 0x00 }, // 256
            { 0xC0, 0x00, 0x8F, 0xFF }, // 36863
            { 0xC1, 0x00, 0x00, 0x00 }, // 16777216
            { 0xF0, 0x00, 0xBF, 0xFF }, // 805355519
            { 0xFF, 0xFF, 0xFF, 0xFF }, // 1073741823 (int-max)
        }};

        const std::array< std::int32_t, in.size() > expected = {
            0,
            1,
            46,
            127,
            256,
            36863,
            16777216,
            805355519,
            1073741823,
        };

        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::int32_t v;
            const char* end = dlis_uvari( (char*)in[ i ], &v );
            CHECK( v == expected[ i ] );
            CHECK( std::intptr_t(end) == std::intptr_t((char*)in[ i ] + 4) );
        }
    }
}

TEST_CASE("short float (16-bit)", "[type]") {
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
        dlis_fshort( (char*)inputs[ i ], &v );
        CHECK( v == Approx( expected[ i ] ).epsilon(0.001) );
    }
}

TEST_CASE("IEEE 754 single precision float (32-bit)", "[type]") {
    SECTION("parsed floats match expected result") {
        const std::array< unsigned char[4], 7 > inputs = {{
            { 0x00, 0x00, 0x00, 0x00 }, // 0
            { 0x80, 0x00, 0x00, 0x00 }, // -0
            { 0x40, 0x49, 0x0F, 0xDB }, // 3.1415927410125732421875
            { 0x43, 0x19, 0x00, 0x00 }, // 153
            { 0xC3, 0x19, 0x00, 0x00 }, // -153
            { 0x7F, 0x80, 0x00, 0x00 }, // infinity
            { 0xFF, 0x80, 0x00, 0x00 }, // -infinity
        }};

        const std::array< float, inputs.size() > expected = {
            0,
            -0,
            3.1415927410125732421875,
            153,
            -153,
            std::numeric_limits< float >::infinity(),
            -std::numeric_limits< float >::infinity(),
        };

        for( std::size_t i = 0; i < expected.size(); ++i ) {
            float v;
            dlis_fsingl( (char*)inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    SECTION("nan input gives nan value") {
        const std::array< unsigned char[4], 4 > inputs = {{
            { 0x7F, 0x80, 0x00, 0x01 },
            { 0x7F, 0x80, 0x00, 0x02 },
            { 0xFF, 0x80, 0x00, 0x03 },
            { 0xFF, 0x80, 0x00, 0x04 },
        }};

        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            float v;
            dlis_fsingl( (char*)inputs[ i ], &v );
            CHECK( std::isnan( v ) );
        }
    }
}

TEST_CASE("IEEE 754 double precision float (64-bit)", "[type]") {
    SECTION("parsed doubles match expected result") {
        const std::array< unsigned char[8], 7 > inputs = {{
            { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, // 0
            { 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, // -0
            { 0x40, 0x09, 0x21, 0xFB, 0x54, 0x44, 0x2D, 0x18 }, // ~3.14
            { 0x40, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 }, // 153
            { 0xC0, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 }, // -153
            { 0x7F, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, // infinity
            { 0xFF, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, // -infinity
        }};

        const std::array< double, inputs.size() > expected = {
            0,
            -0,
            3.1415926535897930,
            153,
            -153,
            std::numeric_limits< double >::infinity(),
            -std::numeric_limits< double >::infinity(),
        };

        for( std::size_t i = 0; i < expected.size(); ++i ) {
            double v;
            dlis_fdoubl( (char*)inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    SECTION("nan input gives nan value") {
        const std::array< unsigned char[8], 4 > inputs = {{
            { 0x7F, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 },
            { 0x7F, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02 },
            { 0xFF, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03 },
            { 0xFF, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04 },
        }};

        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            double v;
            dlis_fdoubl( (char*)inputs[ i ], &v );
            CHECK( std::isnan( v ) );
        }
    }
}

TEST_CASE("ibm single precision float", "[type]") {
    const std::array< unsigned char[4], 5 > inputs = {{
        { 0x00, 0x00, 0x00, 0x00 }, // 0
        { 0x80, 0x00, 0x00, 0x00 }, // -0
        { 0x42, 0x99, 0x00, 0x00 }, // 153
        { 0xC2, 0x99, 0x00, 0x00 }, // -153
        { 0xC2, 0x76, 0xA0, 0x00 }, // -118.625
    }};

    const std::array< float, inputs.size() > expected = {
        0.0,
        -0.0,
        153.0,
        -153.0,
        -118.625,
    };

    for( std::size_t i = 0; i < inputs.size(); ++i ) {
        float v;
        dlis_isingl( (char*)inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("vax single precision float", "[type]") {
    const std::array< unsigned char[4], 3 > inputs = {{
        { 0x00, 0x00, 0x00, 0x00 }, // 0
        { 0x0C, 0x44, 0x00, 0x80 }, // 153
        { 0x0C, 0xC4, 0x00, 0x80 }, // -153
    }};

    const std::array< float, inputs.size() > expected = {
        0.0,
        153,
        -153,
    };

    for( std::size_t i = 0; i < inputs.size(); ++i ) {
        float v;
        dlis_vsingl( (char*)inputs[ i ], &v );
        CHECK( v == expected[ i ] );
    }
}

TEST_CASE("complex and validated single precision floats", "[type]") {
    const std::array< unsigned char, 28 > inputs = {
        0x00, 0x00, 0x00, 0x00, // 0
        0x80, 0x00, 0x00, 0x00, // -0
        0x40, 0x49, 0x0F, 0xDB, // 3.1415927410125732421875
        0x43, 0x19, 0x00, 0x00, // 153
        0xC3, 0x19, 0x00, 0x00, // -153
        0x7F, 0x80, 0x00, 0x00, // infinity
        0xFF, 0x80, 0x00, 0x00, // -infinity
    };

    SECTION("validaed single precision float") {
        for( std::size_t i = 0; i < inputs.size() / sizeof( float ); ++i ) {
            const char* xs = (char*)inputs.data() + i * sizeof( float );
            float v, a;
            float x, y;
            dlis_fsing1( xs, &v, &a );
            const char* ys = dlis_fsingl( xs, &x );
                             dlis_fsingl( ys, &y );
            CHECK( v == x );
            CHECK( a == y );
        }
    }

    SECTION("two-way validated single precision float") {
        for( std::size_t i = 0; i < inputs.size() / sizeof( float ); ++i ) {
            const char* xs = (char*)inputs.data() + i * sizeof( float );
            float v, a, b;
            float x, y, z;
            dlis_fsing2( xs, &v, &a, &b );
            const char* ys = dlis_fsingl( xs, &x );
            const char* zs = dlis_fsingl( ys, &y );
                             dlis_fsingl( zs, &z );
            CHECK( v == x );
            CHECK( a == y );
            CHECK( b == z );
        }
    }

    SECTION("single precision complex float") {
        for( std::size_t j = 0; j < inputs.size() / sizeof( float ); ++j ) {
            const char* xs = (char*)inputs.data() + j * sizeof( float );
            float r, i;
            float x, y;
            dlis_fsing1( xs, &r, &i );
            const char* ys = dlis_fsingl( xs, &x );
                             dlis_fsingl( ys, &y );
            CHECK( r == x );
            CHECK( i == y );
        }
    }
}

TEST_CASE("complex and validaed double precision floats", "[type]") {
    const std::array< unsigned char, 56 > inputs = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0
        0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // -0
        0x40, 0x09, 0x21, 0xFB, 0x54, 0x44, 0x2D, 0x18, // 3.1415926535897930
        0x40, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, // 153
        0xC0, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, // -153
        0x7F, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // infinity
        0xFF, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // -infinity
    };

    SECTION("validaed double precision float") {
        for( std::size_t i = 0; i < inputs.size() / sizeof( double ); ++i ) {
            const char* xs = (char*)inputs.data() + i * sizeof( double );
            double v, a;
            double x, y;
            dlis_fdoub1( xs, &v, &a );
            const char* ys = dlis_fdoubl( xs, &x );
                             dlis_fdoubl( ys, &y );
            CHECK( v == x );
            CHECK( a == y );
        }
    }

    SECTION("two-way validaed double precision float") {
        for( std::size_t i = 0; i < inputs.size() / sizeof( double ); ++i ) {
            const char* xs = (char*)inputs.data() + i * sizeof( double );
            double v, a, b;
            double x, y, z;
            dlis_fdoub2( xs, &v, &a, &b );
            const char* ys = dlis_fdoubl( xs, &x );
            const char* zs = dlis_fdoubl( ys, &y );
                             dlis_fdoubl( zs, &z );
            CHECK( v == x );
            CHECK( a == y );
            CHECK( b == z );
        }
    }

    SECTION("double precision complex float") {
        for( std::size_t j = 0; j < inputs.size() / sizeof( double ); ++j ) {
            const char* xs = (char*)inputs.data() + j * sizeof( double );
            double r, i;
            double x, y;
            dlis_fdoub1( xs, &r, &i );
            const char* ys = dlis_fdoubl( xs, &x );
                             dlis_fdoubl( ys, &y );
            CHECK( r == x );
            CHECK( i == y );
        }
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

TEST_CASE("ascii (var-length string)", "[type]") {
    std::int32_t len;

    SECTION("empty string has zero length") {
        dlis_ascii( "\0", &len, nullptr );
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

    SECTION("can be longer than 255 chars ") {
        std::vector< char > str( 510, ' ' );
        const std::string expected =
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc "
            "tristique enim ac leo tristique, eu finibus enim pharetra. "
            "Donec ac elit congue, viverra mauris nec, maximus mauris. "
            "Integer molestie non mi eget bibendum. Nam dolor nibh, tincidunt "
            "quis metus."
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc "
            "tristique enim ac leo tristique, eu finibus enim pharetra. "
            "Donec ac elit congue, viverra mauris nec, maximus mauris. "
            "Integer molestie non mi eget bibendum. Nam dolor nibh, tincidunt "
            "quis metus.";

        const std::string in = "\x81\xFE" + expected;

        dlis_ascii( in.c_str(), &len, nullptr );
        CHECK( len == 510 );
        dlis_ascii( in.c_str(), &len, str.data() );
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
