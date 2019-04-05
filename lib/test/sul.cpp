#include <cstring>
#include <sstream>
#include <string>
#include <cstdint>
#include <map>

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

struct correct_sul
{
    std::string seqstr = "   1";
    std::string revistr  = "V1.00";
    std::string structur  = "RECORD";
    std::string maxilen = "08192";
    std::string id = std::string(60, 'X');

    SULv1 v1;

    protected:
    void check_sul(std::string exp_input, int exp_return_value){
        INFO( "Storage unit label:\n" << blockify( exp_input ) );
        auto err = dlis_sul( exp_input.c_str(),
                             &v1.seqnum,
                             &v1.major,
                             &v1.minor,
                             &v1.layout,
                             &v1.maxlen,
                             v1.id );

        CHECK( err == exp_return_value );
    }
};

TEST_CASE_METHOD(correct_sul, "SUL with base check correct values", "[sul]") {
    check_sul(seqstr + revistr + structur + maxilen + id, DLIS_OK);
}


TEST_CASE_METHOD(correct_sul, "seq can't be null", "[sul]") {
    check_sul("   0" + revistr + structur + maxilen + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "seq can't be negative", "[sul]") {
    check_sul("  -1" + revistr + structur + maxilen + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "seq can be left-hand formatted", "[sul]") {
    check_sul("1   " + revistr + structur + maxilen + id, DLIS_OK);
}

TEST_CASE_METHOD(correct_sul, "seq should be a valid integer", "[sul]") {
    check_sul("  1." + revistr + structur + maxilen + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "seq can't contain more than 1 number", "[sul]") {
    check_sul("1 0 " + revistr + structur + maxilen + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "seq can't contain invalid characters", "[sul]") {
    check_sul("A3B!" + revistr + structur + maxilen + id, DLIS_INCONSISTENT);
}


TEST_CASE_METHOD(correct_sul, "revision V1 is only supported one", "[sul]") {
    check_sul(seqstr + "V2.00" + structur + maxilen + id, DLIS_UNEXPECTED_VALUE);
}

TEST_CASE_METHOD(correct_sul, "revision V1.00 is only suppoerted one", "[sul]") {
    check_sul(seqstr + "V1.99" + structur + maxilen + id, DLIS_UNEXPECTED_VALUE);
}

TEST_CASE_METHOD(correct_sul, "revision should start from capital", "[sul]") {
    check_sul(seqstr + "v1.00" + structur + maxilen + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "revision should be in a valid format", "[sul]") {
    check_sul(seqstr + "V1.0A" + structur + maxilen + id, DLIS_INCONSISTENT);
}


TEST_CASE_METHOD(correct_sul, "structure should be capital RECORD", "[sul]") {
    check_sul(seqstr + revistr + "record" + maxilen + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "structure should have all capitals", "[sul]") {
    check_sul(seqstr + revistr + "Record" + maxilen + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "structure could be only RECORD", "[sul]") {
    check_sul(seqstr + revistr + "dlisio" + maxilen + id, DLIS_INCONSISTENT);
}


TEST_CASE_METHOD(correct_sul, "maxlen can't be negative", "[sul]") {
    check_sul(seqstr + revistr + structur + "   -1" + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "maxlen can't be empty", "[sul]") {
    check_sul(seqstr + revistr + structur + "     " + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "maxlen can be left-hand formatted", "[sul]") {
    check_sul(seqstr + revistr + structur + "128  " + id, DLIS_OK);
}

TEST_CASE_METHOD(correct_sul, "maxlen should be an integer", "[sul]") {
    check_sul(seqstr + revistr + structur + "234.1" + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "maxlen should have only 1 number", "[sul]") {
    check_sul(seqstr + revistr + structur + "222 3" + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "maxlen should have only 1 number, even if 0", "[sul]") {
    check_sul(seqstr + revistr + structur + "0 128" + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "maxlen can't have alpha characters", "[sul]") {
    check_sul(seqstr + revistr + structur + " 123A" + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "maxlen could have only preceeding spaces", "[sul]") {
    check_sul(seqstr + revistr + structur + ".1234" + id, DLIS_INCONSISTENT);
}

TEST_CASE_METHOD(correct_sul, "maxlen can't consist of invalid characters", "[sul]") {
    check_sul(seqstr + revistr + structur + "ABCDE" + id, DLIS_INCONSISTENT);
}


TEST_CASE_METHOD(correct_sul, "maxlen can be bigger than supposed VRL", "[sul]") {
    check_sul(seqstr + revistr + structur + "16385" + id, DLIS_OK);
}


TEST_CASE_METHOD(correct_sul, "SUL with null seqnum", "[sul][nulls]") {
    auto label = "   0" + revistr + structur + maxilen + id;
    auto err = dlis_sul( label.c_str(), nullptr, &v1.major, &v1.minor,
                                        &v1.layout, &v1.maxlen, v1.id );
    CHECK( err == DLIS_OK );
    CHECK( v1.layout == DLIS_STRUCTURE_RECORD );
    CHECK( v1.maxlen == std::stoi(maxilen) );
    CHECK( v1.id == id );
}

TEST_CASE_METHOD(correct_sul, "SUL with null layout", "[sul][nulls]") {
    auto label = seqstr + revistr + "DLISIO" + maxilen + id;
    auto err = dlis_sul( label.c_str(), &v1.seqnum, &v1.major, &v1.minor,
                                        nullptr, &v1.maxlen, v1.id );
    CHECK( err == DLIS_OK );
    CHECK( v1.seqnum == std::stoi(seqstr) );
    CHECK( v1.maxlen == std::stoi(maxilen) );
    CHECK( v1.id == id );
}

TEST_CASE_METHOD(correct_sul, "SUL with null maxlen", "[sul][nulls]") {
    auto label = seqstr + revistr + structur + "ABCDE" + id;
    auto err = dlis_sul( label.c_str(), &v1.seqnum, &v1.major, &v1.minor,
                                        &v1.layout, nullptr, v1.id );
    CHECK( err == DLIS_OK );
    CHECK( v1.seqnum == std::stoi(seqstr) );
    CHECK( v1.layout == DLIS_STRUCTURE_RECORD );
    CHECK( v1.id == id );
}

TEST_CASE_METHOD(correct_sul, "SUL with null id", "[sul][nulls]") {
    auto label = seqstr + revistr + structur + maxilen + "/0";
    auto err = dlis_sul( label.c_str(), &v1.seqnum, &v1.major, &v1.minor,
                                        &v1.layout, &v1.maxlen, nullptr );
    CHECK( err == DLIS_OK );
    CHECK( v1.seqnum == std::stoi(seqstr) );
    CHECK( v1.layout == DLIS_STRUCTURE_RECORD );
    CHECK( v1.maxlen == std::stoi(maxilen) );
}

TEST_CASE_METHOD(correct_sul, "SUL with garbage minor/major version", "[sul]") {
    auto label = seqstr + "ABCDE" + structur + maxilen + id;
    auto err = dlis_sul( label.c_str(), &v1.seqnum, &v1.major, &v1.minor,
                                        &v1.layout, &v1.maxlen, v1.id );
    CHECK( err == DLIS_INCONSISTENT);
    CHECK( v1.seqnum == std::stoi(seqstr) );
    CHECK( v1.major == 1 );
    CHECK( v1.minor == 0 );
    CHECK( v1.layout == DLIS_STRUCTURE_RECORD );
    CHECK( v1.maxlen == std::stoi(maxilen) );
    CHECK( v1.id == id );
}

static const char plain_sul[] = "   1"
                                "V1.00"
                                "RECORD"
                                " 8192"
                                "Default Storage Set "
                                "                    "
                                "                    "
                                ;

TEST_CASE("Find SUL after 14 bytes of garbage", "[sul]") {
    SULv1 ref;
    ref.seqnum = 1;
    ref.major  = 1;
    ref.minor  = 0;
    ref.layout = DLIS_STRUCTURE_RECORD;
    ref.maxlen = 8192;
    std::strcpy( ref.id, "Default Storage Set "
                         "                    "
                         "                    " );

    const std::string noise = "14 bytes noise";
    const auto reel = noise + plain_sul;

    long long off;
    const auto err = dlis_find_sul(reel.data(), reel.size(), &off);

    REQUIRE(!err);
    CHECK(off == noise.size());

    auto label = reel.substr(off);
    const auto v1 = parse_sulv1(label);
    CHECK(v1 == ref);
}

TEST_CASE("Find SUL when there is no garbage", "[sul]") {
    long long off = -1;
    const auto err = dlis_find_sul(plain_sul, sizeof(plain_sul), &off);

    CHECK(!err);
    CHECK(off == 0);
}

TEST_CASE("find_sul gracefully handles missing SUL", "[sul]") {
    const auto stream = std::vector< char >(400, '.');
    long long off;
    const auto err = dlis_find_sul(stream.data(), stream.size() / 2, &off);
    CHECK(err == DLIS_NOTFOUND);
}

TEST_CASE("find_sul gracefully handles truncated SUL", "[sul]") {
    const auto shift = 3;
    auto stream = std::vector< char >(400, '.');
    std::copy_n(plain_sul + shift, sizeof(plain_sul) - shift, stream.begin());

    long long off;
    const auto err = dlis_find_sul(stream.data(), stream.size() / 2, &off);
    CHECK(err == DLIS_INCONSISTENT);
}
