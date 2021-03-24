#include <cstdint>
#include <cstring>
#include <limits>
#include <vector>

#include <catch2/catch.hpp>

#include <dlisio/dlis/dlisio.h>
#include <dlisio/lis/pack.h>

namespace {

struct check_packflen {
    const char* fmt;
    std::vector< char > buffer;
    std::vector< unsigned char > source;

    ~check_packflen() {
        int nread, nwrite;
        const auto err = lis_packflen(fmt, source.data(), &nread, &nwrite);
        CHECK(err == DLIS_OK);
        CHECK(nread == source.size());
        CHECK(nwrite == buffer.size());
    }
};

}

TEST_CASE_METHOD(check_packflen, "pack unsigned integers (byte)", "[pack]") {
    source = {
        0x00, // 0 byte
        0x01, // 1 byte
        0x59, // 89 byte
        0x7F, // 127 byte
        0xA7, // 167 byte
        0x80, // 128 byte
        0xFF, // uint-max byte
    };

    fmt = "bbbbbbb";
    buffer.resize(7);
    auto* dst = buffer.data();

    const auto err = lis_packf( fmt, source.data(), dst );
    CHECK( err == DLIS_OK );

    std::uint8_t us[7];
    std::memcpy( us, dst, sizeof(us) );
    CHECK( us[ 0 ] == 0 );
    CHECK( us[ 1 ] == 1 );
    CHECK( us[ 2 ] == 89 );
    CHECK( us[ 3 ] == 127 );
    CHECK( us[ 4 ] == 167 );
    CHECK( us[ 5 ] == 128 );
    CHECK( us[ 6 ] == std::numeric_limits< std::uint8_t >::max() );
}

TEST_CASE_METHOD(check_packflen, "pack signed integers", "[pack]") {
    source = {
        0x59, // 89 i8
        0xA7, // -89 i8
        0x00, 0x99, // 153 i16
        0xFF, 0x67, // -153 i16
        0x00, 0x00, 0x00, 0x99, // 153 i32
        0xFF, 0xFF, 0xFF, 0x67, // -153 i32
        0x7F, 0xFF, 0xFF, 0xFF, // ~2.1b i32 (int-max)
    };

    fmt = "ssiilll";
    buffer.resize((1 * 2) + (2 * 2) + (4 * 3));
    auto* dst = buffer.data();

    const auto err = lis_packf( fmt, source.data(), dst );
    CHECK( err == DLIS_OK );

    std::int8_t i8[2];
    std::memcpy( i8, dst, sizeof( i8 ) );
    CHECK( i8[ 0 ] == 89 );
    CHECK( i8[ 1 ] == -89 );

    std::int16_t i16[2];
    std::memcpy( i16, dst + 2, sizeof( i16 ) );
    CHECK( i16[ 0 ] == 153 );
    CHECK( i16[ 1 ] == -153 );

    std::int32_t i32[3];
    std::memcpy( i32, dst + 6, sizeof( i32 ) );
    CHECK( i32[ 0 ] == 153 );
    CHECK( i32[ 1 ] == -153 );
    CHECK( i32[ 2 ] == 2147483647 );
}

TEST_CASE_METHOD(check_packflen, "pack floats", "[pack]") {
    source = {
        0x4C, 0x88, // 153 f16
        0x80, 0x00, //-1 f16
        0x2A, 0x00, 0x00, 0x00, // 0 f32
        0x44, 0x4C, 0x80, 0x00, // 153 f32
        0xBB, 0xB3, 0x80, 0x00, // -153 f32
        0x00, 0x00, 0x00, 0x00, // 0 f32lowres
        0x00, 0x08, 0x4C, 0x80, // 153 f32lowres
        0x00, 0x08, 0xB3, 0x80, // -153 f32lowres
    };

    fmt = "eefffrrr";
    buffer.resize(8 * sizeof(float));
    float* dst = reinterpret_cast< float* >( buffer.data() );

    const auto err = lis_packf( fmt, source.data(), dst );
    CHECK( err == DLIS_OK );

    CHECK( dst[ 0 ] == 153.0 );
    CHECK( dst[ 1 ] == -1.0 );
    CHECK( dst[ 2 ] == 0.0 );
    CHECK( dst[ 3 ] == 153 );
    CHECK( dst[ 4 ] == -153.0 );
    CHECK( dst[ 5 ] == 0 );
    CHECK( dst[ 6 ] == 153 );
    CHECK( dst[ 7 ] == -153 );
}
