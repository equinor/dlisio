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

TEST_CASE("Component roles", "[component][v1]") {
    const std::uint8_t ABSATTR = 0x11;
    const std::uint8_t ATTR =    0x39;
    const std::uint8_t INVATTR = 0x50;
    const std::uint8_t OBJ =     0x72;
    const std::uint8_t RES =     0x96;
    const std::uint8_t RDSET =   0xB5;
    const std::uint8_t RSET =    0xDA;
    const std::uint8_t SET =     0xFF;

    int role, name;
    SECTION("Set" ) {
        auto const err = dlis_component( SET, &role );
        CHECK( err == DLIS_OK );
        CHECK( role == DLIS_ROLE_SET );
    }

    SECTION("Replacement Set" ) {
        auto const err = dlis_component( RSET, &role );
        CHECK( err == DLIS_OK );
        CHECK( role == DLIS_ROLE_RSET );
    }

    SECTION("Redundant Set" ) {
        auto const err = dlis_component( RDSET, &role );
        CHECK( err == DLIS_OK );
        CHECK( role == DLIS_ROLE_RDSET );
    }

    SECTION("Object" ) {
        auto const err = dlis_component( OBJ, &role );
        CHECK( err == DLIS_OK );
        CHECK( role == DLIS_ROLE_OBJECT );
    }

    SECTION("Attribute" ) {
        auto const err = dlis_component( ATTR, &role );
        CHECK( err == DLIS_OK );
        CHECK( role == DLIS_ROLE_ATTRIB  );
    }

    SECTION("Invariant Attribute" ) {
        auto const err = dlis_component( INVATTR, &role );
        CHECK( err == DLIS_OK );
        CHECK( role == DLIS_ROLE_INVATR );
    }

    SECTION("Absent Attribute" ) {
        auto const err = dlis_component( ABSATTR, &role );
        CHECK( err == DLIS_OK );
        CHECK( role == DLIS_ROLE_ABSATR );
    }

    SECTION("--reserved--" ) {
        auto const err = dlis_component( RES, &role );
        CHECK( err == DLIS_OK );
        CHECK( role == DLIS_ROLE_RESERV );
    }
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
    const std::uint8_t R =  0xA7; // 101 00 111

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
        CHECK( err == DLIS_OK );
    }

    SECTION("SET: ") {
        err = dlis_component_set( Z, role, &type, &name );
        CHECK( !type );
        CHECK( !name );
        CHECK( err == DLIS_OK );
    }

    SECTION("SET: reserved values") {
        err = dlis_component_set( R, DLIS_ROLE_RDSET, &type, &name );
        CHECK( !type );
        CHECK( !name );
        CHECK( err == DLIS_OK );
    }
}

TEST_CASE("Object descriptors", "[component][v1]") {
    const std::uint8_t ON = 0x70;
    const std::uint8_t O  = 0x60;
    const std::uint8_t R  = 0x6F;

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
        CHECK( err == DLIS_OK );
        CHECK( !name );
    }

    SECTION("Object: reserved values") {
        err = dlis_component_object( ON, role, &name );
        CHECK( err == DLIS_OK );
        CHECK( name );
    }
}

TEST_CASE("simple visible record length header", "[dlis_vrl]") {
    static const unsigned char data [] = {
        0x00, 0x22,
        0xFF,
        0x01,
    };

    int len;
    int version;

    const auto err = dlis_vrl((char*) data, &len, &version);
    CHECK( err == DLIS_OK );
    CHECK( len == 34 );
    CHECK( version ==  1);
}

TEST_CASE("find visible envelope after 8 bytes of garbage", "[vrl]") {
    static const unsigned char file[] = {
        /* garbage */
        0x01, 0x02, 0x03, 0x04,
        0x02, 0x03, 0x04, 0x05,

        /* visible envelope */
        0x00, 0x22,
        0xFF,
        0x01,

        /* segment header */
        0x00, 0x04,
        0x1F,
        0x02,
    };

    long long off;
    const auto* ptr = reinterpret_cast< const char* >(file);
    const auto err = dlis_find_vrl(ptr, sizeof(file), &off);

    REQUIRE(!err);
    CHECK(off == 8);
}

TEST_CASE("find visible envelope when there is no garbage", "[vrl]") {
    static const unsigned char file[] = {
        /* visible envelope */
        0x00, 0x22,
        0xFF,
        0x01,

        /* segment header */
        0x00, 0x04,
        0x1F,
        0x02,
    };

    long long off;
    const auto* ptr = reinterpret_cast< const char* >(file);
    const auto err = dlis_find_vrl(ptr, sizeof(file), &off);

    REQUIRE(!err);
    CHECK(off == 0);
}

TEST_CASE("find_vrl gracefully handles missing envelope", "[vrl]") {
    const auto file = std::vector< char >(400, '.');
    long long off;
    const auto err = dlis_find_vrl(file.data(), file.size() / 2, &off);
    CHECK(err == DLIS_NOTFOUND);
}

TEST_CASE("find_vrl gracefully handles truncated envelope", "[vrl]") {
    static const unsigned char file[] = {
        /* truncated header */
        /* 0x00, */ 0x08,
        0xFF,
        0x01,

        /* segment header */
        0x00, 0x04,
        0x1F,
        0x02,
    };

    long long off;
    const auto* ptr = reinterpret_cast< const char* >(file);
    const auto err = dlis_find_vrl(ptr, sizeof(file), &off);
    CHECK(err == DLIS_INCONSISTENT);
}

TEST_CASE("simple logical record segment header", "[dlis_lrsh]") {
    static const unsigned char data [] = {
        0x00, 0x24,
        0x1F,
        0x02,
    };

    int length;
    uint8_t attrs;
    int type;

    const auto err = dlis_lrsh((char*) data, &length, &attrs, &type);
    CHECK( err == DLIS_OK );
    CHECK( length == 36 );
    CHECK( attrs == 31 );
    CHECK( type == 2 );
}

TEST_CASE("Attribute descriptors", "[component][v1]") {
    int role;
    int label, count, reprc, units, value;

    const std::uint8_t A   = 0x20;
    const std::uint8_t LRV = 0x35;
    const std::uint8_t L   = 0x30;
    const std::uint8_t CU  = 0x4A;

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
        err = dlis_component_attrib( L, DLIS_ROLE_INVATR,
                                              &label,
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

    SECTION("Attribute: CU") {
        err = dlis_component_attrib( CU, role, &label,
                                               &count,
                                               &reprc,
                                               &units,
                                               &value );
        CHECK( err == DLIS_OK );

        CHECK( !label );
        CHECK(  count );
        CHECK( !reprc );
        CHECK(  units );
        CHECK( !value );
    }
}

TEST_CASE("dlis comp string") {
    SECTION("DLIS_ROLE_ABSATR"){
        CHECK( std::string(dlis_component_str(DLIS_ROLE_ABSATR))
              == "absent attribute");
    }
    SECTION("DLIS_ROLE_ATTRIB"){
        CHECK( std::string(dlis_component_str(DLIS_ROLE_ATTRIB))
              == "attribute");
    }
    SECTION("DLIS_ROLE_INVATR"){
        CHECK( std::string(dlis_component_str(DLIS_ROLE_INVATR))
              == "invariant attribute");
    }
    SECTION("DLIS_ROLE_OBJECT"){
        CHECK( std::string(dlis_component_str(DLIS_ROLE_OBJECT))
              == "object");
    }
    SECTION("DLIS_ROLE_RESERV"){
        CHECK( std::string(dlis_component_str(DLIS_ROLE_RESERV))
              == "reserved");
    }
    SECTION("DLIS_ROLE_RDSET"){
        CHECK( std::string(dlis_component_str(DLIS_ROLE_RDSET))
              == "redundant set");
    }
    SECTION("DLIS_ROLE_RSET"){
        CHECK( std::string(dlis_component_str(DLIS_ROLE_RSET))
              == "replacement set");
    }
    SECTION("DLIS_ROLE_SET"){
        CHECK( std::string(dlis_component_str(DLIS_ROLE_SET))
              == "set");
    }
    SECTION("uknown"){
        CHECK( std::string(dlis_component_str(9819))
              == "unknown");
    }
}


TEST_CASE("fingerprint matches bytes written") {
    std::string type = "CHANNEL";
    std::string id = "IDENT";
    auto origin = 0;
    auto copy = 3;

    int size;
    auto err = dlis_object_fingerprint_size(
        type.size(),
        type.data(),
        id.size(),
        id.data(),
        origin,
        copy,
        &size);

    CHECK(!err);
    CHECK(size > 0);

    std::vector< char > buffer(1024, 0);
    err = dlis_object_fingerprint(
        type.size(),
        type.data(),
        id.size(),
        id.data(),
        origin,
        copy,
        buffer.data());

    CHECK(!err);

    auto fingerprint = std::string(buffer.data());
    CHECK(fingerprint.size() == size);
    CHECK(fingerprint == "T.CHANNEL-I.IDENT-O.0-C.3");
}

TEST_CASE("fingerprint on empty string") {
    SECTION("failure when type is empty") {
        std::string type = "";
        std::string id = "IDENT";
        auto origin = 0;
        auto copy = 0;

        std::vector< char > buffer(1024, 0);
        auto err = dlis_object_fingerprint(
            type.size(),
            type.data(),
            id.size(),
            id.data(),
            origin,
            copy,
            buffer.data());

        CHECK( err == DLIS_INVALID_ARGS );
    };

    SECTION("pass when id is empty") {
        std::string type = "CHANNEL";
        std::string id = "";
        auto origin = 0;
        auto copy = 0;

        int size;
        auto err = dlis_object_fingerprint_size(
            type.size(),
            type.data(),
            id.size(),
            id.data(),
            origin,
            copy,
            &size);

        CHECK(!err);
        CHECK(size > 0);

        std::vector< char > buffer(1024, 0);
        err = dlis_object_fingerprint(
            type.size(),
            type.data(),
            id.size(),
            id.data(),
            origin,
            copy,
            buffer.data());

        CHECK(!err);

        auto fingerprint = std::string(buffer.data());
        CHECK(fingerprint.size() == size);
    };
}

namespace {

struct basic_segment {
    basic_segment() : segment(50, '.') {
        this->begin = this->segment.data();
        this->end = this->segment.data() + this->segment.size();
    }

    std::vector< char > segment;
    const char* begin;
    const char* end;
};

}

TEST_CASE_METHOD(
    basic_segment,
    "trimming segment with nothing to trim leaves it unchanged") {
    const auto expected = 0;
    int size;

    const std::uint8_t attrs = 0;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(!err);
    CHECK(size == expected);
}

TEST_CASE_METHOD(
    basic_segment,
    "trimming segment with checksum trims 2 bytes") {
    const auto expected = 2;
    int size = 0;

    const std::uint8_t attrs = DLIS_SEGATTR_CHCKSUM;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(!err);
    CHECK(size == expected);
}

TEST_CASE_METHOD(
    basic_segment,
    "trimming segment with trailing len trims 2 bytes") {
    const auto expected = 2;
    int size = 0;

    const std::uint8_t attrs = DLIS_SEGATTR_TRAILEN;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(!err);
    CHECK(size == expected);
}

TEST_CASE_METHOD(
    basic_segment,
    "trimming segment with trailing len and checksum trims 4 bytes") {
    const auto expected = 4;
    int size = 0;

    const std::uint8_t attrs = DLIS_SEGATTR_TRAILEN
                             | DLIS_SEGATTR_CHCKSUM
                             ;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(!err);
    CHECK(size == expected);
}

TEST_CASE_METHOD(
    basic_segment,
    "trimming segment with padding trims pad bytes") {
    const auto pad_len = 8;
    segment.back() = pad_len;
    const auto expected = 8;
    int size = 0;

    const std::uint8_t attrs = DLIS_SEGATTR_PADDING;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(!err);
    CHECK(size == expected);
}

TEST_CASE_METHOD(
    basic_segment,
    "trimming segment with padding, checksum and trailing len trims") {
    const auto pad_len = 8;
    segment[segment.size() - 5] = pad_len;
    const auto expected = pad_len + 4;
    int size = 0;

    const std::uint8_t attrs = DLIS_SEGATTR_PADDING
                             | DLIS_SEGATTR_CHCKSUM
                             | DLIS_SEGATTR_TRAILEN
                             ;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(!err);
    CHECK(size == expected);
}

TEST_CASE_METHOD(
    basic_segment,
    "padding full segment") {
    const auto pad_len = segment.size();
    segment.back() = pad_len;

    int size = 0;
    const std::uint8_t attrs = DLIS_SEGATTR_PADDING;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(!err);
    CHECK(size == pad_len);
}

TEST_CASE_METHOD(
    basic_segment,
    "padding larger than segment") {
    const auto pad_len = segment.size() + 8;
    segment.back() = pad_len;

    int size = 0;
    const std::uint8_t attrs = DLIS_SEGATTR_PADDING;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(err == DLIS_BAD_SIZE);
    CHECK(size == pad_len);
}

TEST_CASE_METHOD(
    basic_segment,
    "padding larger than segment with checksum") {
    const auto pad_len = segment.size() + 8;
    const auto expected = pad_len + 2;
    segment[segment.size() - 3] = pad_len;

    int size = 0;
    const std::uint8_t attrs = DLIS_SEGATTR_PADDING
                             | DLIS_SEGATTR_CHCKSUM
                             ;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(err == DLIS_BAD_SIZE);
    CHECK(size == expected);
}

TEST_CASE_METHOD(
    basic_segment,
    "padding larger than segment with trailing len for encrypted rec") {
    const auto pad_len = segment.size() + 8;
    const auto expected = 0;
    segment[segment.size() - 3] = pad_len;

    int size = 0;
    const std::uint8_t attrs = DLIS_SEGATTR_PADDING
                             | DLIS_SEGATTR_TRAILEN
                             | DLIS_SEGATTR_ENCRYPT
                             ;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &size);

    CHECK(!err);
    CHECK(size == expected);
}
