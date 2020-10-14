#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <initializer_list>
#include <iomanip>
#include <limits>
#include <sstream>
#include <string>

#include <catch2/catch.hpp>

#include <dlisio/types.h>

/*
 * Custom type for byte arrays, for nicely printing mismatch between expected
 * and actual parameters to comparison of byte arrays.
 *
 * This type exists mostly for Catch's stringmaker to have something to hook
 * into, as it relies on the type system to pick the correct specialisation.
 * Using std::array is pretty clumsy, and (unsigned) char* already means
 * "print-as-string".
 */
template< std::size_t N, typename T = char >
struct bytes {
    using value_type = T[N];

    bytes() = default;
    bytes( const value_type& xs ) {
        using std::begin;
        using std::end;
        std::copy( begin( xs ), end( xs ), begin( this->data ) );
    }

    bytes( std::initializer_list< std::size_t > xs ) {
        using std::begin;
        using std::end;
        std::copy( begin( xs ), end( xs ), begin( this->data ) );
    }

    operator value_type& ()             { return this->data; }
    operator const value_type& () const { return this->data; }

    value_type data;
};

namespace {

template< typename T, std::size_t N >
class BytesEqualsMatcher : public Catch::MatcherBase< bytes< N > > {
public:
    explicit BytesEqualsMatcher( T x ) : lhs( x ) {}

    virtual bool match( const bytes< N >& rhs ) const override {
        static_assert( sizeof( T ) == N, "sizeof(T) must be equal to N" );
        return std::memcmp( &this->lhs, rhs, sizeof( T ) ) == 0;
    }

    virtual std::string describe() const override {
        bytes< N > lhsb;
        std::memcpy( lhsb, &this->lhs, N );

        using str = Catch::StringMaker< bytes< N > >;
        return "== " + str::convert( lhsb );
    }

private:
    T lhs;
};

template< typename T >
BytesEqualsMatcher< T, sizeof( T ) > BytesEquals( T lhs ) {
    return BytesEqualsMatcher< T, sizeof( T ) >{ lhs };
}

}

namespace Catch {

/*
 * print bytes as a hex sequence
 */
template< std::size_t N >
struct StringMaker< bytes< N > > {
    static std::string convert( const bytes< N >& xs ) {
        std::stringstream ss;
        ss << std::hex;

        /*
         * Convert every byte to unsigned char (even though the byte array
         * stores as unspecified signed) to preserve representation as a byte,
         * so it doesn't change once widened to an int. Once an int, the
         * std::hex manipulator picks it up and writes it as a hex value
         */
        for( unsigned char x : xs.data ) {
            ss << std::setfill( '0' )
               << std::setw( 2 )
               << int( x ) << ' '
               ;
        }

        auto s = ss.str();
        /* remove trailing space */
        s.pop_back();
        return s;
    }
};

}

TEST_CASE("signed short (8-bit)", "[type]") {
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

    SECTION("to native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::int8_t v;
            dlis_sshort( inputs[ i ], &v );
            CHECK( int(v) == int(expected[ i ]) );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::int8_t v;
            dlis_sshorto( &v, expected[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( v ) );
        }
    }
}

TEST_CASE("signed normal (16-bit)", "[type]") {
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

    SECTION("to native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::int16_t v;
            dlis_snorm( inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::int16_t v;
            dlis_snormo( &v, expected[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( v ) );
        }
    }
}

TEST_CASE("signed long (32-bit)", "[type]") {
    const std::array< bytes< 4 >, 8 > inputs = {{
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

    SECTION("to native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::int32_t v;
            dlis_slong( inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::int32_t v;
            dlis_slongo( &v, expected[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( v ) );
        }
    }
}

TEST_CASE("unsigned short (8-bit)", "[type]") {
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

    SECTION("to native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::uint8_t v;
            dlis_ushort( inputs[ i ], &v );
            CHECK( int(v) == int(expected[ i ]) );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::uint8_t v;
            dlis_ushorto( &v, expected[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( v ) );
        }
    }
}

TEST_CASE("unsigned normal (16-bit)", "[type]") {
    const std::array< bytes< 2 >, 8 > inputs = {{
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

    SECTION("to native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::uint16_t v;
            dlis_unorm( inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::uint16_t v;
            dlis_unormo( &v, expected[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( v ) );
        }
    }
}

TEST_CASE("unsigned long (32-bit)", "[type]") {
    const std::array< bytes< 4 >, 8 > inputs = {{
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

    SECTION( "to native" ) {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::uint32_t v;
            dlis_ulong( inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            std::uint32_t v;
            dlis_ulongo( &v, expected[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( v ) );
        }
    }
}

TEST_CASE("variable-length unsigned int", "[type]") {
    SECTION("1-byte") {
        const std::array< bytes<1>, 4 > in = {{
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

        SECTION("to native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                std::int32_t v;
                const char* end = dlis_uvari( in[ i ], &v );
                CHECK( v == expected[ i ] );
                CHECK( std::intptr_t(end) == std::intptr_t(in[ i ] + 1) );
            }
        }

        SECTION("from native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                std::int8_t v;
                const void* end = dlis_uvario( &v, expected[ i ], 1 );
                CHECK_THAT( in[ i ], BytesEquals( v ) );
                CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
            }
        }
    }

    SECTION("2-byte") {
        const std::array< bytes<2>, 7 > in = {{
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

        SECTION("to native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                std::int32_t v;
                const char* end = dlis_uvari( in[ i ], &v );
                CHECK( v == expected[ i ] );
                CHECK( std::intptr_t(end) == std::intptr_t(in[ i ] + 2) );
            }
        }

        SECTION("from native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                std::int16_t v;
                const void* end = dlis_uvario( &v, expected[ i ], 2 );
                CHECK_THAT( in[ i ], BytesEquals( v ) );
                CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
            }
        }
    }

    SECTION("4-byte") {
        const std::array< bytes<4>, 9 > in = {{
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

        SECTION("to native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                std::int32_t v;
                const char* end = dlis_uvari( in[ i ], &v );
                CHECK( v == expected[ i ] );
                CHECK( std::intptr_t(end) == std::intptr_t(in[ i ] + 4) );
            }
        }

        SECTION("from native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                std::int32_t v;
                const void* end = dlis_uvario( &v, expected[ i ], 4 );
                CHECK_THAT( in[ i ], BytesEquals( v ) );
                CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
            }
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
        const std::array< bytes<4>, 7 > inputs = {{
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
            static_cast< float >( std::copysign(0, -1) ),
            3.1415927410125732421875,
            153,
            -153,
            std::numeric_limits< float >::infinity(),
            -std::numeric_limits< float >::infinity(),
        };

        SECTION("to native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                float v;
                dlis_fsingl( inputs[ i ], &v );
                CHECK( v == expected[ i ] );
            }
        }

        SECTION("from native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                float v;
                const void* end = dlis_fsinglo( &v, expected[ i ] );
                CHECK_THAT( inputs[ i ], BytesEquals( v ) );
                CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
            }
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
        const std::array< bytes<8>, 7 > inputs = {{
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
            static_cast< float >( std::copysign(0, -1) ),
            3.1415926535897930,
            153,
            -153,
            std::numeric_limits< double >::infinity(),
            -std::numeric_limits< double >::infinity(),
        };

        SECTION( "to native" ) {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                double v;
                dlis_fdoubl( inputs[ i ], &v );
                CHECK( v == expected[ i ] );
            }
        }

        SECTION( "from native" ) {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                double v;
                const void* end = dlis_fdoublo( &v, expected[ i ] );
                CHECK_THAT( inputs[ i ], BytesEquals( v ) );
                CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
            }
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
    const std::array< bytes< 4 >, 4 > inputs = {{
        { 0x00, 0x00, 0x00, 0x00 }, // 0
        { 0x42, 0x99, 0x00, 0x00 }, // 153
        { 0xC2, 0x99, 0x00, 0x00 }, // -153
        { 0xC2, 0x76, 0xA0, 0x00 }, // -118.625
    }};

    const std::array< float, inputs.size() > expected = {
        0.0,
        153.0,
        -153.0,
        -118.625,
    };

    SECTION( "to native" ) {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            float v;
            dlis_isingl( inputs[ i ], &v );
            CHECK( v == expected[ i ] );
        }
    }

    SECTION( "from native" ) {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            float v;
            const void* end = dlis_isinglo( &v, expected[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( v ) );
            CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
        }
    }
}

TEST_CASE("vax single precision float", "[type]") {
    const std::array< bytes< 4 >, 15 > inputs = {{
        { 0x00, 0x00, 0x00, 0x00 }, //  0
        { 0x19, 0x44, 0x00, 0x00 }, //  153
        { 0x19, 0xC4, 0x00, 0x00 }, // -153
        { 0x80, 0x40, 0x00, 0x00 }, //  1.000000
        { 0x80, 0xC0, 0x00, 0x00 }, // -1.000000
        { 0x60, 0x41, 0x00, 0x00 }, //  3.500000
        { 0x60, 0xC1, 0x00, 0x00 }, // -3.500000
        { 0x49, 0x41, 0xD0, 0x0F }, //  3.141590
        { 0x49, 0xC1, 0xD0, 0x0F }, // -3.141590
        { 0xF0, 0x7D, 0xC2, 0xBD }, //  9.9999999E+36
        { 0xF0, 0xFD, 0xC2, 0xBD }, // -9.9999999E+36
        { 0x08, 0x03, 0xEA, 0x1C }, //  9.9999999E-38
        { 0x08, 0x83, 0xEA, 0x1C }, // -9.9999999E-38
        { 0x9E, 0x40, 0x53, 0x06 }, //  1.234568
        { 0x9E, 0xC0, 0x53, 0x06 }, // -1.234568
    }};

    const std::array< float, inputs.size() > expected = {
        0.0,
        153,
        -153,
        1.000000,
        -1.000000,
        3.500000,
        -3.500000,
        3.141590,
        -3.141590,
        9.9999999E+36,
        -9.9999999E+36,
        9.9999999E-38,
        -9.9999999E-38,
        1.234568,
        -1.234568,
    };

    SECTION( "to native" ) {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            float v;
            dlis_vsingl( inputs[ i ], &v );
            CHECK( v == Approx(expected[ i ]).epsilon(0.0000001));
        }
    }

    SECTION( "to native - undefined" ) {
        bytes<4> vax_undef = { 0x00, 0x80, 0x01, 0x00 }; // s=1, e=0, m=!0

        float v;
        dlis_vsingl( vax_undef, &v );
        CHECK( std::isnan(v) );
    }

    SECTION( "to native - dirty zero" ) {
        bytes<4> vax_undef = { 0x00, 0x00, 0xF3, 0xFF }; // s=0, e=0, m=!0
        float expected = 0.0;

        float v;
        dlis_vsingl( vax_undef, &v );
        CHECK( v == expected);
    }

    SECTION( "from native" ) {
        for( std::size_t i = 0; i < expected.size(); ++i ) {
            float v;
            const void* end = dlis_vsinglo( &v, expected[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( v ) );
            CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
        }
    }
}

TEST_CASE("validated single precision float", "[type]") {
    const std::array< bytes< 8 >, 4 > inputs = {{
        // 0, -0
        { 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00 },
        // 3.1415927410125732421875, -0
        { 0x40, 0x49, 0x0F, 0xDB, 0x80, 0x00, 0x00, 0x00 },
        // 153, -153
        { 0x43, 0x19, 0x00, 0x00, 0xC3, 0x19, 0x00, 0x00 },
        // infinity, -infinity
        { 0x7F, 0x80, 0x00, 0x00, 0xFF, 0x80, 0x00, 0x00 },
    }};

    const std::array< float, inputs.size() > expectedV = {
        0,
        3.1415926535897930,
        153,
        std::numeric_limits< float >::infinity(),
    };

    const std::array< float, inputs.size() > expectedA = {
        static_cast< float >( std::copysign(0, -1) ),
        static_cast< float >( std::copysign(0, -1) ),
        -153,
        -std::numeric_limits< float >::infinity(),
    };

    SECTION("to native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            float v, a;
            dlis_fsing1( inputs[ i ], &v, &a );
            CHECK( v == expectedV[ i ] );
            CHECK( a == expectedA[ i ] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            double x;
            const void* end = dlis_fsing1o( &x, expectedV[ i ], expectedA[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( x ) );
            CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof(x) );
        }
    }
}

TEST_CASE("two-way validated single precision float", "[type]") {
    const std::array< bytes< 12 >, 4 > inputs = {{
        // 0, -0, 153
        { 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x43, 0x19, 0x00, 0x00 },
        // 3.1415927410125732421875, -0, 0
        { 0x40, 0x49, 0x0F, 0xDB, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
        // 153, -153, -0
        { 0x43, 0x19, 0x00, 0x00, 0xC3, 0x19, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00 },
        // infinity, -infinity, -153
        { 0x7F, 0x80, 0x00, 0x00, 0xFF, 0x80, 0x00, 0x00, 0xC3, 0x19, 0x00, 0x00 },
    }};

    const std::array< float, inputs.size() > expectedV = {
        0,
        3.1415926535897930,
        153,
        std::numeric_limits< float >::infinity(),
    };

    const std::array< float, inputs.size() > expectedA = {
        static_cast< float >( std::copysign(0, -1) ),
        static_cast< float >( std::copysign(0, -1) ),
        -153,
        -std::numeric_limits< float >::infinity(),
    };

    const std::array< float, inputs.size() > expectedB = {
        153,
        0,
        static_cast< float >( std::copysign(0, -1) ),
        -153
    };

    SECTION("to native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            float v, a, b;
            dlis_fsing2( inputs[ i ], &v, &a, &b );
            CHECK( v == expectedV[ i ] );
            CHECK( a == expectedA[ i ] );
            CHECK( b == expectedB[ i ] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            bytes< 12 > x;
            const void* end = dlis_fsing2o( &x,
                                            expectedV[ i ],
                                            expectedA[ i ],
                                            expectedB[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( x ) );
            CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof(x) );
        }
    }
}

TEST_CASE("single precision complex float", "[type]") {
    const std::array< bytes< 8 >, 4 > inputs = {{
        // 0, -0
        { 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00 },
        // 3.1415927410125732421875, -0
        { 0x40, 0x49, 0x0F, 0xDB, 0x80, 0x00, 0x00, 0x00 },
        // 153, -153
        { 0x43, 0x19, 0x00, 0x00, 0xC3, 0x19, 0x00, 0x00 },
        // infinity, -infinity
        { 0x7F, 0x80, 0x00, 0x00, 0xFF, 0x80, 0x00, 0x00 },
    }};

    const std::array< float, inputs.size() > expectedR = {
        0,
        3.1415926535897930,
        153,
        std::numeric_limits< float >::infinity(),
    };

    const std::array< float, inputs.size() > expectedI = {
        static_cast< float >( std::copysign(0, -1) ),
        static_cast< float >( std::copysign(0, -1) ),
        -153,
        -std::numeric_limits< float >::infinity(),
    };

    SECTION("to native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            float V, A;
            dlis_csingl( inputs[ i ], &V, &A );
            CHECK( V == expectedR[ i ] );
            CHECK( A == expectedI[ i ] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            double x;
            const void* end = dlis_csinglo( &x,
                                            expectedR[ i ],
                                            expectedI[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( x ) );
            CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof(x) );
        }
    }
}

TEST_CASE("validated double precision float", "[type]") {
    const std::array< bytes< 16 >, 4 > inputs = {{
        // 0,- 0
        { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
        // 3.1415926535897930, 153
        { 0x40, 0x09, 0x21, 0xFB, 0x54, 0x44, 0x2D, 0x18,
          0x40, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 },
        //-153, infinity
        { 0xC0, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x7F, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
        // -infinity, 0
        { 0xFF, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
    }};

    const std::array< double, inputs.size() > expectedV = {
        0,
        3.1415926535897930,
        -153,
        -std::numeric_limits< double >::infinity(),
    };

    const std::array< double, inputs.size() > expectedA = {
        static_cast< double >( std::copysign(0, -1) ),
        153,
        std::numeric_limits< double >::infinity(),
        0
    };

    SECTION("to native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            double v, a;
            dlis_fdoub1( inputs[ i ], &v, &a );
            CHECK( v == expectedV[ i ] );
            CHECK( a == expectedA[ i] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            bytes< 16 > x;
            const void* end = dlis_fdoub1o( &x,
                                            expectedV[ i ],
                                            expectedA[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( x ) );
            CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof(x) );
        }
    }
}

TEST_CASE("two-way validated double precision float", "[type]") {
    const std::array< bytes< 24 >, 4 > inputs = {{
        // 0,- 0, 153
        { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x40, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 },
        // 3.1415926535897930, 153, 0
        { 0x40, 0x09, 0x21, 0xFB, 0x54, 0x44, 0x2D, 0x18,
          0x40, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
        //-153, infinity, -0
        { 0xC0, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x7F, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
        // -infinity, 0, -153
        { 0xFF, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
          0xC0, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 },
    }};

    const std::array< double, inputs.size() > expectedV = {
        0,
        3.1415926535897930,
        -153,
        -std::numeric_limits< double >::infinity(),
    };

    const std::array< double, inputs.size() > expectedA = {
        static_cast< double >( std::copysign(0, -1) ),
        153,
        std::numeric_limits< double >::infinity(),
        0
    };

    const std::array< double, inputs.size() > expectedB = {
        153,
        0,
        static_cast< double >( std::copysign(0, -1) ),
        -153
    };

    SECTION("to native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            double v, a, b;
            dlis_fdoub2( inputs[ i ], &v, &a, &b );
            CHECK( v == expectedV[ i ] );
            CHECK( a == expectedA[ i ] );
            CHECK( b == expectedB[ i ] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            bytes< 24 > x;
            const void* end = dlis_fdoub2o( &x,
                                            expectedV[ i ],
                                            expectedA[ i ],
                                            expectedB[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( x ) );
            CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof(x) );
        }
    }
}

TEST_CASE("double precision complex float", "[type]") {
    const std::array< bytes< 16 >, 4 > inputs = {{
        // 0,- 0
        { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
        // 3.1415926535897930, 153
        { 0x40, 0x09, 0x21, 0xFB, 0x54, 0x44, 0x2D, 0x18,
          0x40, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 },
        //-153, infinity
        { 0xC0, 0x63, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x7F, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
        // -infinity, 0
        { 0xFF, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
          0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 },
    }};

    const std::array< double, inputs.size() > expectedR = {
        0,
        3.1415926535897930,
        -153,
        -std::numeric_limits< double >::infinity(),
    };

    const std::array< double, inputs.size() > expectedI = {
        static_cast< double >( std::copysign(0, -1) ),
        153,
        std::numeric_limits< double >::infinity(),
        0
    };

    SECTION("to native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            double re, im;
            dlis_cdoubl( inputs[ i ], &re, &im );
            CHECK( re == expectedR[ i ] );
            CHECK( im == expectedI[ i ] );
        }
    }

    SECTION("from native") {
        for( std::size_t i = 0; i < inputs.size(); ++i ) {
            bytes< 16 > x;
            const void* end = dlis_cdoublo( &x,
                                            expectedR[ i ],
                                            expectedI[ i ] );
            CHECK_THAT( inputs[ i ], BytesEquals( x ) );
            CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof(x) );
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

    SECTION("from native") {
        const std::string in = "foobar";
        const uint8_t length = 6;

        const std::array< bytes< 7 >, 1> expected = {{
            { 0x06, 0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72 }
        }};

        std::array< char, 7 > x;
        const void* end = dlis_idento( &x, length, in.c_str() );
        CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof( x ) );
        CHECK_THAT( expected[ 0 ], BytesEquals( x ) );
    }
}

TEST_CASE("units (var-length string)", "[type]") {
    std::int32_t len;

    SECTION("empty string has zero length") {
        dlis_units( "\0", &len, nullptr );
        CHECK( len == 0 );
    }

    SECTION("empty string does not affect output") {
        char str[] = "foobar";
        dlis_units( "\0", &len, str );
        CHECK( str == std::string("foobar") );
    }

    SECTION("single-char string has length 1") {
        char str[] = "    ";
        dlis_units( "\x01""a", &len, str );
        CHECK( str == std::string("a   ") );
        CHECK( len == 1 );
    }

    SECTION("single-char string has length 1") {
        char str[] = "    ";
        dlis_units( "\x01""a", &len, str );
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

        dlis_units( in.c_str(), &len, nullptr );
        CHECK( len == 255 );
        dlis_units( in.c_str(), &len, str.data() );
        CHECK( std::string( str.begin(), str.end() ) == expected );

    }

    SECTION("returns pointer past read data") {
        const char in[] = "\x32"
                          "Lorem ipsum dolor sit amet, consectetur adipiscing";

        const char* noread = dlis_units( in, &len, nullptr );
        CHECK( len == 50 );
        CHECK( std::intptr_t(noread) == std::intptr_t(in + sizeof( in ) - 1) );

        char out[ 50 ] = {};
        const char* withread = dlis_units( in, &len, out );
        CHECK( len == 50 );
        CHECK( std::intptr_t(withread) == std::intptr_t(noread) );
    }

    SECTION("from native") {
        const std::string in = "foobar";
        const uint8_t length = 6;

        const std::array< bytes< 7 >, 1> expected = {{
            { 0x06, 0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72 }
        }};

        std::array< char, 7 > x;
        const void* end = dlis_unitso( &x, length, in.c_str() );
        CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof( x ) );
        CHECK_THAT( expected[ 0 ], BytesEquals( x ) );
    }
}

TEST_CASE("origin", "[type]") {
    SECTION("4-byte") {
        const std::array< bytes<4>, 9 > in = {{
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

        SECTION("to native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                std::int32_t v;
                const char* end = dlis_origin( in[ i ], &v );
                CHECK( v == expected[ i ] );
                CHECK( std::intptr_t(end) == std::intptr_t(in[ i ] + 4) );
            }
        }

        SECTION("from native") {
            for( std::size_t i = 0; i < expected.size(); ++i ) {
                std::int32_t v;
                const void* end = dlis_origino( &v, expected[ i ] );
                CHECK_THAT( in[ i ], BytesEquals( v ) );
                CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
            }
        }
    }
}

TEST_CASE("ascii (var-length string)", "[type]") {
    std::int32_t len;

    SECTION("to native") {

        SECTION("empty string has zero length") {
            dlis_ascii( "\0", &len, nullptr );
            CHECK( len == 0 );
        }

        SECTION("empty string does not affect output") {
            char str[] = "foobar";
            dlis_ascii( "\0", &len, str );
            CHECK( str == std::string("foobar") );
        }

        SECTION("single-char string has length 1") {
            char str[] = "    ";
            dlis_ascii( "\x01""a", &len, str );
            CHECK( str == std::string("a   ") );
            CHECK( len == 1 );
        }

        SECTION("single-char string has length 1") {
            char str[] = "    ";
            dlis_ascii( "\x01""a", &len, str );
            CHECK( str == std::string("a   ") );
            CHECK( len == 1 );
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

            const char* noread = dlis_ascii( in, &len, nullptr );
            CHECK( len == 50 );
            CHECK( std::intptr_t(noread) == std::intptr_t(in + sizeof( in ) - 1) );

            char out[ 50 ] = {};
            const char* withread = dlis_ascii( in, &len, out );
            CHECK( len == 50 );
            CHECK( std::intptr_t(withread) == std::intptr_t(noread) );
        }
    }

    SECTION("from native") {

        SECTION("can write the correct string") {
            const std::string in = "foobar";
            const int32_t length = 6;

            const std::array< bytes< 7 >, 1> expected = {{
                { 0x06, 0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72 }
            }};

            std::array< char, 7 > x;
            const void* end = dlis_asciio( &x, length, in.c_str(), 1 );
            CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof( x ) );
            CHECK_THAT( expected[ 0 ], BytesEquals( x ) );
        }

        SECTION("can write 2-byte len-prefix") {
            const std::string in = "foobar";
            const int32_t length = 6;

            const std::array< bytes< 8 >, 1> expected = {{
                { 0x80, 0x06, 0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72 }
            }};

            std::array< char, 8 > x;
            const void* end = dlis_asciio( &x, length, in.c_str(), 2 );
            CHECK( std::intptr_t(end) == std::intptr_t(&x) + sizeof( x ) );
            CHECK_THAT( expected[ 0 ], BytesEquals( x ) );

        }
    }
}

TEST_CASE("date-time", "[type]") {
    bytes< 8 > input = {
        0x57, // 87
        0x14, // 1, 4
        0x13, // 19
        0x15, // 21
        0x14, // 20
        0x0F, // 15
        0x02, 0x6C // 620
    };

    // 9:20:15.62 PM, April 19, 1987 (DST)
    int Y, TZ, M, D, H, MN, S, MS;

    SECTION("to native") {
        dlis_dtime( input, &Y, &TZ, &M, &D, &H, &MN, &S, &MS );

        CHECK( Y  == 87 );
        CHECK( dlis_year( Y ) == 1987 );
        CHECK( TZ == DLIS_TZ_DST );
        CHECK( M  == 4 );
        CHECK( D  == 19 );
        CHECK( H  == 21 );
        CHECK( MN == 20 );
        CHECK( S  == 15 );
        CHECK( MS == 620 );
    }

    SECTION("from native") {
        bytes< 8 > x;
        const void* end = dlis_dtimeo( &x,
                                       dlis_yearo( 1987 ),
                                       DLIS_TZ_DST,
                                       4,
                                       19,
                                       21,
                                       20,
                                       15,
                                       620 );
        CHECK( intptr_t(end) == intptr_t(&x) + sizeof( x ) );
        CHECK_THAT( input, BytesEquals( x ) );
    }
}

TEST_CASE( "obname", "[type]" ) {
    const std::array< bytes< 12 >, 1 > in = {{
        { 0xC0, 0x00, 0x00, 0x7F,               // 127
          0x59,                                 // 89
          0x06,                                 // 6
          0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72 }  // foobar
    }};

    const std::int32_t originOut = 127;
    const std::uint8_t copynumberOut = 89;
    const std::int32_t idlenOut = 6;
    std::string identOut = "foobar";


    std::int32_t origin, idlen;
    std::uint8_t copynumber;
    std::vector< char > ident( 6, ' ' );

    SECTION("to native") {
        const char* end = dlis_obname( in[ 0 ], &origin,
                                                &copynumber,
                                                &idlen,
                                                ident.data() );
        CHECK( origin     == originOut );
        CHECK( copynumber == copynumberOut );
        CHECK( idlen      == idlenOut );
        CHECK( std::string( ident.begin(), ident.end() ) == identOut );
        CHECK( std::intptr_t(end) == std::intptr_t( in[ 0 ] + 12 ) );
    }

    SECTION("from native") {
        bytes< 12 > v;
        const std::uint8_t idlen = 6;
        const void* end = dlis_obnameo( &v, originOut,
                                            copynumberOut,
                                            idlen,
                                            identOut.c_str() );

        CHECK_THAT( in[ 0 ], BytesEquals( v ) );
        CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
    }
}

TEST_CASE( "objref", "[type]" ) {
    const std::array< bytes< 19 >, 1 > in = {{
        { 0x06,                                 // 6
          0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72,   // foobar
          0xC0, 0x00, 0x00, 0x7F,               // 127
          0x59,                                 // 89
          0x06,                                 // 6
          0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72 }  // foobar
    }};

    const std::int32_t originOut = 127;
    const std::uint8_t copynumberOut = 89;
    const std::int32_t idlenOut = 6;
    std::string identOut = "foobar";


    std::int32_t idlen1, origin, idlen2;
    std::uint8_t copynumber;
    std::vector< char > ident1( 6, ' ' );
    std::vector< char > ident2( 6, ' ' );

    SECTION("to native") {
        const char* end = dlis_objref( in[ 0 ], &idlen1,
                                                ident1.data(),
                                                &origin,
                                                &copynumber,
                                                &idlen2,
                                                ident2.data() );

        CHECK( idlen1     == idlenOut );
        CHECK( idlen2     == idlenOut );
        CHECK( origin     == originOut );
        CHECK( copynumber == copynumberOut );
        CHECK( std::string( ident1.begin(), ident1.end() ) == identOut );
        CHECK( std::string( ident2.begin(), ident2.end() ) == identOut );
        CHECK( std::intptr_t(end) == std::intptr_t( in[ 0 ] + 19 ) );
    }

    SECTION("from native") {
        bytes< 19 > v;
        const std::uint8_t idlen = 6;
        const void* end = dlis_objrefo( &v, idlen,
                                            identOut.c_str(),
                                            originOut,
                                            copynumberOut,
                                            idlen,
                                            identOut.c_str() );

        CHECK_THAT( in[ 0 ], BytesEquals( v ) );
        CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
    }
}

TEST_CASE( "attref", "[type]" ) {
    const std::array< bytes< 26 >, 1 > in = {{
        { 0x06,                                 // 6
          0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72,   // foobar
          0xC0, 0x00, 0x00, 0x7F,               // 127
          0x59,                                 // 89
          0x06,                                 // 6
          0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72,   // foobar
          0x06,                                 // 6
          0x66, 0x6F, 0x6F, 0x62, 0x61, 0x72 }  // foobar
    }};

    const std::int32_t originOut = 127;
    const std::uint8_t copynumberOut = 89;
    const std::int32_t idlenOut = 6;
    std::string identOut = "foobar";


    std::int32_t idlen1, origin, idlen2, idlen3;
    std::uint8_t copynumber;
    std::vector< char > ident1( 6, ' ' );
    std::vector< char > ident2( 6, ' ' );
    std::vector< char > ident3( 6, ' ' );

    SECTION("to native") {
        const char* end = dlis_attref( in[ 0 ], &idlen1,
                                                ident1.data(),
                                                &origin,
                                                &copynumber,
                                                &idlen2,
                                                ident2.data(),
                                                &idlen3,
                                                ident3.data() );

        CHECK( idlen1     == idlenOut );
        CHECK( idlen2     == idlenOut );
        CHECK( idlen3     == idlenOut );
        CHECK( origin     == originOut );
        CHECK( copynumber == copynumberOut );
        CHECK( std::string( ident1.begin(), ident1.end() ) == identOut );
        CHECK( std::string( ident2.begin(), ident2.end() ) == identOut );
        CHECK( std::string( ident3.begin(), ident3.end() ) == identOut );
        CHECK( std::intptr_t(end) == std::intptr_t( in[ 0 ] + 26 ) );
    }

    SECTION("from native") {
        bytes< 26 > v;
        const std::uint8_t idlen = 6;
        const void* end = dlis_attrefo( &v, idlen,
                                            identOut.c_str(),
                                            originOut,
                                            copynumberOut,
                                            idlen,
                                            identOut.c_str(),
                                            idlen,
                                            identOut.c_str() );

        CHECK_THAT( in[ 0 ], BytesEquals( v ) );
        CHECK( std::intptr_t(end) == std::intptr_t(&v) + sizeof(v) );
    }
}

TEST_CASE( "size-of", "[type]" ) {
    CHECK( dlis_sizeof_type( DLIS_FSHORT ) == 2 );
    CHECK( dlis_sizeof_type( DLIS_FSINGL ) == 4 );
    CHECK( dlis_sizeof_type( DLIS_FSING1 ) == 8 );
    CHECK( dlis_sizeof_type( DLIS_FSING2 ) == 12 );
    CHECK( dlis_sizeof_type( DLIS_ISINGL ) == 4 );
    CHECK( dlis_sizeof_type( DLIS_VSINGL ) == 4 );
    CHECK( dlis_sizeof_type( DLIS_FDOUBL ) == 8 );
    CHECK( dlis_sizeof_type( DLIS_FDOUB1 ) == 16 );
    CHECK( dlis_sizeof_type( DLIS_FDOUB2 ) == 24 );
    CHECK( dlis_sizeof_type( DLIS_CSINGL ) == 8 );
    CHECK( dlis_sizeof_type( DLIS_CDOUBL ) == 16 );
    CHECK( dlis_sizeof_type( DLIS_SSHORT ) == 1 );
    CHECK( dlis_sizeof_type( DLIS_SNORM  ) == 2 );
    CHECK( dlis_sizeof_type( DLIS_SLONG  ) == 4 );
    CHECK( dlis_sizeof_type( DLIS_USHORT ) == 1 );
    CHECK( dlis_sizeof_type( DLIS_UNORM  ) == 2 );
    CHECK( dlis_sizeof_type( DLIS_ULONG  ) == 4 );
    CHECK( dlis_sizeof_type( DLIS_UVARI  ) == 0 );
    CHECK( dlis_sizeof_type( DLIS_IDENT  ) == 0 );
    CHECK( dlis_sizeof_type( DLIS_ASCII  ) == 0 );
    CHECK( dlis_sizeof_type( DLIS_DTIME  ) == 8 );
    CHECK( dlis_sizeof_type( DLIS_ORIGIN ) == 0 );
    CHECK( dlis_sizeof_type( DLIS_OBNAME ) == 0 );
    CHECK( dlis_sizeof_type( DLIS_OBJREF ) == 0 );
    CHECK( dlis_sizeof_type( DLIS_ATTREF ) == 0 );
    CHECK( dlis_sizeof_type( DLIS_STATUS ) == 1 );
    CHECK( dlis_sizeof_type( DLIS_UNITS  ) == 0 );
}
