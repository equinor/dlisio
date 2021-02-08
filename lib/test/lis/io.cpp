#include <vector>
#include <cstdint>
#include <cstring>
#include <ciso646>
#include <stdexcept>

#include <catch2/catch.hpp>

#include <lfp/lfp.h>
#include <lfp/memfile.h>

#include <dlisio/lis/io.hpp>
#include <dlisio/lis/protocol.hpp>
#include <dlisio/exception.hpp>

using namespace Catch::Matchers;
namespace lis = dlisio::lis79;

namespace {

std::FILE* tempfile( const std::vector< unsigned char >& contents ) {
    std::FILE* fp = std::tmpfile();
    std::fwrite(contents.data(), 1, contents.size(), fp);
    std::rewind(fp);
    return fp;
}


std::vector< unsigned char >
wrap_tif( const std::vector< unsigned char >& source) {
    /*
     * Wraps the source data in Tape Image Format:
     *
     * Tapemark type 0
     * source.data()
     * Tapemark type 1
     * Tapemark type 1
     *
     * The next / prev fields of the tapemarks are updated based on the
     * size of source to create a valid TIF file.
     */

    std::size_t size = source.size();

    std::uint32_t type = 0;
    std::uint32_t prev = 0;
    std::uint32_t next = size + 12;

    std::vector< unsigned char > dest(size + 3*12);
    auto* dst = dest.data();

    /* Write first tapemark */
    std::memcpy( dst + 0, &type, sizeof(std::uint32_t) );
    std::memcpy( dst + 4, &prev, sizeof(std::uint32_t) );
    std::memcpy( dst + 8, &next, sizeof(std::uint32_t) );
    #if (defined(IS_BIG_ENDIAN) || \
        (defined(__BYTE_ORDER__) && \
        (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)))
        std::reverse(dst + 0, dst + 4);
        std::reverse(dst + 4, dst + 8);
        std::reverse(dst + 8, dst + 12);
    #endif

    /* Write the source data */
    std::memcpy(dst + 12, source.data(), size);

    /* Write the two EOF tapemarks */
    type = 1;
    next += 12;
    std::memcpy(dst + 12 + size + 0, &type, sizeof(std::uint32_t) );
    std::memcpy(dst + 12 + size + 4, &prev, sizeof(std::uint32_t) );
    std::memcpy(dst + 12 + size + 8, &next, sizeof(std::uint32_t) );

    prev = next;
    next += 12;
    std::memcpy(dst + 24 + size + 0, &type, sizeof(std::uint32_t) );
    std::memcpy(dst + 24 + size + 4, &prev, sizeof(std::uint32_t) );
    std::memcpy(dst + 24 + size + 8, &next, sizeof(std::uint32_t) );

    #if (defined(IS_BIG_ENDIAN) || \
        (defined(__BYTE_ORDER__) && \
        (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)))
        std::reverse(dst + 12 + size + 0, dst + 12 + size + 4);
        std::reverse(dst + 12 + size + 4, dst + 12 + size + 8);
        std::reverse(dst + 12 + size + 8, dst + 12 + size + 12);

        std::reverse(dst + 24 + size + 0, dst + 24 + size + 4);
        std::reverse(dst + 24 + size + 4, dst + 24 + size + 8);
        std::reverse(dst + 24 + size + 8, dst + 24 + size + 12);
    #endif

    return dest;
}

}

TEST_CASE("A PRH can be read", "[iodevice]") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x06, 0x00, 0x00, // prh(len=6, pred=0, succ=0)
        0x84, 0x00,             // lrh(type=132)
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    auto prh = file.read_physical_header();

    CHECK( prh.length == 6 );
    CHECK( not (prh.attributes & lis::prheader::succses) );
    CHECK( not (prh.attributes & lis::prheader::predces) );

    /* The tell is left right after the header */
    CHECK( file.ltell() == 4 );

    file.close();
}

TEST_CASE("A PRH with pred=0 must be at least 6 bytes", "[iodevice]") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x05, 0x00, 0x00, // prh(len=5, pred=0, succ=0)
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    CHECK_THROWS_AS(file.read_physical_header(), std::runtime_error);

    file.close();
}

TEST_CASE("A PRH with pred=1 must be at least 4 bytes", "[iodevice]") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x03, 0x00, 0x02, // prh(len=3, pred=1, succ=0)
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    CHECK_THROWS_AS(file.read_physical_header(), std::runtime_error);

    file.close();
}

TEST_CASE("A PRH can start at uneven tell when no padding", "[iodevice]" ) {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x07, 0x00, 0x00, // prh(len=7, pred=0, succ=0)
        0x01, 0x02, 0x03,
        0x00, 0x06, 0x00, 0x01, // prh(len=6, pred=0, succ=1)
        0x01, 0x02,
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    file.seek(7); // Seek past first PR
    auto prh = file.read_physical_header();

    CHECK( prh.length == 6 );
    CHECK(     (prh.attributes & lis::prheader::succses) );
    CHECK( not (prh.attributes & lis::prheader::predces) );

    /* The tell is left right after the header */
    CHECK( file.ltell() == 11 );

    file.close();
}

TEST_CASE("A PRH can be found when file is padded", "[iodevice]") {
    SECTION("When padbytes == 1") {
        const auto contents = std::vector< unsigned char > {
            0x00, 0x07, 0x00, 0x00, // prh(len=7, pred=0, succ=0)
            0x01, 0x02, 0x03,
            0x00,                   // Padbyte
            0x00, 0x06, 0x00, 0x01, // prh(len=6, pred=0, succ=1)
            0x01, 0x02,
        };
        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );

        file.seek(7); // Seek past first PR
        auto prh = file.read_physical_header();

        CHECK( prh.length == 6 );
        CHECK(     (prh.attributes & lis::prheader::succses) );
        CHECK( not (prh.attributes & lis::prheader::predces) );

        /* The tell is left right after the header */
        CHECK( file.ltell() == 12 );

        file.close();
    }

    SECTION("When padbytes == 2") {
        const auto contents = std::vector< unsigned char > {
            0x00, 0x06, 0x00, 0x00, // prh(len=6, pred=0, succ=0)
            0x01, 0x02,
            0x00, 0x00,             // Padbyte
            0x00, 0x06, 0x00, 0x01, // prh(len=6, pred=0, succ=1)
            0x01, 0x02,
        };
        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );

        file.seek(6); // Seek past first PR
        auto prh = file.read_physical_header();

        CHECK( prh.length == 6 );
        CHECK(     (prh.attributes & lis::prheader::succses) );
        CHECK( not (prh.attributes & lis::prheader::predces) );

        /* The tell is left right after the header */
        CHECK( file.ltell() == 12 );

        file.close();
    }

    SECTION("When padbytes == 3") {
        const auto contents = std::vector< unsigned char > {
            0x00, 0x05, 0x00, 0x00, // prh(len=5, pred=0, succ=0)
            0x01,
            0x00, 0x00, 0x00,       // Padbyte
            0x00, 0x06, 0x00, 0x01, // prh(len=6, pred=0, succ=1)
            0x01, 0x02,
        };
        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );

        file.seek(5); // Seek past first PR
        auto prh = file.read_physical_header();

        CHECK( prh.length == 6 );
        CHECK(     (prh.attributes & lis::prheader::succses) );
        CHECK( not (prh.attributes & lis::prheader::predces) );

        /* The tell is left right after the header */
        CHECK( file.ltell() == 12 );

        file.close();
    }

    SECTION("When padbytes == 4") {
        const auto contents = std::vector< unsigned char > {
            0x00, 0x00, 0x00, 0x00, // Padbyte
            0x00, 0x06, 0x00, 0x01, // prh(len=6, pred=0, succ=1)
            0x01, 0x02,
        };
        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );

        auto prh = file.read_physical_header();

        CHECK( prh.length == 6 );
        CHECK(     (prh.attributes & lis::prheader::succses) );
        CHECK( not (prh.attributes & lis::prheader::predces) );

        /* The tell is left right after the header */
        CHECK( file.ltell() == 8 );

        file.close();
    }

    SECTION("When padbytes > 4") {
        const auto contents = std::vector< unsigned char > {
            0x00, 0x06, 0x00, 0x00, // prh(len=6, pred=0, succ=0)
            0x01, 0x02,
            0x00, 0x00,             // Padbyte
            0x00, 0x00, 0x00, 0x00, // Padbyte
            0x00, 0x06, 0x00, 0x01, // prh(len=6, pred=0, succ=1)
            0x03, 0x04,
        };
        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );

        file.seek(6); // Seek past first PR
        auto prh = file.read_physical_header();

        CHECK( prh.length == 6 );
        CHECK(     (prh.attributes & lis::prheader::succses) );
        CHECK( not (prh.attributes & lis::prheader::predces) );

        /* The tell is left right after the header */
        CHECK( file.ltell() == 16 );

        file.close();
    }
}

TEST_CASE("Padbytes after last PR is considered EOF", "[iodevice]") {
    SECTION("When n-padbytes < 4") {
        const auto contents = std::vector< unsigned char > {
            0x20, 0x20, 0x20, //padbytes
        };

        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );

        CHECK_THROWS_AS(file.read_physical_header(), dlisio::eof_error);
        file.close();
    }

    SECTION("When n-padbytes == 4") {
        const auto contents = std::vector< unsigned char > {
            0x20, 0x20, 0x20, 0x20 //padbytes
        };

        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );

        CHECK_THROWS_AS(file.read_physical_header(), dlisio::eof_error);
        file.close();
    }

    SECTION("When n-padbytes > 4") {
        const auto contents = std::vector< unsigned char > {
            0x20, 0x20, 0x20, 0x20,
            0x20, 0x20, //padbytes
        };

        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );

        CHECK_THROWS_AS(file.read_physical_header(), dlisio::eof_error);
        file.close();
    }
}

TEST_CASE("A LRH can be read", "[iodevice]") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x06, 0x00, 0x00, // prh(len=6, pred=0, succ=0)
        0x84, 0x00,             // lrh(type=132)
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    file.read_physical_header();
    auto lrh = file.read_logical_header();
    CHECK( lis::decay( lrh.type ) == 132 );

    /* The tell is left right after the header */
    CHECK( file.ltell() == 6 );

    file.close();
}

TEST_CASE("A LRH with invalid type", "[iodevice]") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x03, 0x00,             // lrh(type=03)
        0x01, 0x02,             // dummy data
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    SECTION("A LRH with invalid type can be read") {
        file.seek(4);
        auto lrh = file.read_logical_header();
        CHECK( lis::decay( lrh.type ) == 3 );
    }

    SECTION("A record with invalid type cannot be indexed") {
        CHECK_THROWS_AS( file.index_record(), std::runtime_error );
    }

    file.close();
}

TEST_CASE("A record spanning one PR can be indexed and read", "[iodevice]") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x84, 0x00,             // lrh(type=132)
        0x01, 0x02,             // dummy data
    };

    const auto expected = std::vector< char > {
        0x01, 0x02,
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    auto index = file.index_records();
    auto info = index.explicits()[0];

    const auto type = static_cast< lis::record_type >(lis::decay(info.type));
    CHECK( info.ltell      == 0 );
    CHECK( info.size       == 8 );
    CHECK( type            == lis::record_type::reel_header );
    CHECK( info.consistent == true );

    /* The tell is left right after the header */
    CHECK( file.ltell() == 8 );

    auto rec = file.read_record( info );
    CHECK_THAT( rec.data, Equals(expected) );

    file.close();
}

TEST_CASE("A record spanning two PRs can be indexed and read", "[iodevice]") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x08, 0x00, 0x01, // prh(len=8, pred=0, succ=1)
        0x84, 0x00,             // lrh(type=132)
        0x01, 0x02,             // dummy data

        0x00, 0x08, 0x00, 0x02, // prh(len=8, pred=1, succ=0)
        0x03, 0x04, 0x05, 0x06  // dummy data
    };

    const auto expected = std::vector< char > {
        0x01, 0x02, 0x03, 0x04, 0x05, 0x06
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    auto index = file.index_records();
    auto explicits = index.explicits();

    CHECK( explicits.size() == 1 );
    CHECK( index.size()     == 1 ); // Total record count equals explicit count

    auto info = explicits[0];
    const auto type = static_cast< lis::record_type >(lis::decay(info.type));
    CHECK( info.ltell == 0 );
    CHECK( info.size  == 16 );
    CHECK( type == lis::record_type::reel_header );
    CHECK( info.consistent == true );

    /* The tell is left right after the header */
    CHECK( file.ltell() == 16 );

    auto rec = file.read_record( info );
    CHECK_THAT( rec.data, Equals(expected) );

    file.close();
}

TEST_CASE("A record spanning three PRs can be indexed and read", "[iodevice]") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x08, 0x00, 0x01, // prh(len=8, pred=0, succ=1)
        0x84, 0x00,             // lrh(type=132)
        0x01, 0x02,             // dummy data

        0x00, 0x08, 0x00, 0x03, // prh(len=8, pred=1, succ=1)
        0x03, 0x04, 0x05, 0x06, // dummy data

        0x00, 0x07, 0x00, 0x02, // prh(len=7, pred=1, succ=0)
        0x07, 0x08, 0x09        // dummy data
    };

    const auto expected = std::vector< char > {
        0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    auto index = file.index_records();
    auto explicits = index.explicits();

    CHECK( explicits.size() == 1 );
    CHECK( index.size()     == 1 ); // Total record count equals explicit count

    auto info = explicits[0];
    const auto type = static_cast< lis::record_type >(lis::decay(info.type));
    CHECK( info.ltell  == 0 );
    CHECK( info.size   == 23 );
    CHECK( type == lis::record_type::reel_header );
    CHECK( info.consistent == true );

    /* The tell is left right after the header */
    CHECK( file.ltell() == 23 );

    auto rec = file.read_record( info );
    CHECK_THAT( rec.data, Equals(expected) );

    file.close();
}

TEST_CASE("Padding after last PRH is considered a valid EOF") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x84, 0x00,             // lrh(type=132)
        0x01, 0x02,             // dummy data

        0x00, 0x00, 0x00, 0x00  // Padding
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    SECTION("Trying to read padbytes result in eof_error") {
        file.seek(8);
        CHECK_THROWS_AS(file.read_physical_header(), dlisio::eof_error);
    }

    SECTION("File is not considered truncated") {
        const auto index = file.index_records();

        CHECK( index.size() == 1 );
        CHECK( file.truncated() == false );
    }

    SECTION("N-padbytes < PRH size"){
        file.seek(10);
        CHECK_THROWS_AS(file.read_physical_header(), dlisio::eof_error);
    }

    file.close();

}

TEST_CASE("Padbytes can be identified and skipped") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x84, 0x00,             // lrh(type=132)
        0x01, 0x02,             // dummy data

        0x00, 0x00, 0x00, 0x00, // Padding

        0x00, 0x07, 0x00, 0x00, // prh(len=7, pred=0, succ=0)
        0x82, 0x00,             // lrh(type=130)
        0x03,                   // dummy data
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    SECTION("PRH is found and read correctly") {
        file.seek(8);
        const auto prh = file.read_physical_header();

        CHECK( prh.length == 7 );
    }

    SECTION(" A record after padbytes is indexed correctly") {
        file.seek(8);
        const auto info = file.index_record();

        const auto type = static_cast< lis::record_type >(lis::decay(info.type));
        CHECK( info.ltell == 12 );
        CHECK( info.size  ==  7 );
        CHECK( type == lis::record_type::tape_header );
    }

    SECTION("PR after padding is included in the index") {
        const auto index = file.index_records();

        CHECK( index.size() == 2 );
        CHECK( file.truncated() == false );
    }

    file.close();

}

TEST_CASE("Inconsistent PR headers") {
    SECTION("PRH1(succ=0), PRH2(pred=1)") {}

    SECTION("PRH1(succ=1), PRH2(pred=0)") {}
}

TEST_CASE("Implicit records are stored seperatly from explicits/fixed") {
}

TEST_CASE("Size of the indexed file") {
    const auto contents = std::vector< unsigned char > {
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x40, 0x00,             // lrh(type=64) DFSR
        0x01, 0x02,             // dummy data

        0x00, 0x07, 0x00, 0x00, // prh(len=7, pred=0, succ=0)
        0x40, 0x00,             // lrh(type=64) DFSR
        0x01,                   // dummy data
    };

    SECTION("Size of file is correct after indexing") {
        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );
        auto index = file.index_records();

        CHECK( index.size() == 2 );
        CHECK( file.psize() == 15 );

        file.close();
    }

    SECTION("Size of file is correct after indexing - TIF") {
        auto* cfile = lfp_cfile( tempfile( wrap_tif( contents ) ) );
        auto* tif = lfp_tapeimage_open( cfile );
        auto file = lis::iodevice( tif );
        auto index = file.index_records();

        CHECK( index.size() == 2 );
        CHECK( file.psize() == 15 + 2*12 );

        file.close();
    }

    SECTION("A un-indexed file does not have a size") {
        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );

        CHECK_THROWS_AS(file.psize(), std::runtime_error);
        CHECK_THROWS_AS(file.truncated(), std::runtime_error);

        file.close();
    }

    SECTION("Padding at after last PR is not considered as truncation") {
        const auto contents = std::vector< unsigned char > {
            0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
            0x40, 0x00,             // lrh(type=64) DFSR
            0x01, 0x02,             // dummy data

            0x00, 0x00,             // padding
        };

        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );
        auto index = file.index_records();

        CHECK( not file.truncated() );

        CHECK( index.size() == 1 );
        CHECK( file.psize() == 10 );

        file.close();
    }

    SECTION("A truncated file cannot report a valid size") {
        const auto contents = std::vector< unsigned char > {
            0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
            0x40, 0x00,             // lrh(type=64) DFSR
            0x01, 0x02,             // dummy data

            0x00, 0x05,             // truncated
        };

        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto file = lis::iodevice( cfile );
        auto index = file.index_records();

        CHECK( file.truncated() );
        CHECK_THROWS_AS(file.psize(), std::runtime_error);

        file.close();
    }

    SECTION("A new file can be opened from previous offset + size") {
        const auto contents = std::vector< unsigned char > {
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x18, 0x00, 0x00, 0x00, // tm(type=0,prev=0,next=24)

            0x00, 0x06, 0x00, 0x00, // prh(len=6, pred=0, succ=0)
            0x84, 0x00,             // lrh(type=132)

            0x00, 0x06, 0x00, 0x00, // prh(len=6, pred=0, succ=0)
            0x82, 0x00,             // lrh(type=130)

            0x01, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x24, 0x00, 0x00, 0x00, // tm(type=1,prev=0,next=36)

            0x00, 0x00, 0x00, 0x00,
            0x18, 0x00, 0x00, 0x00,
            0x36, 0x00, 0x00, 0x00, // tm(type=0,prev=24,next=72)

            0x00, 0x06, 0x00, 0x00, // prh(len=6, pred=0, succ=0)
            0x80, 0x00,             // lrh(type=128)

            0x01, 0x00, 0x00, 0x00,
            0x24, 0x00, 0x00, 0x00,
            0x42, 0x00, 0x00, 0x00, // tm(type=1,prev=0,next=24)
        };

        auto* cfile = lfp_cfile( tempfile( contents ) );
        auto* tif   = lfp_tapeimage_open( cfile );
        auto file1 = lis::iodevice( tif );
        auto index1 = file1.index_records();

        CHECK( index1.size()   == 2 );
        CHECK( file1.poffset() == 0 );
        CHECK( file1.psize()   == 12 + 12 + 12); // TM + data + TM

        auto prev_offset = file1.poffset();
        auto prev_size   = file1.psize();

        auto* cfile2 = lfp_cfile( tempfile( contents ) );
        lfp_seek( cfile2, file1.poffset() + file1.psize() );

        auto file2 = lis::iodevice( lfp_tapeimage_open( cfile2 ) );
        auto index2 = file2.index_records();

        CHECK( index2.size()   == 1 );
        CHECK( file2.poffset() == prev_offset + prev_size );
        CHECK( file2.psize()   == 12 + 6 + 12 ); // TM + data + TM

        file1.close();
        file2.close();
    }
}

TEST_CASE("Implicits are partitioned correctly by their DFSR") {

    const auto contents = std::vector< unsigned char > {
        /* DFSR no 1 - No assosiated implicit records */
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x40, 0x00,             // lrh(type=64) DFSR
        0x01, 0x02,             // dummy data
        /* DFSR no 2 */
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x40, 0x00,             // lrh(type=64) DFSR
        0x03, 0x04,             // dummy data
        /* Implicit record no 1 - described by DFSR no 2 */
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x00, 0x00,             // lrh(type=0) normal data record
        0x05, 0x06,             // dummy data
        /* Implicit record no 2 - described by  with DFSR no 2 */
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x00, 0x00,             // lrh(type=0) normal data record
        0x07, 0x08,             // dummy data
        /* DFSR no 3 */
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x40, 0x00,             // lrh(type=64) DFSR
        0x09, 0x0A,             // dummy data
        /* Implicit record no 3 - described by DFSR no 3 */
        0x00, 0x08, 0x00, 0x00, // prh(len=8, pred=0, succ=0)
        0x00, 0x00,             // lrh(type=0) normal data record
        0x0B, 0x0C,             // dummy data
    };

    auto* cfile = lfp_cfile( tempfile( contents ) );
    auto file = lis::iodevice( cfile );

    auto index = file.index_records();
    auto explicits = index.explicits();

    SECTION("No implicits are found for a DFSR where next record is also DFSR") {
        auto dfsr = explicits[0];
        const auto type = static_cast< lis::record_type >(lis::decay(dfsr.type));
        CHECK( dfsr.ltell == 0 );
        CHECK( type == lis::record_type::data_format_spec );

        auto im = index.implicits_of(dfsr);
        CHECK(im.begin() == im.end());
    }

    SECTION("All implicits for a DFSR (not last DFSR in file) are found") {
        const auto expected = std::vector< std::vector< char > > {
            { 0x05, 0x06 },
            { 0x07, 0x08 }
        };

        auto dfsr = explicits[1];
        const auto type = static_cast< lis::record_type >(lis::decay(dfsr.type));
        CHECK( dfsr.ltell == 8 );
        CHECK( type == lis::record_type::data_format_spec );

        auto implicits = index.implicits_of(dfsr);
        auto beg = implicits.begin();
        auto end = implicits.end();

        CHECK( std::distance(beg, end) == 2 );
        CHECK( beg->ltell == 16 );
        CHECK( std::next( beg )->ltell == 24 );

        int idx = 0;
        for ( const auto& info : implicits ) {
            auto record = file.read_record(info);

            CHECK_THAT( record.data, Equals(expected[idx]) );
            idx++;
        }
    }

    SECTION("All implicits for a DFSR (last DFSR in file) are found") {
        const auto expected = std::vector< char > {
            0x0B, 0x0C
        };

        auto dfsr = explicits[2];
        const auto type = static_cast< lis::record_type >(lis::decay(dfsr.type));
        CHECK( dfsr.ltell == 32 );
        CHECK( type == lis::record_type::data_format_spec );

        auto implicits = index.implicits_of(dfsr);
        auto beg = implicits.begin();
        auto end = implicits.end();

        CHECK( std::distance(beg, end) == 1 );
        CHECK( beg->ltell == 40 );

        for ( const auto& info : implicits ) {
            auto record = file.read_record(info);
            CHECK_THAT( record.data, Equals(expected) );
        }
    }

    file.close();
}

