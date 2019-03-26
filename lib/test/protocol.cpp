#include <cstdint>

#include <catch2/catch.hpp>

#include <dlisio/dlisio.h>


TEST_CASE("A well-formatted logical record segment header", "[lrsh][v1]") {
    const char lrsh[] = {
        0x00, 0x7c, // 124 in big-endian
        0x01,       // has-padding only
        0x00,       // type (0 = File-Header)
    };

    int length = 0;
    std::uint8_t attrs = 0;
    int type = 0;

    dlis_lrsh( lrsh, &length, &attrs, &type );

    CHECK( length == 124 );
    CHECK( type == 0 );

    int explicit_formatting = 0;
    int has_predecessor = 0;
    int has_successor = 0;
    int is_encrypted = 0;
    int has_encryption_packet = 0;
    int has_checksum = 0;
    int has_trailing_length = 0;
    int has_padding = 0;

    dlis_segment_attributes( attrs,
                             &explicit_formatting,
                             &has_predecessor,
                             &has_successor,
                             &is_encrypted,
                             &has_encryption_packet,
                             &has_checksum,
                             &has_trailing_length,
                             &has_padding );

    CHECK_FALSE( explicit_formatting );
    CHECK_FALSE( has_predecessor );
    CHECK_FALSE( has_successor );
    CHECK_FALSE( is_encrypted );
    CHECK_FALSE( has_encryption_packet );
    CHECK_FALSE( has_checksum );
    CHECK_FALSE( has_trailing_length );
    CHECK( has_padding );

}

TEST_CASE("An empty encryption packet", "[encpk][v1]") {
    const char encpk[] = {
        0x00, 0x04,
        0x00, 0x00,
    };

    int len = -1;
    int cc = -1;
    auto err = dlis_encryption_packet_info( encpk, &len, &cc );

    CHECK( err == DLIS_OK );
    CHECK( len == 0 );
    CHECK( cc == 0 );
}

TEST_CASE("A non-empty encryption packet", "[encpk][v1]") {
    const char encpk[] = {
        0x00, 0x08,
        0x00, 0x03,
    };

    int len = -1;
    int cc = -1;
    auto err = dlis_encryption_packet_info( encpk, &len, &cc );

    CHECK( err == DLIS_OK );
    CHECK( len == 4 );
    CHECK( cc == 3 );
}

TEST_CASE("A non-even encryption packet", "[encpk][v1]") {
    const char encpk[] = {
        0x00, 0x07,
        0x00, 0x03,
    };

    int len = -1;
    int cc = -1;
    auto err = dlis_encryption_packet_info( encpk, &len, &cc );

    CHECK( err == DLIS_UNEXPECTED_VALUE );
}

TEST_CASE("A too small encryption packet", "[encpk][v1]") {
    const char encpk[] = {
        0x00, 0x03,
        0x00, 0x07,
    };

    int len = -1;
    int cc = -1;
    auto err = dlis_encryption_packet_info( encpk, &len, &cc );

    CHECK( err == DLIS_INCONSISTENT );
}

TEST_CASE("Set descriptors", "[component][v1]") {
    int role, type, name;
    int err = dlis_component( 0xF8, &role );
    CHECK( err == DLIS_OK );
    CHECK( role == DLIS_ROLE_SET );

    const std::uint8_t TN = 0xF8; // 111 11 xxx
    const std::uint8_t T  = 0xF0; // 111 10 xxx
    const std::uint8_t N  = 0xE8; // 111 01 xxx
    const std::uint8_t Z  = 0xE0; // 111 00 xxx

    SECTION("Unexpected value" ) {
        err = dlis_component_set( 0xF8, DLIS_ROLE_OBJECT, &type, &name );
        CHECK( err == DLIS_UNEXPECTED_VALUE );
    }

    SECTION("SET: type name") {
        err = dlis_component_set( TN, role, &type, &name );
        CHECK( type );
        CHECK( name );
        CHECK( err == DLIS_OK );
    }

    SECTION("SET: type") {
        err = dlis_component_set( T, role, &type, &name );
        CHECK( type );
        INFO( name );
        CHECK( !name );
        CHECK( err == DLIS_OK );
    }

    SECTION("SET: name") {
        err = dlis_component_set( N, role, &type, &name );
        CHECK( !type );
        CHECK( name );
        CHECK( err == DLIS_INCONSISTENT );
    }

    SECTION("SET: ") {
        err = dlis_component_set( Z, role, &type, &name );
        CHECK( !type );
        CHECK( !name );
        CHECK( err == DLIS_INCONSISTENT );
    }
}

TEST_CASE("Object descriptors", "[component][v1]") {
    const std::uint8_t ON = 0x70;
    const std::uint8_t O  = 0x60;

    int role, name;
    int err = dlis_component( ON, &role );
    CHECK( err == DLIS_OK );
    CHECK( role == DLIS_ROLE_OBJECT );

    SECTION("Unexpected value" ) {
        err = dlis_component_object( ON, DLIS_ROLE_RDSET, &name );
        CHECK( err == DLIS_UNEXPECTED_VALUE );
    }

    SECTION("Object: name") {
        err = dlis_component_object( ON, role, &name );
        CHECK( err == DLIS_OK );
        CHECK( name );
    }

    SECTION("Object: ") {
        err = dlis_component_object( O, role, &name );
        CHECK( err == DLIS_INCONSISTENT );
        CHECK( !name );
    }
}


TEST_CASE("Attribute descriptors", "[component][v1]") {
    int role;
    int label, count, reprc, units, value;

    const std::uint8_t A   = 0x20;
    const std::uint8_t LRV = 0x35;
    const std::uint8_t L   = 0x30;

    int err = dlis_component( A, &role );
    CHECK( err == DLIS_OK );
    CHECK( role == DLIS_ROLE_ATTRIB );

    SECTION("Attribute: LRV") {
        err = dlis_component_attrib( LRV, role, &label,
                                                &count,
                                                &reprc,
                                                &units,
                                                &value );
        CHECK( err == DLIS_OK );

        CHECK(  label );
        CHECK( !count );
        CHECK(  reprc );
        CHECK( !units );
        CHECK(  value );
    }

    SECTION("Attribute: L") {
        err = dlis_component_attrib( L, role, &label,
                                              &count,
                                              &reprc,
                                              &units,
                                              &value );
        CHECK( err == DLIS_OK );

        CHECK(  label );
        CHECK( !count );
        CHECK( !reprc );
        CHECK( !units );
        CHECK( !value );
    }
}

TEST_CASE("fingerprint length matches bytes written") {
    std::string type = "CHANNEL";
    std::string id = "IDENT";
    auto origin = 0;
    auto copy = 0;

    auto len = dlis_object_fingerprint_len(
        type.size(),
        type.data(),
        id.size(),
        id.data(),
        origin,
        copy);

    CHECK(len > 0);

    std::vector< char > buffer(1024, 0);
    auto err = dlis_object_fingerprint(
        type.size(),
        type.data(),
        id.size(),
        id.data(),
        origin,
        copy,
        buffer.data());

    CHECK(!err);

    auto fingerprint = std::string(buffer.data());
    CHECK(fingerprint.size() == len);
}
