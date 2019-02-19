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

void check_pack_varsize(const char* fmt, bool is_varsize)
{
    int varsize;
    const auto err = dlis_pack_varsize(fmt, &varsize);
    CHECK( err == DLIS_OK );
    if(is_varsize)
    {
        CHECK( varsize == 1 );
    }else
    {
        CHECK( varsize == 0 );
    }
}

void check_packsize_ok(const char* fmt, int expected_size)
{
    check_pack_varsize(fmt, false);
    int size;
    const auto err = dlis_pack_size( fmt, &size );
    CHECK( err == DLIS_OK );
    CHECK( size == expected_size );
}

void check_packsize_inconsistent(const char* fmt)
{
    check_pack_varsize(fmt, true);
    int size;
    const auto err = dlis_pack_size( fmt, &size );
    CHECK( err == DLIS_INCONSISTENT );
}

void check_packsize_invalid_arguments(const char* fmt)
{
    int varsize;
    auto err = dlis_pack_varsize(fmt, &varsize);
    CHECK( err == DLIS_INVALID_ARGS );

    int size;
    err = dlis_pack_size( fmt, &size );
    CHECK( err == DLIS_INVALID_ARGS );
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

static const unsigned char plain16 [] = {
        0x00, 0x18, /* VRL.len */
        0xFF,       /* VRL.padding */
        0x01,       /* VRL.version */
        0x00, 0x14, /* seg.len */
        0x80,       /* seg.attr: explicit */
        0x00,       /* seg.type */

        /* 16 bytes body */
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,

        /* no trailer */
};

static const int plain16_size = sizeof(plain16);

TEST_CASE("single visible record", "[envelope]") {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
    const char* next;
    int initial_residual = 0;
    const auto err = dlis_index_records( (char*)plain16,
                                         (char*)plain16 + plain16_size,
                                         1,
                                         &initial_residual,
                                         &next,
                                         &count,
                                         tells,
                                         residuals,
                                         explicits );
    CHECK( err == DLIS_OK );
    CHECK( count == 1 );
    CHECK( tells[0] == -plain16_size );
    CHECK( explicits[0] );
    CHECK( residuals[0] == 0 );
}

struct two_records {
    two_records() {
        begin = file;
        end = std::copy( plain16, plain16 + plain16_size, begin );
        end = std::copy( plain16, plain16 + plain16_size, end );
    }

    char* begin;
    char* end;
    char file[2 * plain16_size];
    int initial_residual = 0;
};

static const unsigned char multisegment16[] = {
    0x00, 0x2C, /* VRL.len */
    0xFF,       /* VRL.padding */
    0x01,       /* VRL.version */

    /* first header */
    0x00, 0x14, /* seg.len */
    0xa0,       /* seg.attr: explicit | succ */
    0x00,       /* seg.type */

    /* 16 bytes body */
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    /* no trailer */

    /* second header */
    0x00, 0x14, /* seg.len */
    0x80,       /* seg.attr: explicit */
    0x00,       /* seg.type */

    /* 16 bytes body */
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
};

struct multi_segment_record {
    multi_segment_record() {
        begin = file;
        end = std::copy( multisegment16,
                         multisegment16 + sizeof(multisegment16),
                         begin );
    }

    char* begin;
    char* end;
    char file[sizeof(multisegment16)];
    int initial_residual = 0;
};

TEST_CASE_METHOD( two_records,
                  "two visible records, sufficient allocsize",
                  "[envelope]") {

    int count = 0;
    long long tells[2];
    int explicits[2];
    int residuals[2];
    const char* next = nullptr;
    const auto err = dlis_index_records( begin,
                                         end,
                                         2,
                                         &initial_residual,
                                         &next,
                                         &count,
                                         tells,
                                         residuals,
                                         explicits );
    CHECK( err == DLIS_OK );
    CHECK( next == end );
    CHECK( count == 2 );

    CHECK( tells[0] == std::distance(end, begin) );
    CHECK( explicits[0] );
    CHECK( residuals[0] == 0 );

    CHECK( tells[1] == std::distance(end, begin + plain16_size) );
    CHECK( explicits[1] );
    CHECK( residuals[1] == 0 );
}

TEST_CASE_METHOD( two_records,
                  "two vanilla records visible, insufficient alloc",
                  "[envelope]") {

    /* make first record implicitly formatted */
    /* LRSH attribute field is 6 bytes in */
    file[6] = 0;

    int count = 0;
    long long tells[2];
    int explicits[2];
    int residuals[2];
    const char* next = nullptr;
    int err;
    err = dlis_index_records( begin,
                              end,
                              1,
                              &initial_residual,
                              &next,
                              &count,
                              tells,
                              residuals,
                              explicits );
    CHECK( err == DLIS_OK );
    CHECK( count == 1 );
    CHECK( tells[0] == std::distance(end, begin) );
    CHECK( !explicits[0] );
    CHECK( residuals[0] == 0 );
    CHECK( next - begin == plain16_size );

    err = dlis_index_records( next,
                              end,
                              1,
                              &initial_residual,
                              &next,
                              &count,
                              count + tells,
                              count + residuals,
                              count + explicits );

    CHECK( err == DLIS_OK );
    CHECK( next == end );
    CHECK( count == 2 );
    CHECK( tells[1] == std::distance(end, begin + plain16_size) );
    CHECK( explicits[1] );
    CHECK( residuals[1] == 0 );
}

TEST_CASE("truncated visible record", "[envelope]") {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
    const char* next;
    int initial_residual = 0;
    const auto err = dlis_index_records( (char*)plain16,
                                         (char*)plain16 + plain16_size / 2,
                                         1,
                                         &initial_residual,
                                         &next,
                                         &count,
                                         tells,
                                         residuals,
                                         explicits );
    CHECK( err == DLIS_TRUNCATED );
}

TEST_CASE_METHOD( two_records,
                  "two visible records, second truncated",
                  "[envelope]") {
    int count = 0;
    long long tells[2];
    int explicits[2];
    int residuals[2];
    const char* next = nullptr;
    int err;


    auto trunc_end = begin + plain16_size + plain16_size/2;
    err = dlis_index_records( begin,
                              trunc_end,
                              2,
                              &initial_residual,
                              &next,
                              &count,
                              tells,
                              residuals,
                              explicits );
    CHECK( err == DLIS_TRUNCATED );
    CHECK( count == 1 );
    CHECK( tells[0] == std::distance(trunc_end, begin) );
    CHECK( explicits[0] );
    CHECK( residuals[0] == 0 );
    CHECK( next - begin == plain16_size );

    err = dlis_index_records( next,
                              end,
                              1,
                              &initial_residual,
                              &next,
                              &count,
                              count + tells,
                              count + residuals,
                              count + explicits );

    CHECK( err == DLIS_OK );
    CHECK( next == end );
    CHECK( count == 2 );
    CHECK( tells[1] == std::distance(end, begin + plain16_size) );
    CHECK( explicits[1] );
    CHECK( residuals[1] == 0 );
}

TEST_CASE_METHOD( multi_segment_record,
                  "valid, multi-segment record"
                  "[envelope]" ) {
    int count = 0;
    long long tells[2];
    int explicits[2];
    int residuals[2];
    const char* next = nullptr;
    int err;
    err = dlis_index_records( begin,
                              end,
                              2,
                              &initial_residual,
                              &next,
                              &count,
                              tells,
                              residuals,
                              explicits );

    CHECK( err == DLIS_OK );
    CHECK( next == end );

    CHECK( count == 1 );
    CHECK( tells[0] == std::distance(end, begin) );
    CHECK( residuals[0] == 0 );
    CHECK( explicits );
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

TEST_CASE("pack UVARIs and ORIGINs", "[scan]") {
    const int test_len = 8;
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

    const char* fmt = "iJiJiJiJ";
    check_packsize_ok(fmt, 4 * test_len);

    std::int32_t dst[ test_len ];
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
        0xC0, 0x00, 0x40, 0x00, // 16384 uvari (first with 4 bytes)
        0xBF, 0xFF, //16383 uvari (last with 2 bytes)
        0x80, 0x80, //128 uvari (first with 2 bytes)
        0x7F, //127 uvari (last with 1 byte)
        0x80, 0x01, //1 uvari (on 2 bytes)
    };

    const int expected_size = (1 * 2) + (2 * 2) + (4 * 2) + (4 * 9);
    unsigned char dst[expected_size];
    const char* fmt = "uuUULLiiiiiiiii";

    check_packsize_ok(fmt, expected_size);

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

    std::int32_t uv[9];
    std::memcpy( uv, dst + 14, sizeof( uv ) );
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

    const int expected_size = (1 * 2) + (2 * 2) + (4 * 3);
    unsigned char dst[expected_size];
    const char* fmt = "ddDDlll";

    check_packsize_ok(fmt, expected_size);

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

TEST_CASE("pack floats", "[scan]") {
    const int test_len = 8;
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

    const int expected_size = (test_len * 4);
    const char* fmt = "rrffxxVV";

    check_packsize_ok(fmt, expected_size);

    float dst[test_len];
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

TEST_CASE("pack statistical", "[scan]") {
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


    const char* fmt = "bBzZ";
    const int expected_size = 4 * 2 + 4 * 3 + 8 * 2 + 8 * 3;
    check_packsize_ok(fmt, expected_size);

    unsigned char dst[expected_size];
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

TEST_CASE("pack doubles", "[scan]") {
    const int test_len = 2;
    const unsigned char source[] = {
        0x3F, 0xD0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,// 0.25 fdouble
        0xC2, 0xF3, 0x78, 0x5F, 0x66, 0x30, 0x1C, 0x0A,// -342523480572352.625 fdouble
    };

    const int expected_size = (test_len * 8);
    const char* fmt = "FF";

    check_packsize_ok(fmt, expected_size);

    double dst[test_len];
    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    CHECK( dst[ 0 ] == 0.25 );
    CHECK( dst[ 1 ] == -342523480572352.625 );
}

TEST_CASE("pack complex", "[scan]") {
    const unsigned char source[] = {
        0x41, 0x2C, 0x00, 0x00, //10.75 csingl R
        0xC1, 0x10, 0x00, 0x00, //-9 csing1 I
        0x40, 0x3C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, //28 cdoubl R
        0x40, 0x42, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, //36.5 cdoub1 I
    };

    const char* fmt = "cC";
    const int expected_size = 4 * 2 + 8 * 2;
    check_packsize_ok(fmt, expected_size);

    unsigned char dst[expected_size];
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


TEST_CASE("pack datetime", "[scan]") {
    const int test_len = 2;
    const unsigned char source[] = {
        0xFF, 0x2C, 0x1F, 0x00, 0x20, 0x10, 0x00, 0x00, //255Y 2TZ 12M 31D 0H 32MN 16S 0MS
        0x00, 0x01, 0x01, 0x17, 0x3B, 0x00, 0x03, 0xE7, //0Y 0TZ 1M 1D 23H 59M 0S 999MS
    };


    const int expected_size = (test_len * 32);
    const char* fmt = "jj";

    check_packsize_ok(fmt, expected_size);

    unsigned char dst[expected_size];
    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    int expected[test_len][8] = {
        {255, 2, 12, 31, 0, 32, 16, 0},
        {0, 0, 1, 1, 23, 59, 0, 999},
    };

    for (int i = 0; i < test_len; ++i)
    {
        int dt[8];
        std::memcpy( dt, dst + 32 * i, sizeof( dt ) );
        for (int j = 0; j < 8; ++j)
        {
            CHECK( dt[ j ] == expected[i][j] );
        }
    }
}


TEST_CASE("pack status", "[scan]") {
    const unsigned char source[] = {
        0x00, // 0 status
        0x01, // 1 status
    };

    const int expected_size = 2;
    unsigned char dst[expected_size];
    const char* fmt = "qq";
    check_packsize_ok(fmt, expected_size);

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    std::uint8_t st[expected_size];
    std::memcpy( st, dst, sizeof( st ) );
    CHECK( st[ 0 ] == 0 );
    CHECK( st[ 1 ] == 1 );
}


void read_int32(unsigned char dst[], int* dst_index, int expected_value)
{
    std::int32_t value;
    std::memcpy( &value, dst + *dst_index, sizeof(std::int32_t));
    CHECK( value == expected_value );
    *dst_index += sizeof(std::int32_t);
}

void read_int8(unsigned char dst[], int* dst_index, int expected_value)
{
    std::uint8_t value = dst[*dst_index];
    CHECK( value == expected_value);
    *dst_index += sizeof(std::uint8_t);
}

void read_varstring(unsigned char dst[], int* dst_index,
    std::string::size_type expected_length, std::string expected_text)
{
    read_int32(dst, dst_index, expected_length);

    char text[expected_length];
    std::memcpy(text, dst + *dst_index, expected_length);
    if (expected_text.length() != expected_length)
    {
        //V1 doesn't require special treatment of null character
        CHECK( strncmp(text, expected_text.c_str(), expected_length) == 0);
    }else{
        CHECK( std::string (text, expected_length) == expected_text );
    }
    *dst_index += expected_length;
}



TEST_CASE("pack ident & ascii & unit", "[scan]") {
    const int test_data_len = 9;
    const unsigned char source[] = {
        0x04, 0x54, 0x45, 0x53, 0x54,//"TEST" ident
        0x05, 0x54, 0x59, 0x50, 0x45, 0x31,//"TYPE1" ident
        0x05, 0x54, 0x45, 0x53, 0x54, 0x54,//"TESTT" ident
        0x03, 0x41, 0x42, 0x43, //"ABC" ident
        0x00, //empty ident
        0xE, 0x54, 0x45, 0x53, 0x54, 0x54, 0x45, 0x53, 0x54,
             0x54, 0x45, 0x53, 0x54, 0x54, 0x45, //"TESTTESTTESTTE" ident
        0x03, 0x41, 0x0A, 0x62, //A <linefeed> b ascii
        0x80, 0x04, 0x5C, 0x00, 0x7E, 0x00, // \<NULL character>~<NULL character> ascii
        //0x05, 0x24, 0x20, 0x2F, 0x20, 0xA3 //`$ / £' V2 ascii. Invalid for V1
        0xD,
        0x55, 0x20, 0x2D, 0x20, 0x75, 0x6E, 0x69, 0x74, 0x20, 0x28, 0x2F, 0x33, 0x29//U - unit (/3)
    };

    const char* fmt = "ssssssSSQ";
    check_packsize_inconsistent(fmt);

    const int expected_size = 4 * test_data_len + (4 + 5 + 5 + 3 + 0 + 14) + (3 + 4) + (13);
    unsigned char dst[expected_size];
    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    struct varstr
    {
        std::string::size_type exp_length;
        std::string exp_text;
    };

    struct varstr test_data[test_data_len] =
    {
        {4, "TEST"},
        {5, "TYPE1"},
        {5, "TESTT"},
        {3, "ABC"},
        {0, ""},
        {14, "TESTTESTTESTTE"},
        {3, "A\nb"},
        {4, "\\\0~\0"},
        //{5, "$ / £"}, //test is invalid for V1, valid for V2 only
        {13, "U - unit (/3)"},
    };

    struct varstr* test_data_ptr = test_data;

    int dst_index = 0;
    for (int i=0; i<test_data_len; i++, test_data_ptr++ )
    {
        read_varstring(dst, &dst_index, test_data_ptr->exp_length, test_data_ptr->exp_text);
    }

    CHECK( expected_size == dst_index );
}

TEST_CASE("pack long ascii ", "[scan]") { //failing one
    //const int str_len = 301;
    //unsigned char len_bytes[4] = {0xC0, 0x00, 0x01, 0x2D}; //301

    const int str_len = 243;
    unsigned char len_bytes[4] = {0xC0, 0x00, 0x00, 0xF3}; //243

    const std::string test_str =
    //"Lorem ipsum dolor sit amet, consectetuer adipiscing elit. " //58
    "Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque " //67
    "penatibus et magnis dis parturient montes, nascetur ridiculus mus. " //67
    "Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. "//69
    "Nulla consequat massa quis enim. Doneca.";//40

    CHECK( test_str.length() == str_len);

    unsigned char src[str_len + 4];
    std::memcpy( src, len_bytes, 4 );
    std::memcpy( src + 4, test_str.c_str(), str_len);

    const char* fmt = "S";
    check_packsize_inconsistent(fmt);
    unsigned char dst[str_len + 4];
    const auto err = dlis_packf( fmt, src, dst );
    CHECK( err == DLIS_OK );

    int dst_index = 0;
    int length = dst[dst_index];
    CHECK( length == str_len );
    dst_index += 4;

    CHECK( std::string( &dst[dst_index], &dst[dst_index + length] ) == test_str );
}


TEST_CASE("pack obname", "[scan]") {
    const unsigned char source[] = {
        0x81, 0x3A, 0xFF, //"314 O 255 C
              0x0C, 0x44, 0x4C, 0x49, 0x53, 0x49, 0x4F,
                   0x44, 0x4C, 0x49, 0x53, 0x49, 0x4F,//DLISIODLISIO I obname
        0x04, 0x0F, 0x02, 0x44, 0x4C//"4 O 15 C DL I obname
    };

    int expected_length = (4 + 1 + 16) + (4 + 1 + 6);
    unsigned char dst[expected_length];
    const char* fmt = "oo";
    check_packsize_inconsistent(fmt);

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    int dst_index = 0;
    read_int32(dst, &dst_index, 314);
    read_int8(dst, &dst_index, 255);
    read_varstring(dst, &dst_index, 12, std::string("DLISIODLISIO"));

    read_int32(dst, &dst_index, 4);
    read_int8(dst, &dst_index, 15);
    read_varstring(dst, &dst_index, 2, std::string("DL"));

    CHECK( expected_length == dst_index );
}



TEST_CASE("pack objref", "[scan]") {
    const unsigned char source[] = {
    0x07, 0x4C, 0x49, 0x42, 0x52, 0x41, 0x52, 0x59, //LIBRARY T
          0x01, 0x00, 0x08,//1 NO 0 NC 8 LEN NI
          0x50, 0x52, 0x4F, 0x54, 0x4F, 0x43, 0x4F, 0x4C, ////PROTOCOL NI obref


    };

    int expected_length = (4 + 7 + 4 + 1 + 4 + 8);
    unsigned char dst[expected_length];
    const char* fmt = "O";
    check_packsize_inconsistent(fmt);

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    int dst_index = 0;
    read_varstring(dst, &dst_index, 7, std::string("LIBRARY"));
    read_int32(dst, &dst_index, 1);
    read_int8(dst, &dst_index, 0);
    read_varstring(dst, &dst_index, 8, std::string("PROTOCOL"));

    CHECK( expected_length == dst_index );
}


TEST_CASE("pack attref", "[scan]") {
    const unsigned char source[] = {
    0x0A, 0x4C, 0x4F, 0x52, 0x45, 0x4D, 0x49, 0x50, 0x53, 0x55, 0x4D, //LOREMIPSUM T
          0xC0, 0x00, 0x00, 0x0A, 0x45, 0x0C,//10 (4 bytes) NO 69 NC 12 LEN NI
          0x44, 0x4F, 0x4C, 0x4F, 0x52, 0x53, 0x49, 0x54, 0x41, 0x4D, 0x45, 0x54, //DOLORSITAMET NI obref
    0x0D, 0x43, 0x4F, 0x4E, 0x53, 0x45, 0x43, 0x54, 0x45, 0x54, 0x55, 0x45, 0x52, 0x41//CONSECTETUERA T
    };

    int expected_length = (4 + 10) + (4 + 1) + (4 + 12) + (4 + 13);
    unsigned char dst[expected_length];
    const char* fmt = "A";
    check_packsize_inconsistent(fmt);

    const auto err = dlis_packf( fmt, source, dst );
    CHECK( err == DLIS_OK );

    int dst_index = 0;
    read_varstring(dst, &dst_index, 10, std::string("LOREMIPSUM"));
    read_int32(dst, &dst_index, 10);
    read_int8(dst, &dst_index, 69);
    read_varstring(dst, &dst_index, 12, std::string("DOLORSITAMET"));
    read_varstring(dst, &dst_index, 13, std::string("CONSECTETUERA"));

    CHECK( expected_length == dst_index );
}


TEST_CASE("pack unexpected value", "[scan]") {
    const unsigned char source[] = {
        0x59, // 89 sshort
        0x01, 0x53, //"S" ident
    };

    unsigned char dst[6];
    const char* fmt = "ust";

    //check_packsize_invalid_arguments(fmt);
    //due to inconsistent arg, it doesn't return that it's invalid. Expected?

    const auto err = dlis_packf( fmt, source, dst );

    CHECK( err == DLIS_UNEXPECTED_VALUE);
    CHECK( dst[0] == 89);
    CHECK( dst[5] == 'S');
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
