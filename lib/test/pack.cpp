#include <array>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>

#include <catch2/catch.hpp>

#include <dlisio/dlisio.h>


namespace {

struct check_packflen {
    const char* fmt;
    std::vector< char > buffer;
    std::vector< unsigned char > source;

    ~check_packflen() {
        int nread, nwrite;
        const auto err = dlis_packflen(fmt, source.data(), &nread, &nwrite);
        CHECK(err == DLIS_OK);
        CHECK(nread == source.size());
        CHECK(nwrite == buffer.size());
    }
};

struct check_packsize : check_packflen {
    ~check_packsize() {
        pck_check_pack_size();
        pck_check_pack_varsize();
    }

    private:

    void pck_check_pack_size(){
        std::int32_t src_size;
        std::int32_t dst_size;
        const auto err = dlis_pack_size( fmt, &src_size, &dst_size );
        CHECK( !err );
        CHECK( src_size == source.size() );
        CHECK( dst_size == buffer.size() );
    }

    void pck_check_pack_varsize(){
        int src_variable;
        int dst_variable;
        const auto err = dlis_pack_varsize( fmt, &src_variable, &dst_variable );
        CHECK( !err );
        CHECK( !src_variable );
        CHECK( !dst_variable );
    }
};

struct check_mixed_packsize : check_packflen {
    ~check_mixed_packsize() {
        mix_check_pack_size();
        mix_check_pack_varsize();
    }

    private:

    void mix_check_pack_size(){
        std::int32_t src_size;
        std::int32_t dst_size;
        const auto err = dlis_pack_size( fmt, &src_size, &dst_size );
        CHECK( !err );
        CHECK( src_size == 0 );
        CHECK( dst_size == buffer.size() );
    }

    void mix_check_pack_varsize(){
        int src_variable;
        int dst_variable;
        const auto err = dlis_pack_varsize( fmt, &src_variable, &dst_variable );
        CHECK( !err );
        CHECK(  src_variable );
        CHECK( !dst_variable );
    }

};

}

TEST_CASE_METHOD(check_mixed_packsize, "pack UVARIs and ORIGINs", "[pack]") {
    source = {
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

    const auto err = dlis_packf( fmt, source.data(), dst );

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

TEST_CASE_METHOD(check_mixed_packsize,
                 "pack UVARIs and ORIGINs of diff size", "[pack]") {
    source = {
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

    fmt = "iiiJiiJii";
    std::int32_t dst[ 9 ];
    buffer.resize(sizeof(dst));

    const auto err = dlis_packf( fmt, source.data(), dst );

    CHECK( err == DLIS_OK );
    CHECK( dst[ 0 ] == 1 );
    CHECK( dst[ 1 ] == 256 );
    CHECK( dst[ 2 ] == 36863 );
    CHECK( dst[ 3 ] == 805355519 );
    CHECK( dst[ 4 ] == 16384 );
    CHECK( dst[ 5 ] == 16383 );
    CHECK( dst[ 6 ] == 128 );
    CHECK( dst[ 7 ] == 127 );
    CHECK( dst[ 8 ] == 1 );
}

TEST_CASE_METHOD(check_packsize, "pack unsigned integers", "[pack]") {
    source = {
        0x59, // 89 ushort
        0xA7, // 167 ushort
        0x00, 0x99, // 153 unorm
        0x80, 0x00, // 32768 unorm
        0x00, 0x00, 0x00, 0x99, // 153 ulong
        0xFF, 0xFF, 0xFF, 0x67, // 4294967143 ulong
    };

    fmt = "uuUULL";
    buffer.resize((1 * 2) + (2 * 2) + (4 * 2));
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source.data(), dst );
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
}



TEST_CASE_METHOD(check_packsize, "pack signed integers", "[pack]") {
    source = {
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

    const auto err = dlis_packf( fmt, source.data(), dst );
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
    source = {
        0x4C, 0x88, // 153 fshort
        0x80, 0x00, //-1 fshort
        0x3F, 0x80, 0x00, 0x00, //1 fsingl
        0xC3, 0x19, 0x00, 0x00, //-153 fsingl
        0xC1, 0xC0, 0x00, 0x00, //-12 isingl
        0x45, 0x10, 0x00, 0x08, //65536.5 isingl
        0xAA, 0xC2, 0x00, 0x00, //-21.25 vsingl
        0x00, 0x3F, 0x00, 0x00, //0.125 vsingl
    };

    fmt = "rrffxxVV";
    buffer.resize(8 * sizeof(float));
    float* dst = reinterpret_cast< float* >( buffer.data() );

    const auto err = dlis_packf( fmt, source.data(), dst );
    CHECK( err == DLIS_OK );

    CHECK( dst[ 0 ] == 153.0 );
    CHECK( dst[ 1 ] == -1.0 );
    CHECK( dst[ 2 ] == 1.0 );
    CHECK( dst[ 3 ] == -153.0 );
    CHECK( dst[ 4 ] == -12 );
    CHECK( dst[ 5 ] == 65536.5 );
    CHECK( dst[ 6 ] == -21.25 );
    CHECK( dst[ 7 ] == 0.125 );
}

TEST_CASE_METHOD(check_packsize, "pack statistical", "[pack]") {
    source = {
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

    const auto err = dlis_packf( fmt, source.data(), dst );
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
    source = {
        0x3F, 0xD0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,// 0.25 fdouble
        0xC2, 0xF3, 0x78, 0x5F, 0x66, 0x30, 0x1C, 0x0A,// -342523480572352.625
        0x43, 0x09, 0x94, 0x5C, 0xA2, 0x62, 0x00, 0x04,// 900000000000000.5
    };

    buffer.resize( 3 * sizeof(double) );
    fmt = "FFF";
    auto* dst = reinterpret_cast< double* >( buffer.data() );

    const auto err = dlis_packf( fmt, source.data(), dst );
    CHECK( err == DLIS_OK );

    CHECK( dst[ 0 ] == 0.25 );
    CHECK( dst[ 1 ] == -342523480572352.625 );
    CHECK( dst[ 2 ] == 900000000000000.5 );
}

TEST_CASE_METHOD(check_packsize, "pack complex", "[pack]") {
    source = {
        0x41, 0x2C, 0x00, 0x00, //10.75 csingl R
        0xC1, 0x10, 0x00, 0x00, //-9 csing1 I
        0x40, 0x3C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, //28 cdoubl R
        0x40, 0x42, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, //36.5 cdoub1 I
    };

    fmt = "cC";
    buffer.resize( 4 * 2 + 8 * 2 );
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source.data(), dst );
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
    source = {
        // 255Y 2TZ 12M 31D 0H 32MN 16S 0MS
        0xFF, 0x2C, 0x1F, 0x00, 0x20, 0x10, 0x00, 0x00,

        // 0Y 0TZ 1M 1D 23H 59M 0S 999MS
        0x00, 0x01, 0x01, 0x17, 0x3B, 0x00, 0x03, 0xE7,
    };

    fmt = "jj";
    buffer.resize( 2 * 8 * sizeof(int) );
    auto* dst = reinterpret_cast< int* >( buffer.data() );

    const auto err = dlis_packf( fmt, source.data(), dst );
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
    source = {
        0x00, // 0 status
        0x01, // 1 status
    };

    buffer.resize( 2 );
    fmt = "qq";
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source.data(), dst );
    CHECK( err == DLIS_OK );

    CHECK( !dst[ 0 ] );
    CHECK(  dst[ 1 ] );
}

namespace {

struct check_is_varsize {
    ~check_is_varsize () {
        int src_variable;
        int dst_variable;
        auto err = dlis_pack_varsize( fmt, &src_variable, &dst_variable );
        CHECK( err == DLIS_OK );
        CHECK( src_variable );
        CHECK( dst_variable );

        err = dlis_pack_size( fmt, &src_variable, &dst_variable);
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

TEST_CASE_METHOD(check_mixed_packsize, "pack mixed", "[pack]") {
    source = {
        0x4C, 0x88, // 153 fshort
        0x81, 0x00, // 256 uvari
        // 254Y 2TZ 12M 30D 1H 33MN 17S 1MS
        0xFE, 0x2C, 0x1E, 0x01, 0x21, 0x11, 0x00, 0x01,
        0x81, 0x01, // 257 origin
    };

    buffer.resize( 4  + 4 + 32 + 4 );
    fmt = "rijJ";
    auto* dst = buffer.data();

    const auto err = dlis_packf( fmt, source.data(), dst );
    CHECK( err == DLIS_OK );

    float fl[1];
    std::memcpy( fl, dst, sizeof(fl) );
    CHECK( fl[ 0 ] == 153.0 );

    std::uint32_t in[10];
    std::memcpy( in, dst + 4, sizeof(in) );
    CHECK( in[ 0 ] == 256 );
    CHECK( in[ 1 ] == 254 );
    CHECK( in[ 8 ] == 1 );
    CHECK( in[ 9 ] == 257 );
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

bool dst_pack_varsize( const char* fmt ) {
    int vsize;
    CHECK( dlis_pack_varsize( fmt, nullptr, &vsize ) == DLIS_OK );
    return vsize;
};

bool src_pack_varsize( const char* fmt ) {
    int vsize;
    CHECK( dlis_pack_varsize( fmt, &vsize, nullptr ) == DLIS_OK );
    return vsize;
};

}

TEST_CASE("destination pack var-size with all-constant specifiers") {
    CHECK( !dst_pack_varsize( "r" ) );
    CHECK( !dst_pack_varsize( "f" ) );
    CHECK( !dst_pack_varsize( "b" ) );
    CHECK( !dst_pack_varsize( "B" ) );
    CHECK( !dst_pack_varsize( "x" ) );
    CHECK( !dst_pack_varsize( "V" ) );
    CHECK( !dst_pack_varsize( "F" ) );
    CHECK( !dst_pack_varsize( "z" ) );
    CHECK( !dst_pack_varsize( "Z" ) );
    CHECK( !dst_pack_varsize( "c" ) );
    CHECK( !dst_pack_varsize( "C" ) );
    CHECK( !dst_pack_varsize( "d" ) );
    CHECK( !dst_pack_varsize( "D" ) );
    CHECK( !dst_pack_varsize( "l" ) );
    CHECK( !dst_pack_varsize( "u" ) );
    CHECK( !dst_pack_varsize( "U" ) );
    CHECK( !dst_pack_varsize( "L" ) );
    CHECK( !dst_pack_varsize( "j" ) );
    CHECK( !dst_pack_varsize( "J" ) );
    CHECK( !dst_pack_varsize( "q" ) );
    CHECK( !dst_pack_varsize( "i" ) );

    CHECK( !dst_pack_varsize( "rfbBxVFzZcCdDluULjJqi" ) );
}

TEST_CASE("destination pack var-size with all-variable specifiers") {
    CHECK( dst_pack_varsize( "s" ) );
    CHECK( dst_pack_varsize( "S" ) );
    CHECK( dst_pack_varsize( "o" ) );
    CHECK( dst_pack_varsize( "O" ) );
    CHECK( dst_pack_varsize( "A" ) );
    CHECK( dst_pack_varsize( "Q" ) );

    CHECK( dst_pack_varsize( "sSoOAQ" ) );
}


TEST_CASE("source pack var-size with all-constant specifiers") {
    CHECK( !src_pack_varsize( "r" ) );
    CHECK( !src_pack_varsize( "f" ) );
    CHECK( !src_pack_varsize( "b" ) );
    CHECK( !src_pack_varsize( "B" ) );
    CHECK( !src_pack_varsize( "x" ) );
    CHECK( !src_pack_varsize( "V" ) );
    CHECK( !src_pack_varsize( "F" ) );
    CHECK( !src_pack_varsize( "z" ) );
    CHECK( !src_pack_varsize( "Z" ) );
    CHECK( !src_pack_varsize( "c" ) );
    CHECK( !src_pack_varsize( "C" ) );
    CHECK( !src_pack_varsize( "d" ) );
    CHECK( !src_pack_varsize( "D" ) );
    CHECK( !src_pack_varsize( "l" ) );
    CHECK( !src_pack_varsize( "u" ) );
    CHECK( !src_pack_varsize( "U" ) );
    CHECK( !src_pack_varsize( "L" ) );
    CHECK( !src_pack_varsize( "j" ) );
    CHECK( !src_pack_varsize( "q" ) );

    CHECK( !src_pack_varsize( "rfbBxVFzZcCdDluULjq" ) );
}

TEST_CASE("source pack var-size with all-variable specifiers") {
    CHECK( src_pack_varsize( "s" ) );
    CHECK( src_pack_varsize( "S" ) );
    CHECK( src_pack_varsize( "o" ) );
    CHECK( src_pack_varsize( "O" ) );
    CHECK( src_pack_varsize( "A" ) );
    CHECK( src_pack_varsize( "Q" ) );
    CHECK( src_pack_varsize( "J" ) );
    CHECK( src_pack_varsize( "i" ) );

    CHECK( src_pack_varsize( "sSoOAQiJ" ) );
}

namespace {

int dst_packsize( const char* fmt ) {
    int size;
    CHECK( dlis_pack_size( fmt, nullptr, &size ) == DLIS_OK );
    return size;
};


int src_packsize( const char* fmt ) {
    int size;
    CHECK( dlis_pack_size( fmt, &size, nullptr ) == DLIS_OK );
    return size;
};

}

TEST_CASE("destination pack size single values consisent") {
    CHECK( dst_packsize( "r" ) == 4 );
    CHECK( dst_packsize( "f" ) == 4 );
    CHECK( dst_packsize( "b" ) == 8 );
    CHECK( dst_packsize( "B" ) == 12 );
    CHECK( dst_packsize( "x" ) == 4 );
    CHECK( dst_packsize( "V" ) == 4 );
    CHECK( dst_packsize( "F" ) == 8 );
    CHECK( dst_packsize( "z" ) == 16 );
    CHECK( dst_packsize( "Z" ) == 24 );
    CHECK( dst_packsize( "c" ) == 8 );
    CHECK( dst_packsize( "C" ) == 16 );
    CHECK( dst_packsize( "d" ) == 1 );
    CHECK( dst_packsize( "D" ) == 2 );
    CHECK( dst_packsize( "l" ) == 4 );
    CHECK( dst_packsize( "u" ) == 1 );
    CHECK( dst_packsize( "U" ) == 2 );
    CHECK( dst_packsize( "L" ) == 4 );
    CHECK( dst_packsize( "i" ) == 4 );
    CHECK( dst_packsize( "j" ) == 32 );
    CHECK( dst_packsize( "J" ) == 4 );
    CHECK( dst_packsize( "q" ) == 1 );
}

TEST_CASE("source pack size single values consistent") {
    CHECK( src_packsize( "r" ) == 2 );
    CHECK( src_packsize( "f" ) == 4 );
    CHECK( src_packsize( "b" ) == 8 );
    CHECK( src_packsize( "B" ) == 12 );
    CHECK( src_packsize( "x" ) == 4 );
    CHECK( src_packsize( "V" ) == 4 );
    CHECK( src_packsize( "F" ) == 8 );
    CHECK( src_packsize( "z" ) == 16 );
    CHECK( src_packsize( "Z" ) == 24 );
    CHECK( src_packsize( "c" ) == 8 );
    CHECK( src_packsize( "C" ) == 16 );
    CHECK( src_packsize( "d" ) == 1 );
    CHECK( src_packsize( "D" ) == 2 );
    CHECK( src_packsize( "l" ) == 4 );
    CHECK( src_packsize( "u" ) == 1 );
    CHECK( src_packsize( "U" ) == 2 );
    CHECK( src_packsize( "L" ) == 4 );
    CHECK( src_packsize( "j" ) == 8 );
    CHECK( src_packsize( "q" ) == 1 );

    CHECK( src_packsize( "i" ) == 0 );
    CHECK( src_packsize( "J" ) == 0 );
}

TEST_CASE("pack size single values inconsistent") {
    CHECK( dlis_pack_size( "s" , nullptr, nullptr ) == DLIS_INCONSISTENT );
    CHECK( dlis_pack_size( "S" , nullptr, nullptr ) == DLIS_INCONSISTENT );
    CHECK( dlis_pack_size( "o" , nullptr, nullptr ) == DLIS_INCONSISTENT );
    CHECK( dlis_pack_size( "O" , nullptr, nullptr ) == DLIS_INCONSISTENT );
    CHECK( dlis_pack_size( "A" , nullptr, nullptr ) == DLIS_INCONSISTENT );
    CHECK( dlis_pack_size( "Q" , nullptr, nullptr ) == DLIS_INCONSISTENT );
}
