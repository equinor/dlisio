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
    std::strcpy( ref.id, "Default Storage Set"
                         "                   "
                         "                   " );

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
        "Default Storage Set"
        "                   "
        "                   ",
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
    std::strcpy( ref.id, "Default Storage Set"
                         "                   "
                         "                   " );

    static const std::string pre = "   1"
                                   "V1.00"
                                   "RECORD";

    static const std::string post = "Default Storage Set"
                                    "                   "
                                    "                   ";

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
