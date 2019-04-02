#include <array>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>

#include <catch2/catch.hpp>

#include <dlisio/dlisio.h>


namespace {

struct check_packsize {
    ~check_packsize() {
        std::int32_t size;
        auto err = dlis_pack_size( fmt, nullptr, &size );
        CHECK( err == DLIS_OK );
        CHECK( size == buffer.size() );

        int variable;
        err = dlis_pack_varsize( fmt, nullptr, &variable );
        CHECK( err == DLIS_OK );
        CHECK( !variable );
    }

    const char* fmt;
    std::vector< char > buffer;
};

}

TEST_CASE_METHOD(check_packsize, "pack UVARIs and ORIGINs", "[pack]") {
    const unsigned char source[] = {
        0xC0, 0x00, 0x00, 0x00, // 0
        0xC0, 0x00, 0x00, 0x01, // 1
        0xC0, 0x00, 0x00, 0x2E, // 46
        0xC0, 0x00, 0x00, 0x7F, // 127
        0xC0, 0x00, 0x01, 0x00, // 256
        0xC0, 0x00, 0x8F, 0xFF, // 36863
        0xC1, 0x00, 0x00, 0x00, // 16777216
        0xF0, 0x00, 0xBF, 0xFF, // 805355519
    };

    fmt = "iJiJiJiJ";
    std::int32_t dst[ 8 ];
    buffer.resize(sizeof(dst));

    const auto err = dlis_packf( fmt, source, dst );

    CHECK( err == DLIS_OK );
    CHECK( dst[ 0 ] == 0 );
    CHECK( dst[ 1 ] == 1 );
    CHECK( dst[ 2 ] == 46 );
    CHECK( dst[ 3 ] == 127 );
    CHECK( dst[ 4 ] == 256 );
    CHECK( dst[ 5 ] == 36863 );
    CHECK( dst[ 6 ] == 16777216 );
    CHECK( dst[ 7 ] == 805355519 );
}

TEST_CASE_METHOD(check_packsize, "pack unsigned integers", "[pack]") {
    const unsigned char source[] = {
        0x59, // 89 ushort
        0xA7, // 167 ushort
        0x00, 0x99, // 153 unorm
        0x80, 0x00, // 32768 unorm
        0x00, 0x00, 0x00, 0x99, // 153 ulong
        0xFF, 0xFF, 0xFF, 0x67, // 4294967143 ulong
        0x01, // 1 uvari
        0x81, 0x00, // 256 uvari
        0xC0, 0x00, 0x8F, 0xFF, // 36863 uvari
        0xF0, 0x00, 0xBF, 0xFF, // 805355519 uvari
        0xC0, 0x00, 0x40, 0x00, // 16384 uvari (first with 4 bytes)
        0xBF, 0xFF, //16383 uvari (last with 2 bytes)
        0x80, 0x80, //128 uvari (first with 2 bytes)
        0x7F, //127 uvari (last with 1 byte)
        0x80, 0x01, //1 uvari (on 2 bytes)
    };

    fmt = "uuUULLiiiiiiiii";
    buffer.resize((1 * 2) + (2 * 2) + (4 * 2) + (4 * 9));
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    std::uint8_t us[2];
    std::memcpy( us, dst, sizeof(us) );
    CHECK( us[ 0 ] == 89 );
    CHECK( us[ 1 ] == 167 );

    std::uint16_t un[2];
    std::memcpy( un, dst + 2, sizeof(un) );
    CHECK( un[ 0 ] == 153 );
    CHECK( un[ 1 ] == 32768 );

    std::uint32_t ul[2];
    std::memcpy( ul, dst + 6, sizeof(ul) );
    CHECK( ul[ 0 ] == 153 );
    CHECK( ul[ 1 ] == 4294967143 );

    std::int32_t uv[9];
    std::memcpy( uv, dst + 14, sizeof(uv) );
    CHECK( uv[ 0 ] == 1 );
    CHECK( uv[ 1 ] == 256 );
    CHECK( uv[ 2 ] == 36863 );
    CHECK( uv[ 3 ] == 805355519 );
    CHECK( uv[ 4 ] == 16384 );
    CHECK( uv[ 5 ] == 16383 );
    CHECK( uv[ 6 ] == 128 );
    CHECK( uv[ 7 ] == 127 );
    CHECK( uv[ 8 ] == 1 );
}

TEST_CASE_METHOD(check_packsize, "pack signed integers", "[pack]") {
    const unsigned char source[] = {
        0x59, // 89 sshort
        0xA7, // -89 sshort
        0x00, 0x99, // 153 snorm
        0xFF, 0x67, // -153 snorm
        0x00, 0x00, 0x00, 0x99, // 153 slong
        0xFF, 0xFF, 0xFF, 0x67, // -153 slong
        0x7F, 0xFF, 0xFF, 0xFF, // ~2.1b slong (int-max)
    };

    fmt = "ddDDlll";
    buffer.resize((1 * 2) + (2 * 2) + (4 * 3));
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    std::int8_t ss[2];
    std::memcpy( ss, dst, sizeof( ss ) );
    CHECK( ss[ 0 ] == 89 );
    CHECK( ss[ 1 ] == -89 );

    std::int16_t sn[2];
    std::memcpy( sn, dst + 2, sizeof( sn ) );
    CHECK( sn[ 0 ] == 153 );
    CHECK( sn[ 1 ] == -153 );

    std::int32_t sl[3];
    std::memcpy( sl, dst + 6, sizeof( sl ) );
    CHECK( sl[ 0 ] == 153 );
    CHECK( sl[ 1 ] == -153 );
    CHECK( sl[ 2 ] == 2147483647 );
}

TEST_CASE_METHOD(check_packsize, "pack floats", "[pack]") {
    const unsigned char source[] = {
        0x4C, 0x88, // 153 fshort
        0x80, 0x00, //-1 fshort
        0x3F, 0x80, 0x00, 0x00, //1 fsingl
        0xC3, 0x19, 0x00, 0x00, //-153 fsingl
        0xC1, 0xC0, 0x00, 0x00, //-12 isingl
        0x45, 0x10, 0x00, 0x08, //65536.5 isingl
        0xAA, 0xC2, 0x00, 0x00, //-26.5 vsingl
        0x00, 0x3F, 0x00, 0x00, //0.125 vsingl
    };

    fmt = "rrffxxVV";
    buffer.resize(8 * sizeof(float));
    float* dst = reinterpret_cast< float* >( buffer.data() );

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    CHECK( dst[ 0 ] == 153.0 );
    CHECK( dst[ 1 ] == -1.0 );
    CHECK( dst[ 2 ] == 1.0 );
    CHECK( dst[ 3 ] == -153.0 );
    CHECK( dst[ 4 ] == -12 );
    CHECK( dst[ 5 ] == 65536.5 );
    CHECK( dst[ 6 ] == -26.5 );
    CHECK( dst[ 7 ] == 0.125 );
}

TEST_CASE_METHOD(check_packsize, "pack statistical", "[pack]") {
    const unsigned char source[] = {
        0x41, 0xE4, 0x00, 0x00, //28.5 fsing1 V
        0x3F, 0x00, 0x00, 0x00, //0.5 fsing1 A
        0xC3, 0x00, 0x00, 0x00, //-128 fsing2 V
        0x40, 0x70, 0x00, 0x00, //3.75 fsing2 A
        0x3E, 0x00, 0x00, 0x00, //0.125 fsing2 B
        0xC0, 0x8F, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, //-1000 fdoubl1 V
        0x3F, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, //1 fdoub11 A
        0xC0, 0xBA, 0x83, 0x00, 0x00, 0x00, 0x00, 0x00, //-6787 fdoubl2 V
        0x3F, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, //0.015625 fdoubl2 A
        0x3F, 0xA4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, //0.0390625 fdoubl2 B
    };


    fmt = "bBzZ";
    buffer.resize(4 * 2 + 4 * 3 + 8 * 2 + 8 * 3);
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    float fs1[2];
    std::memcpy( fs1, dst, sizeof( fs1 ) );
    CHECK( fs1[ 0 ] == 28.5 );
    CHECK( fs1[ 1 ] == 0.5 );

    float fs2[3];
    std::memcpy( fs2, dst + 8, sizeof( fs2 ) );
    CHECK( fs2[ 0 ] == -128 );
    CHECK( fs2[ 1 ] == 3.75 );
    CHECK( fs2[ 2 ] == 0.125 );

    double fd1[2];
    std::memcpy( fd1, dst + 20, sizeof( fd1 ) );
    CHECK( fd1[ 0 ] == -1000 );
    CHECK( fd1[ 1 ] == 1 );

    double fd2[3];
    std::memcpy( fd2, dst + 36, sizeof( fd2 ) );
    CHECK( fd2[ 0 ] == -6787 );
    CHECK( fd2[ 1 ] == 0.015625 );
    CHECK( fd2[ 2 ] == 0.0390625 );
}

TEST_CASE_METHOD(check_packsize, "pack doubles", "[pack]") {
    const unsigned char source[] = {
        0x3F, 0xD0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,// 0.25 fdouble
        0xC2, 0xF3, 0x78, 0x5F, 0x66, 0x30, 0x1C, 0x0A,// -342523480572352.625 fdouble
    };

    buffer.resize( 2 * sizeof(double) );
    fmt = "FF";
    auto* dst = reinterpret_cast< double* >( buffer.data() );

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    CHECK( dst[ 0 ] == 0.25 );
    CHECK( dst[ 1 ] == -342523480572352.625 );
}

TEST_CASE_METHOD(check_packsize, "pack complex", "[pack]") {
    const unsigned char source[] = {
        0x41, 0x2C, 0x00, 0x00, //10.75 csingl R
        0xC1, 0x10, 0x00, 0x00, //-9 csing1 I
        0x40, 0x3C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, //28 cdoubl R
        0x40, 0x42, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, //36.5 cdoub1 I
    };

    fmt = "cC";
    buffer.resize( 4 * 2 + 8 * 2 );
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    float cs[2];
    std::memcpy( cs, dst, sizeof( cs ) );
    CHECK( cs[ 0 ] == 10.75 );
    CHECK( cs[ 1 ] == -9 );

    double cd[2];
    std::memcpy( cd, dst + 8, sizeof( cd ) );
    CHECK( cd[ 0 ] == 28 );
    CHECK( cd[ 1 ] == 36.5 );
}


TEST_CASE_METHOD(check_packsize, "pack datetime", "[pack]") {
    const unsigned char source[] = {
        // 255Y 2TZ 12M 31D 0H 32MN 16S 0MS
        0xFF, 0x2C, 0x1F, 0x00, 0x20, 0x10, 0x00, 0x00,

        // 0Y 0TZ 1M 1D 23H 59M 0S 999MS
        0x00, 0x01, 0x01, 0x17, 0x3B, 0x00, 0x03, 0xE7,
    };

    fmt = "jj";
    buffer.resize( 2 * 8 * sizeof(int) );
    auto* dst = reinterpret_cast< int* >( buffer.data() );

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    CHECK( dst[0] == 255 );
    CHECK( dst[1] == 2 );
    CHECK( dst[2] == 12 );
    CHECK( dst[3] == 31 );
    CHECK( dst[4] == 0 );
    CHECK( dst[5] == 32 );
    CHECK( dst[6] == 16 );
    CHECK( dst[7] == 0 );

    CHECK( dst[ 8] == 0 );
    CHECK( dst[ 9] == 0 );
    CHECK( dst[10] == 1 );
    CHECK( dst[11] == 1 );
    CHECK( dst[12] == 23 );
    CHECK( dst[13] == 59 );
    CHECK( dst[14] == 0 );
    CHECK( dst[15] == 999 );
}

TEST_CASE_METHOD(check_packsize, "pack status", "[pack]") {
    const unsigned char source[] = {
        0x00, // 0 status
        0x01, // 1 status
    };

    buffer.resize( 2 );
    fmt = "qq";
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    CHECK( !dst[ 0 ] );
    CHECK(  dst[ 1 ] );
}

namespace {

struct check_is_varsize {
    ~check_is_varsize () {
        int variable;
        auto err = dlis_pack_varsize( fmt, nullptr, &variable );
        CHECK( err == DLIS_OK );
        CHECK( variable );

        err = dlis_pack_size( fmt, nullptr, &variable );
        CHECK( err == DLIS_INCONSISTENT );
    }

    const char* fmt;
};

std::string readstr( const char* src ) {
    std::int32_t len;
    std::memcpy( &len, src, sizeof(len) );
    return std::string( src + 4, len );
}

}

TEST_CASE_METHOD(check_is_varsize, "pack ident & ascii & unit", "[pack]") {
    const unsigned char source[] = {
        0x04, 0x54, 0x45, 0x53, 0x54,       //"TEST" ident
        0x05, 0x54, 0x59, 0x50, 0x45, 0x31, //"TYPE1" ident
        0x05, 0x54, 0x45, 0x53, 0x54, 0x54, //"TESTT" ident
        0x03, 0x41, 0x42, 0x43,             //"ABC" ident
        0x00, //empty ident

        0x0E, 0x54, 0x45, 0x53, 0x54, 0x54, 0x45,
              0x53, 0x54, 0x54, 0x45, 0x53, 0x54,
              0x54, 0x45, // "TESTTESTTESTTE" ident

        0x03, 0x41, 0x0A, 0x62, //A <linefeed> b ascii

        0x80, 0x04, 0x5C, 0x00, 0x7E, 0x00, // \\0~\0 ascii

        0x0D, 0x55, 0x20, 0x2D, 0x20, 0x75,
              0x6E, 0x69, 0x74, 0x20, 0x28, 0x2F, 0x33, 0x29, // U - unit (/3)
    };

    std::array< std::string, 9 > expected;
    expected[0] = "TEST";
    expected[1] = "TYPE1";
    expected[2] = "TESTT";
    expected[3] = "ABC";
    expected[4] = "";
    expected[5] = "TESTTESTTESTTE";
    expected[6] = "A\nb";
    expected[7] = std::string("\\\0~\0", 4);
    expected[8] = "U - unit (/3)";

    std::vector< char > buffer(
          expected.size() * sizeof(std::int32_t)
        + expected[0].size()
        + expected[1].size()
        + expected[2].size()
        + expected[3].size()
        + expected[4].size()
        + expected[5].size()
        + expected[6].size()
        + expected[7].size()
        + expected[8].size()
    );

    fmt = "ssssssSSQ";
    REQUIRE( std::string(fmt).size() == expected.size() );
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    std::array< std::string, 9 > result;
    REQUIRE( result.size() == expected.size() );

    result[0] = readstr( dst + 0  );
    result[1] = readstr( dst + 8  );
    result[2] = readstr( dst + 17 );
    result[3] = readstr( dst + 26 );
    result[4] = readstr( dst + 33 );
    result[5] = readstr( dst + 37 );
    result[6] = readstr( dst + 55 );
    result[7] = readstr( dst + 62 );
    result[8] = readstr( dst + 70 );

    for (auto i = 0U; i < result.size(); ++i)
        CHECK( result[i] == expected[i] );
}

TEST_CASE_METHOD(check_is_varsize, "pack long ascii ", "[pack]") {
    const unsigned char len[4] = { 0xC0, 0x00, 0x01, 0x2D }; //301
    const std::string expected =
        "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. "
        "Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque "
        "penatibus et magnis dis parturient montes, nascetur ridiculus mus. "
        "Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. "
        "Nulla consequat massa quis enim. Doneca."
    ;

    REQUIRE( expected.size() == 301 );

    std::vector< char > src( sizeof(std::int32_t) + expected.size() );
    std::memcpy( src.data() + 0, len, sizeof(std::int32_t) );
    std::memcpy( src.data() + 4, expected.data(), expected.size() );
    fmt = "S";

    std::vector< char > dst( src.size() );
    const auto err = dlis_packf( fmt, src.data(), dst.data() );
    CHECK( err == DLIS_OK );

    std::int32_t length;
    std::memcpy( &length, dst.data(), sizeof(length) );

    std::string outcome( dst.begin() + 4, dst.end() );
    CHECK( length == expected.size() );
    CHECK( outcome == expected );
}

TEST_CASE_METHOD(check_is_varsize, "pack obname", "[pack]") {
    const unsigned char source[] = {
        // (314, 255, "DLISIODLISIO")
        0x81, 0x3A,
        0xFF,
        0x0C, 0x44, 0x4C, 0x49, 0x53, 0x49, 0x4F,
        0x44, 0x4C, 0x49, 0x53, 0x49, 0x4F,

        // (4, 15, "DL")
        0x04, 0x0F,
        0x02,
        0x44, 0x4C,
    };

    std::vector< char > buffer( (4 + 1 + 16) + (4 + 1 + 6) );
    fmt = "oo";
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    std::int32_t origin;
    std::uint8_t copy;
    std::string id;

    std::memcpy( &origin, dst + 0, sizeof(origin) );
    std::memcpy( &copy,   dst + 4, sizeof(copy) );
    id = readstr( dst + 5 );
    CHECK( origin == 314 );
    CHECK( copy == 255 );
    CHECK( id == "DLISIODLISIO" );

    dst += sizeof(origin) + sizeof(copy) + sizeof(int32_t) + id.size();

    std::memcpy( &origin, dst + 0, sizeof(origin) );
    std::memcpy( &copy,   dst + 4, sizeof(copy) );
    id = readstr( dst + 5 );
    CHECK( origin == 4 );
    CHECK( copy == 15 );
    CHECK( id == "DL" );
}

TEST_CASE_METHOD(check_is_varsize, "pack objref", "[pack]") {
    const unsigned char source[] = {
        // ("LIBRARY", (1, 0, "PROTOCOL"))
        0x07, 0x4C, 0x49, 0x42, 0x52, 0x41, 0x52, 0x59, // "LIBRARY"
        0x01, 0x00, // 1, 0
        0x08, 0x50, 0x52, 0x4F, 0x54, 0x4F, 0x43, 0x4F, 0x4C, // "PROTOCOL"
    };

    std::vector< char > buffer(4 + 7 + 4 + 1 + 4 + 8);
    auto* dst = buffer.data();

    fmt = "O";
    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    std::string type;
    std::int32_t origin;
    std::uint8_t copy;
    std::string id;

    type = readstr( dst + 0 );
    std::memcpy( &origin, dst + 11, sizeof(origin) );
    std::memcpy( &copy,   dst + 15, sizeof(copy) );
    id = readstr( dst + 16 );

    CHECK( type == "LIBRARY" );
    CHECK( 1 == origin );
    CHECK( 0 == copy );
    CHECK( id == "PROTOCOL" );
}

TEST_CASE_METHOD(check_is_varsize, "pack attref", "[pack]") {
    const unsigned char source[] = {
        // ("LOREMIPSUM", (10, 69, "DOLORISTAMET"), "CONSECTETUERA")
        // "LOREMIPSUM"
        0x0A, 0x4C, 0x4F, 0x52, 0x45, 0x4D, 0x49, 0x50, 0x53, 0x55, 0x4D,
        // 10, 69
        0xC0, 0x00, 0x00, 0x0A, 0x45,

        // "DOLORSITAMET"
        0x0C,
        0x44, 0x4F, 0x4C, 0x4F, 0x52, 0x53, 0x49, 0x54, 0x41, 0x4D, 0x45, 0x54,

        // "CONSECTETUERA"
        0x0D, 0x43, 0x4F, 0x4E, 0x53, 0x45, 0x43, 0x54, 0x45, 0x54, 0x55, 0x45,
        0x52, 0x41,
    };

    fmt = "A";
    std::vector< char > buffer( (4 + 10) + (4 + 1) + (4 + 12) + (4 + 13) );
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    std::string type;
    std::int32_t origin;
    std::uint8_t copy;
    std::string id;
    std::string label;

    type = readstr( dst + 0 );
    std::memcpy( &origin, dst + 14, sizeof(origin) );
    std::memcpy( &copy,   dst + 18, sizeof(copy) );
    id = readstr( dst + 19 );
    label = readstr( dst + 35 );

    CHECK( type == "LOREMIPSUM" ) ;
    CHECK( origin == 10 );
    CHECK( copy == 69 );
    CHECK( id == "DOLORSITAMET" );
    CHECK( label == "CONSECTETUERA" );
}

TEST_CASE_METHOD(check_is_varsize, "pack unexpected value", "[pack]") {
    const unsigned char source[] = {
        0x59, // 89 sshort
        0x01, 0x53, // "S" ident
    };

    unsigned char dst[6];
    fmt = "ust";

    const auto err = dlis_packf( fmt, source, dst );

    CHECK( err == DLIS_UNEXPECTED_VALUE);
    CHECK( dst[0] == 89);
    CHECK( dst[5] == 'S');
}

TEST_CASE("pack var-size fails with invalid specifier") {
    CHECK( dlis_pack_varsize( "w",  nullptr, nullptr ) == DLIS_INVALID_ARGS );
    CHECK( dlis_pack_varsize( "lw", nullptr, nullptr ) == DLIS_INVALID_ARGS );
    CHECK( dlis_pack_varsize( "wl", nullptr, nullptr ) == DLIS_INVALID_ARGS );
}

namespace {

bool pack_varsize( const char* fmt ) {
    int vsize;
    CHECK( dlis_pack_varsize( fmt, nullptr, &vsize ) == DLIS_OK );
    return vsize;
};

}

TEST_CASE("pack var-size with all-constant specifiers") {
    CHECK( !pack_varsize( "r" ) );
    CHECK( !pack_varsize( "f" ) );
    CHECK( !pack_varsize( "b" ) );
    CHECK( !pack_varsize( "B" ) );
    CHECK( !pack_varsize( "x" ) );
    CHECK( !pack_varsize( "V" ) );
    CHECK( !pack_varsize( "F" ) );
    CHECK( !pack_varsize( "z" ) );
    CHECK( !pack_varsize( "Z" ) );
    CHECK( !pack_varsize( "c" ) );
    CHECK( !pack_varsize( "C" ) );
    CHECK( !pack_varsize( "d" ) );
    CHECK( !pack_varsize( "D" ) );
    CHECK( !pack_varsize( "l" ) );
    CHECK( !pack_varsize( "u" ) );
    CHECK( !pack_varsize( "U" ) );
    CHECK( !pack_varsize( "L" ) );
    CHECK( !pack_varsize( "j" ) );
    CHECK( !pack_varsize( "J" ) );
    CHECK( !pack_varsize( "q" ) );
    CHECK( !pack_varsize( "i" ) );

    CHECK( !pack_varsize( "rfbBxVFzZcCdDluULjJqi" ) );
}

TEST_CASE("pack var-size with all-variable specifiers") {
    CHECK( pack_varsize( "s" ) );
    CHECK( pack_varsize( "S" ) );
    CHECK( pack_varsize( "o" ) );
    CHECK( pack_varsize( "O" ) );
    CHECK( pack_varsize( "A" ) );
    CHECK( pack_varsize( "Q" ) );

    CHECK( pack_varsize( "sSoOAQ" ) );
}

namespace {

int packsize( const char* fmt ) {
    int size;
    CHECK( dlis_pack_size( fmt, nullptr, &size ) == DLIS_OK );
    return size;
};

}

TEST_CASE("pack size single values") {
    CHECK( packsize( "r" ) == 4 );
    CHECK( packsize( "f" ) == 4 );
    CHECK( packsize( "b" ) == 8 );
    CHECK( packsize( "B" ) == 12 );
    CHECK( packsize( "x" ) == 4 );
    CHECK( packsize( "V" ) == 4 );
    CHECK( packsize( "F" ) == 8 );
    CHECK( packsize( "z" ) == 16 );
    CHECK( packsize( "Z" ) == 24 );
    CHECK( packsize( "c" ) == 8 );
    CHECK( packsize( "C" ) == 16 );
    CHECK( packsize( "d" ) == 1 );
    CHECK( packsize( "D" ) == 2 );
    CHECK( packsize( "l" ) == 4 );
    CHECK( packsize( "u" ) == 1 );
    CHECK( packsize( "U" ) == 2 );
    CHECK( packsize( "L" ) == 4 );
    CHECK( packsize( "i" ) == 4 );
    CHECK( packsize( "j" ) == 32 );
    CHECK( packsize( "J" ) == 4 );
    CHECK( packsize( "q" ) == 1 );
}
