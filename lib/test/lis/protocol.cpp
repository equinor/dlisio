
#include <catch2/catch.hpp>

#include <dlisio/exception.hpp>
#include <dlisio/lis/types.hpp>
#include <dlisio/lis/protocol.hpp>

using namespace Catch::Matchers;
namespace lis = dlisio::lis79;


TEST_CASE("A Logical Record Header can be read", "[protocol]") { }
TEST_CASE("A Physical Record Header can be read", "[protocol]") { }

TEST_CASE("Pad-bytes are correctly identified", "[protocol]") { }

TEST_CASE("Valid repcodes", "[protocol]") { }

TEST_CASE("Record type strings") {
    using rectype = lis::record_type;
    SECTION("Normal Data") {
        CHECK( lis::record_type_str(rectype::normal_data) ==
               "Normal Data" );
    }
    SECTION("Alternate Data") {
        CHECK( lis::record_type_str(rectype::alternate_data) ==
               "Alternate Data" );
    }
    SECTION("Job Identification") {
        CHECK( lis::record_type_str(rectype::job_identification) ==
               "Job Identification" );
    }
    SECTION("Wellsite Data") {
        CHECK( lis::record_type_str(rectype::wellsite_data) ==
               "Wellsite Data" );
    }
    SECTION("Tool String Info") {
        CHECK( lis::record_type_str(rectype::tool_string_info) ==
               "Tool String Info" );
    }
    SECTION("Encrypted Table Dump") {
        CHECK( lis::record_type_str(rectype::enc_table_dump) ==
               "Encrypted Table Dump" );
    }
    SECTION("Table Dump") {
        CHECK( lis::record_type_str(rectype::table_dump) ==
               "Table Dump" );
    }
    SECTION("Data Format Specification") {
        CHECK( lis::record_type_str(rectype::data_format_spec) ==
               "Data Format Specification" );
    }
    SECTION("Data Descriptor") {
        CHECK( lis::record_type_str(rectype::data_descriptor) ==
               "Data Descriptor" );
    }
    SECTION("TU10 Software Boot") {
        CHECK( lis::record_type_str(rectype::tu10_software_boot) ==
               "TU10 Software Boot" );
    }
    SECTION("Bootstrap Loader") {
        CHECK( lis::record_type_str(rectype::bootstrap_loader) ==
               "Bootstrap Loader" );
    }
    SECTION("CP-Kernel Loader Boot") {
        CHECK( lis::record_type_str(rectype::cp_kernel_loader) ==
               "CP-Kernel Loader Boot" );
    }
    SECTION("Program File Header") {
        CHECK( lis::record_type_str(rectype::prog_file_header) ==
               "Program File Header" );
    }
    SECTION("Program Overlay Header") {
        CHECK( lis::record_type_str(rectype::prog_overlay_header) ==
               "Program Overlay Header" );
    }
    SECTION("Program Overlay Load") {
        CHECK( lis::record_type_str(rectype::prog_overlay_load) ==
               "Program Overlay Load" );
    }
    SECTION("File Header") {
        CHECK( lis::record_type_str(rectype::file_header) ==
               "File Header" );
    }
    SECTION("File Trailer") {
        CHECK( lis::record_type_str(rectype::file_trailer) ==
               "File Trailer" );
    }
    SECTION("Tape Header") {
        CHECK( lis::record_type_str(rectype::tape_header) ==
               "Tape Header" );
    }
    SECTION("Tape Trailer") {
        CHECK( lis::record_type_str(rectype::tape_trailer) ==
               "Tape Trailer" );
    }
    SECTION("Reel Header") {
        CHECK( lis::record_type_str(rectype::reel_header) ==
               "Reel Header" );
    }
    SECTION("Reel Trailer") {
        CHECK( lis::record_type_str(rectype::reel_trailer) ==
               "Reel Trailer" );
    }
    SECTION("Logical EOF") {
        CHECK( lis::record_type_str(rectype::logical_eof) ==
               "Logical EOF" );
    }
    SECTION("Logical BOT") {
        CHECK( lis::record_type_str(rectype::logical_bot) ==
               "Logical BOT" );
    }
    SECTION("Logical EOT") {
        CHECK( lis::record_type_str(rectype::logical_eot) ==
               "Logical EOT" );
    }
    SECTION("Logical EOM") {
        CHECK( lis::record_type_str(rectype::logical_eom) ==
               "Logical EOM" );
    }
    SECTION("Operator Command Inputs") {
        CHECK( lis::record_type_str(rectype::op_command_inputs) ==
               "Operator Command Inputs" );
    }
    SECTION("Operator Response Inputs") {
        CHECK( lis::record_type_str(rectype::op_response_inputs) ==
               "Operator Response Inputs" );
    }
    SECTION("System Outputs to Operator") {
        CHECK( lis::record_type_str(rectype::system_outputs) ==
               "System Outputs to Operator" );
    }
    SECTION("FLIC Comment") {
        CHECK( lis::record_type_str(rectype::flic_comment) ==
               "FLIC Comment" );
    }
    SECTION("Blank Record/CSU Comment") {
        CHECK( lis::record_type_str(rectype::blank_record) ==
               "Blank Record/CSU Comment" );
    }
    SECTION("Picture") {
        CHECK( lis::record_type_str(rectype::picture) ==
               "Picture" );
    }
    SECTION("Image") {
        CHECK( lis::record_type_str(rectype::image) ==
               "Image" );
    }
    SECTION("Invalid") {
        CHECK( lis::record_type_str(static_cast< lis::record_type >(2)) ==
               "Invalid LIS79 Record Type" );
    }
}

TEST_CASE("Entry Block", "[protocol]") {
    SECTION("Well-formatted - lis::i8") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x01, // Type
            0x01, // Size
            0x38, // Representation code 56 (lis::i8)
            0x00, // Entry
        };

        const auto entry = lis::read_entry_block( rec, 0 );

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

        const auto entry = lis::read_entry_block( rec, 0 );

        CHECK( lis::decay(entry.type)  == 9  );
        CHECK( lis::decay(entry.size)  == 4  );
        CHECK( lis::decay(entry.reprc) == 65 );

        CHECK( mpark::holds_alternative< lis::string >(entry.value) );
        const auto value = lis::decay( mpark::get< lis::string >(entry.value) );
        CHECK( value == std::string(".1IN") );
    }

    SECTION("Can be read from arbitrary offset") { /* TODO */ }
    SECTION("Too little data to parse entry") { /* TODO */ }

    SECTION("Too little data to parse entry") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x01, // Type
            0x04, // Size
        };

        CHECK_THROWS_WITH(
            lis::read_entry_block(rec, 0),
            Contains("lis::entry_block: "
                     "2 bytes left in record, expected at least 3"));
    }

    SECTION("Too little data to parse entry value") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x01, // Type
            0x04, // Size
            0x49, // Representation code 73 (lis::i32)
            0x00, // Entry
        };

        CHECK_THROWS_WITH(
            lis::read_entry_block(rec, 0),
            Contains("lis::entry_block: "
                     "1 bytes left in record, expected at least 4"));
    }

}

TEST_CASE("Process indicators", "[protocol]") {
    SECTION("Well-formatted process indicators") {
        const auto buffer = std::vector< unsigned char > {
            0xAA, // 0b10101010
            0x55, // 0b01010101
            0xFF, // 0b11111111
            0x03, // 0b00000011
            0x00, // 0b00000000
        };
        lis::mask mask{ std::string{ buffer.begin(), buffer.end() } };

        const auto flags = lis::process_indicators( mask );
        CHECK( flags.original_logging_direction     == 2     );
        CHECK( flags.true_vertical_depth_correction == true  );
        CHECK( flags.data_channel_not_on_depth      == false );
        CHECK( flags.data_channel_is_filtered       == true  );
        CHECK( flags.data_channel_is_calibrated     == false );
        CHECK( flags.computed                       == true  );
        CHECK( flags.derived                        == false );
        CHECK( flags.tool_defined_correction_nb_2   == false );
        CHECK( flags.tool_defined_correction_nb_1   == true  );
        CHECK( flags.mudcake_correction             == false );
        CHECK( flags.lithology_correction           == true  );
        CHECK( flags.inclinometry_correction        == false );
        CHECK( flags.pressure_correction            == true  );
        CHECK( flags.hole_size_correction           == false );
        CHECK( flags.temperature_correction         == true  );
        CHECK( flags.auxiliary_data_flag            == true  );
        CHECK( flags.schlumberger_proprietary       == true  );
    }

    SECTION("Invalid mask size") {
        lis::mask mask{ std::string{"ABCD"} };
        CHECK_THROWS_AS( lis::process_indicators( mask ), std::runtime_error );
    }
}

TEST_CASE("Spec Block", "[protocol]") {
    lis::record rec;
    rec.data = std::vector< char > {
        0x44, 0x45, 0x50, 0x54,                         // "DEPT"
        0x53, 0x4C, 0x42, 0x20, 0x20, 0x20,             // "SLB     " (blank)
        0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x35, 0x34, // "      54"
        0x2E, 0x31, 0x49, 0x4E,                         // ".1IN"
        0x2D, 0x1F, 0x00, 0x0B, // 45;31;00;11 as 4 x uint8 or 757006347 as int32
        0x00, 0x01,                                     // 1
        0x00, 0x08,                                     // size
        0x20, 0x20,                                     // pad-byte
        0x20,                                           // pad-bytes/plevel
        0x02,                                           // nb size
        0x44,                                           // reprc (F32)
        0x20, 0x20, 0x20, 0x20, 0x20,                   // pad-bytes/pindicators
    };

    SECTION("Well-formatted sub-type 0 can be read") {
        const auto spec = lis::read_spec_block0( rec, 0 );

        CHECK( lis::decay(spec.mnemonic)         == std::string("DEPT")     );
        CHECK( lis::decay(spec.service_id)       == std::string("SLB   ")   );
        CHECK( lis::decay(spec.service_order_nr) == std::string("      54") );
        CHECK( lis::decay(spec.units)            == std::string(".1IN")     );
        CHECK( lis::decay(spec.api_log_type)     == 45 );
        CHECK( lis::decay(spec.api_curve_type)   == 31 );
        CHECK( lis::decay(spec.api_curve_class)  == 0  );
        CHECK( lis::decay(spec.api_modifier)     == 11 );
        CHECK( lis::decay(spec.filenr)           == 1  );
        CHECK( lis::decay(spec.reserved_size)    == 8  );
        CHECK( lis::decay(spec.process_level)    == 32 );
        CHECK( lis::decay(spec.samples)          == 2  );
        CHECK( lis::decay(spec.reprc)            == 68 );
    }

    SECTION("Well-formatted sub-type 1 can be read") {
        const auto spec = lis::read_spec_block1( rec, 0 );

        CHECK( lis::decay(spec.mnemonic)           == std::string("DEPT")     );
        CHECK( lis::decay(spec.service_id)         == std::string("SLB   ")   );
        CHECK( lis::decay(spec.service_order_nr)   == std::string("      54") );
        CHECK( lis::decay(spec.units)              == std::string(".1IN")     );
        CHECK( lis::decay(spec.api_codes)          == 757006347 );
        CHECK( lis::decay(spec.filenr)             == 1  );
        CHECK( lis::decay(spec.reserved_size)      == 8  );
        CHECK( lis::decay(spec.samples)            == 2  );
        CHECK( lis::decay(spec.reprc)              == 68 );
        CHECK( lis::decay(spec.process_indicators) == std::string("     ") );
    }

    SECTION("Too little data to parse entry") {
        CHECK_THROWS_WITH(
            lis::read_spec_block1( rec, 10 ),
            Contains("lis::spec_block: "
                     "30 bytes left in record, expected at least 40"));
    }
}

TEST_CASE("Data Format Specification Record", "[protocol]") {
    lis::record rec;
    rec.data = std::vector< char > {
        // Entry Block
        0x00, // Type
        0x01, // Size
        0x41, // Representation code 65 (lis::string)
        0x00, // Entry
        // Spec Block
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

    const auto formatspec = lis::parse_dfsr( rec );

    CHECK( formatspec.entries.size() == 1 );
    CHECK( formatspec.specs.size()   == 1 );

    const auto entry = formatspec.entries.at(0);
    const auto sb    = formatspec.specs.at(0);
    const auto spec  = mpark::get< lis::spec_block0 >(sb);

    CHECK( lis::decay(entry.type)  == 0  );
    CHECK( lis::decay(entry.size)  == 1  );
    CHECK( lis::decay(entry.reprc) == 65 );
    CHECK( lis::decay(spec.mnemonic)         == std::string("DEPT")     );
    CHECK( lis::decay(spec.service_id)       == std::string("SLB   ")   );
    CHECK( lis::decay(spec.service_order_nr) == std::string("      54") );
    CHECK( lis::decay(spec.units)            == std::string(".1IN")     );
}

TEST_CASE("Component Block", "[protocol]") {
    SECTION("Well-formatted - lis::i8") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x45, // type
            0x38, // representation code 56 (lis::i8)
            0x01, // size
            0x03, // category
            0x44, 0x45, 0x50, 0x54, // mnemonic
            0x2E, 0x31, 0x49, 0x4E, // units

            0x04, // Component
        };

        const auto component = lis::read_component_block( rec, 0 );

        CHECK( lis::decay(component.type_nb)  == 69 );
        CHECK( lis::decay(component.reprc)    == 56 );
        CHECK( lis::decay(component.size)     == 1  );
        CHECK( lis::decay(component.category) == 3  );
        CHECK( lis::decay(component.mnemonic) == std::string("DEPT") );
        CHECK( lis::decay(component.units)    == std::string(".1IN") );

        CHECK( mpark::holds_alternative< lis::i8 >(component.component) );
        const auto value = lis::decay( mpark::get< lis::i8 >(component.component) );
        CHECK( value == 4 );
    }

    SECTION("Well-formatted - lis::string") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x45, // type
            0x41, // representation code 65 (lis::string)
            0x02, // size
            0x03, // category
            0x44, 0x45, 0x50, 0x54, // mnemonic
            0x2E, 0x31, 0x49, 0x4E, // units

            0x35, 0x34 // Component
        };

        const auto component = lis::read_component_block( rec, 0 );

        CHECK( lis::decay(component.type_nb)  == 69 );
        CHECK( lis::decay(component.reprc)    == 65 );
        CHECK( lis::decay(component.size)     == 2  );
        CHECK( lis::decay(component.category) == 3  );
        CHECK( lis::decay(component.mnemonic) == std::string("DEPT") );
        CHECK( lis::decay(component.units)    == std::string(".1IN") );

        CHECK( mpark::holds_alternative< lis::string >(component.component) );
        const auto value = lis::decay( mpark::get< lis::string >(component.component) );
        CHECK( value == std::string("54") );
    }

    SECTION("Can be read from arbitrary offset") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x00, // dummy data
            0x45, // type
            0x38, // representation code 56 (lis::i8)
            0x01, // size
            0x03, // category
            0x44, 0x45, 0x50, 0x54, // mnemonic
            0x2E, 0x31, 0x49, 0x4E, // units

            0x04, // Component
        };

        const auto component = lis::read_component_block( rec, 1 );

        CHECK( lis::decay(component.type_nb)  == 69 );
        CHECK( lis::decay(component.reprc)    == 56 );
        CHECK( lis::decay(component.size)     == 1  );
        CHECK( lis::decay(component.category) == 3  );
        CHECK( lis::decay(component.mnemonic) == std::string("DEPT") );
        CHECK( lis::decay(component.units)    == std::string(".1IN") );

        CHECK( mpark::holds_alternative< lis::i8 >(component.component) );
        const auto value = lis::decay( mpark::get< lis::i8 >(component.component) );
        CHECK( value == 4 );
    }

    SECTION("Too little data to parse component") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x45, // type
            0x49, // representation code 73 (lis::i32)
            0x04, // size
        };

        CHECK_THROWS_WITH(
            lis::read_component_block(rec, 0),
            Contains("lis::component_block: "
                     "3 bytes left in record, expected at least 12"));
    }

    SECTION("Too little data to parse component value") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x45, // type
            0x49, // representation code 73 (lis::i32)
            0x04, // size
            0x03, // category
            0x44, 0x45, 0x50, 0x54, // mnemonic
            0x2E, 0x31, 0x49, 0x4E, // units

            0x35, // Component
        };

        CHECK_THROWS_WITH(
            lis::read_component_block(rec, 0),
            Contains("lis::component_block: "
                     "1 bytes left in record, expected at least 4"));
    }

    SECTION("Wrong type") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x02, // type (invalid)
            0x44, // representation code 68 (lis::f32)
            0x04, // size
            0x03, // category
            0x44, 0x45, 0x50, 0x54, // mnemonic
            0x2E, 0x31, 0x49, 0x4E, // units

            0x35, 0x34, 0x35, 0x34 // Component
        };

        CHECK_THROWS_WITH(
            lis::read_component_block(rec, 0),
            Contains("unknown component type 2 in component DEPT"));
    }

    SECTION("Wrong repcode") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x00, // type
            0x00, // representation code 0 (invalid)
            0x04, // size
            0x03, // category
            0x44, 0x45, 0x50, 0x54, // mnemonic
            0x2E, 0x31, 0x49, 0x4E, // units

            0x35, 0x34, 0x35, 0x34 // Component
        };

        CHECK_THROWS_WITH(
            lis::read_component_block(rec, 0),
            Contains("unknown representation code 0 in component DEPT"));
    }

    SECTION("Wrong size") {
        lis::record rec;
        rec.data = std::vector< char > {
            0x00, // type
            0x44, // representation code 68 (lis::f32)
            0x05, // size (invalid)
            0x03, // category
            0x44, 0x45, 0x50, 0x54, // mnemonic
            0x2E, 0x31, 0x49, 0x4E, // units

            0x35, 0x34, 0x35, 0x34 // Component
        };

        CHECK_THROWS_WITH(
            lis::read_component_block(rec, 0),
            Contains("invalid component (mnem: DEPT). "
                     "Expected size for reprc 68 is 4, was 5"));
    }
}

TEST_CASE("Information Record", "[protocol]") {
    lis::record rec;
    rec.data = std::vector< char > {
        0x45, // type
        0x41, // representation code 65 (lis::string)
        0x02, // size
        0x03, // category
        0x44, 0x45, 0x50, 0x54, // mnemonic
        0x2E, 0x31, 0x49, 0x4E, // units
        0x35, 0x34, // Component

        0x45, // type
        0x38, // representation code 56 (lis::i8)
        0x01, // size
        0x03, // category
        0x44, 0x45, 0x50, 0x54, // mnemonic
        0x2E, 0x31, 0x49, 0x4E, // units
        0x04, // Component
    };

    const auto inforec = lis::parse_info_record( rec );
    CHECK( inforec.components.size() == 2 );

    auto component = inforec.components.at(0);
    CHECK( mpark::holds_alternative< lis::string >(component.component) );
    const auto v0 = lis::decay( mpark::get< lis::string >(component.component) );
    CHECK( v0 == std::string("54") );

    component = inforec.components.at(1);
    CHECK( mpark::holds_alternative< lis::i8 >(component.component) );
    const auto v1 = lis::decay( mpark::get< lis::i8 >(component.component) );
    CHECK( v1 == 4 );
}
