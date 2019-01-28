#include <cstdio>
#include <cstring>
#include <sstream>
#include <sstream>
#include <string>

#include <catch2/catch.hpp>

#include <dlisio/dlisio.h>

struct SULv1 {
    int seqnum          = -1;
    int major           = -1;
    int minor           = -1;
    int layout          = -1;
    std::int64_t maxlen = -1;
    char id[ 61 ] = {};

    bool operator==( const SULv1& o ) const {
        std::string sid = this->id;
        return this->seqnum == o.seqnum
            && this->major  == o.major
            && this->minor  == o.minor
            && this->layout == o.layout
            && this->maxlen == o.maxlen
            &&       sid    == o.id
            ;
    }

    bool operator!=( const SULv1& o ) const {
        return !(*this == o);
    }
};

std::ostream& operator<<( std::ostream& stream, const SULv1& x ) {
    return stream << "SULv1 {"
                  << "\n\t.seq = " << x.seqnum
                  << "\n\t.ver = " << x.major << "." << x.minor
                  << "\n\t.lay = " << (x.layout == DLIS_STRUCTURE_RECORD ?
                                       "RECORD" : "UNKNOWN")
                  << "\n\t.len = " << x.maxlen
                  << "\n\t.idt = '" << x.id << "'"
                  << "\n}";

}

std::string blockify( const std::string& xs, int len = 16 ) {
    /*
     * Print the string to disk, formatted like hexdump -c would, except
     * embedded NUL bytes are printed as @
     * Unfortunately, this makes intational @'s indistinguishable from \0, but
     * it should be good enough for now
     */
    int pos = 0;
    std::stringstream ss;

    while( true ) {
        if( pos + len > xs.size() ) {
            ss.write( xs.c_str() + pos, xs.size() - pos );
            ss << "\n";
            return ss.str();
        }

        if( pos + len == xs.size() ) {
            return ss.str();
        }

        std::string line( xs, pos, len );
        for( auto& c : line ) if( c == '\0' ) c = '@';
        ss << "|" << line << "|\n";
        pos += len;
    }
}

SULv1 parse_sulv1( const std::string& sul ) {
    SULv1 v1;
    auto err = dlis_sul( sul.c_str(), &v1.seqnum,
                                      &v1.major,
                                      &v1.minor,
                                      &v1.layout,
                                      &v1.maxlen,
                                      v1.id );
    REQUIRE( err == 0 );
    return v1;
}

TEST_CASE("A simple, well-formatted SULv1", "[sul][v1]") {

    SULv1 ref;
    ref.seqnum = 1;
    ref.major  = 1;
    ref.minor  = 0;
    ref.layout = DLIS_STRUCTURE_RECORD;
    ref.maxlen = 8192;
    std::strcpy( ref.id, "Default Storage Set "
                         "                    "
                         "                    " );

    /*
     * Generate all valid permutations of numbers with paddings and leading
     * zeros and whatnot, that would produce the same record, and create a test
     * case for each of them. Since revision and record only has one valid
     * format (for revision 1.0), they don't change. The storage set identifier
     * is an arbitrary string anyway so there's no wiggle room for two distinct
     * strings that produce the same record
     */

    static const std::string sequence_numbers[] = {
        "   1",
        "  01",
        " 001",
        "0001",
    };

    static const std::string revisions[] = {
        "V1.00",
    };

    static const std::string structures[] = {
        "RECORD",
    };

    static const std::string maxlens[] = {
        " 8192",
        "08192",
    };

    static const std::string identifiers[] = {
        "Default Storage Set "
        "                    "
        "                    ",
    };

    for( const auto& seq : sequence_numbers )
    for( const auto& rev : revisions )
    for( const auto& rec : structures )
    for( const auto& len : maxlens )
    for( const auto& idt : identifiers )
    SECTION("[" + seq + "," + len + "]" ) {
        const auto label = seq + rev + rec + len + idt;
        INFO( "Storage unit label:\n" << blockify( label ) );

        auto v1 = parse_sulv1( label );
        CHECK( v1 == ref );
    }
}

TEST_CASE("A well-formatted SULv1 with undefined maxlen", "[sul][v1]") {
    SULv1 ref;
    ref.seqnum = 1;
    ref.major  = 1;
    ref.minor  = 0;
    ref.layout = DLIS_STRUCTURE_RECORD;
    ref.maxlen = 0;
    std::strcpy( ref.id, "Default Storage Set "
                         "                    "
                         "                    " );

    static const std::string pre = "   1"
                                   "V1.00"
                                   "RECORD";

    static const std::string post = "Default Storage Set "
                                    "                    "
                                    "                    ";

    static const std::string maxlens[] = {
        "    0",
        "   00",
        "  000",
        " 0000",
        "00000",
    };

    for( const auto& len : maxlens )
    SECTION("Explicit zero: '" + len + "'") {
        const auto label = pre + len + post;
        INFO( "Storage unit label:\n" << blockify( label ) );

        auto v1 = parse_sulv1( label );
        CHECK( v1 == ref );
    }

    /*
     * embedded NULL-bytes aren't according to spec, but they're trivially
     * handled by the same code, so check their behaviour
     */
    static const std::string maxlens0[] = {
        { "0\0000", 5 },
        { "00\000", 5 },
        { "000\00", 5 },
        { " 00\0 ", 5 }, // trailing spaces after early \0 is ok
        { "  0\0 ", 5 },
    };

    for( const auto& len : maxlens0 )
    SECTION("Zeros with embedded NUL: '" + std::string( len.c_str() ) + "'") {
        const auto label = pre + len + post;
        INFO( "Storage unit label:\n" << blockify( label ) );

        auto v1 = parse_sulv1( label );
        CHECK( v1 == ref );
    }
}

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

TEST_CASE("pack UVARIs", "[scan]") {
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

    std::int32_t dst[ 8 ];
    const char* fmt = "iiiiiiii";
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

TEST_CASE("pack unsigned integers", "[scan]") {
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
    };

    unsigned char dst[30];
    const char* fmt = "uuUULLiiii";
    const auto err = dlis_packf( fmt, source, dst );

    CHECK( err == DLIS_OK );

    std::uint8_t us[2];
    std::memcpy( us, dst, sizeof( us ) );
    CHECK( us[ 0 ] == 89 );
    CHECK( us[ 1 ] == 167 );

    std::uint16_t un[2];
    std::memcpy( un, dst + 2, sizeof( un ) );
    CHECK( un[ 0 ] == 153 );
    CHECK( un[ 1 ] == 32768 );

    std::uint32_t ul[2];
    std::memcpy( ul, dst + 6, sizeof( ul ) );
    CHECK( ul[ 0 ] == 153 );
    CHECK( ul[ 1 ] == 4294967143 );

    std::int32_t uv[4];
    std::memcpy( uv, dst + 14, sizeof( uv ) );
    CHECK( uv[ 0 ] == 1 );
    CHECK( uv[ 1 ] == 256 );
    CHECK( uv[ 2 ] == 36863 );
    CHECK( uv[ 3 ] == 805355519 );
}

TEST_CASE("pack signed integers", "[scan]") {
    const unsigned char source[] = {
        0x59, // 89 sshort
        0xA7, // -89 sshort
        0x00, 0x99, // 153 snorm
        0xFF, 0x67, // -153 snorm
        0x00, 0x00, 0x00, 0x99, // 153 slong
        0xFF, 0xFF, 0xFF, 0x67, // -153 slong
        0x7F, 0xFF, 0xFF, 0xFF, // ~2.1b slong (int-max)
    };

    unsigned char dst[18];
    const char* fmt = "ddDDlll";
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

TEST_CASE("pack var-size fails with invalid specifier") {
    int vsize;
    CHECK( dlis_pack_varsize( "w",  &vsize ) == DLIS_INVALID_ARGS );
    CHECK( dlis_pack_varsize( "lw", &vsize ) == DLIS_INVALID_ARGS );
    CHECK( dlis_pack_varsize( "wl", &vsize ) == DLIS_INVALID_ARGS );
}

namespace {

bool pack_varsize( const char* fmt ) {
    int vsize;
    CHECK( dlis_pack_varsize( fmt, &vsize ) == DLIS_OK );
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
    CHECK( dlis_pack_size( fmt, &size ) == DLIS_OK );
    return size;
};

}

TEST_CASE("pack size single values") {
    CHECK( packsize( "r" ) == 2 );
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
    CHECK( packsize( "j" ) == 8 );
    CHECK( packsize( "J" ) == 4 );
    CHECK( packsize( "q" ) == 1 );
}
