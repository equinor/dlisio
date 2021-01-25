
#include <catch2/catch.hpp>

#include <dlisio/lis/types.hpp>
#include <dlisio/lis/protocol.hpp>

using namespace Catch::Matchers;
namespace lis = dlisio::lis79;


TEST_CASE("A Logical Record Header can be read", "[protocol]") { }
TEST_CASE("A Physical Record Header can be read", "[protocol]") { }

TEST_CASE("Pad-bytes are correctly identified", "[protocol]") { }

TEST_CASE("Valid repcodes", "[protocol]") { }

TEST_CASE("Entry Block", "[protocol]") {
    SECTION("Well-formatted - lis::i8") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x01, // Type
            0x01, // Size
            0x38, // Representation code 56 (lis::i8)
            0x00, // Entry
        };

        std::size_t offset = 0;
        const auto entry = lis::read_entry_block( rec, &offset );

        CHECK( offset == 4 );
        CHECK( lis::decay(entry.type)  == 1  );
        CHECK( lis::decay(entry.size)  == 1  );
        CHECK( lis::decay(entry.reprc) == 56 );

        CHECK( mpark::holds_alternative< lis::i8 >(entry.value) );
        const auto value = lis::decay( mpark::get< lis::i8 >(entry.value) );
        CHECK( value == 0 );
    }

    SECTION("Well-formatted - lis::string") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x09, // Type
            0x04, // Size
            0x41, // Representation code 65 (lis::string)
            0x2E, 0x31, 0x49, 0x4E  // Entry
        };

        std::size_t offset = 0;
        const auto entry = lis::read_entry_block( rec, &offset );

        CHECK( offset == 7 );
        CHECK( lis::decay(entry.type)  == 9  );
        CHECK( lis::decay(entry.size)  == 4  );
        CHECK( lis::decay(entry.reprc) == 65 );

        CHECK( mpark::holds_alternative< lis::string >(entry.value) );
        const auto value = lis::decay( mpark::get< lis::string >(entry.value) );
        CHECK( value == std::string(".1IN") );
    }

    SECTION("Can be read from arbitrary offset") { /* TODO */ }
    SECTION("Too little data to parse entry") { /* TODO */ }
}

TEST_CASE("Spec Block", "[protocol]") {
    lis::record rec;
    rec.data = std::vector< char > {
        0x44, 0x45, 0x50, 0x54,                         // "DEPT"
        0x53, 0x4C, 0x42, 0x20, 0x20, 0x20,             // "SLB     " (blank)
        0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x35, 0x34, // "      54"
        0x2E, 0x31, 0x49, 0x4E,                         // ".1IN"
        0x30, 0x31, 0x32, 0x33,                         // 0123
        0x00, 0x01,                                     // 1
        0x00, 0x08,                                     // size
        0x20, 0x20,                                     // pad-byte
        0x20,                                           // pad-bytes/plevel
        0x02,                                           // nb size
        0x44,                                           // reprc (F32)
        0x20, 0x20, 0x20, 0x20, 0x20,                   // pad-bytes/pindicators
    };

    SECTION("Well-formatted sub-type 0 can be read") {
        std::size_t offset = 0;
        const auto spec = lis::read_spec_block0( rec, &offset );

        CHECK( offset == 40 );

        CHECK( lis::decay(spec.mnemonic)         == std::string("DEPT")     );
        CHECK( lis::decay(spec.service_id)       == std::string("SLB   ")   );
        CHECK( lis::decay(spec.service_order_nr) == std::string("      54") );
        CHECK( lis::decay(spec.units)            == std::string(".1IN")     );
        // TODO API codes
        CHECK( lis::decay(spec.filenr)  ==  1 );
        CHECK( lis::decay(spec.ssize)   ==  8 );
        CHECK( lis::decay(spec.samples) ==  2 );
        CHECK( lis::decay(spec.reprc)   == lis::representation_code::f32 );
    }

    SECTION("Well-formatted sub-type 1 can be read") {}
    SECTION("Too little data to parse entry") { /* TODO */ }


}
TEST_CASE("Data Format Specification Record", "[protocol]") {








}
