#include <catch2/catch.hpp>

#include <dlisio/dlisio.h>

TEST_CASE("A well-formatted visible-record-label", "[vrl][v1]") {
    const unsigned char blob[] = { 0x20, 0x00, 0xff, 0x01 };

    int length, version;
    const auto err = dlis_vrl( (char*)blob, &length, &version );
    CHECK( err == 0 );
    CHECK( length == 8192 );
    CHECK( version == 1 );
}
