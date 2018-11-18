#include <cstdint>
#include <cstring>
#include <sstream>
#include <tuple>

#include <catch2/catch.hpp>

#include <dlisio/dlisio.h>
#include <dlisio/types.h>

#include "../dlisio/ext/io.hpp"

using filestream = dl::basic_file< std::stringstream >;

void write_vrl( filestream& fs, int len ) {
    std::array< char, DLIS_VRL_SIZE > xs;
    void* ptr = xs.data();

    ptr = dlis_unormo( ptr, len + DLIS_VRL_SIZE );
    ptr = dlis_ushorto( ptr, 0xFF );
    ptr = dlis_ushorto( ptr, 1 );

    fs.write( xs.data(), xs.size() );
}

void write_iflr_segment( filestream& fs, int len, std::uint8_t attrs = 0 ) {
    std::array< char, DLIS_VRL_SIZE > xs;
    void* ptr = xs.data();

    ptr = dlis_unormo( ptr, len + DLIS_LRSH_SIZE );
    ptr = dlis_ushorto( ptr, attrs );
    ptr = dlis_ushorto( ptr, 0 );

    fs.write( xs.data(), xs.size() );
}

std::array< char, 8 > iflr( std::string name = "iflr" ) {
    decltype(iflr()) xs;

    void* ptr = xs.data();

    ptr = dlis_uvario( ptr, 1, 2 );
    ptr = dlis_ushorto( ptr, 1 );
    ptr = dlis_ushorto( ptr, 4 );
    std::memcpy( ptr, "iflr", 4 );
    return xs;
}

TEST_CASE("IFRL in single VRL, unsegmented, minimal size") {
    filestream fs;

    std::array< char, 4 > body = {};
    const auto name = iflr();

    write_vrl( fs, name.size() + body.size() + DLIS_LRSH_SIZE );
    write_iflr_segment( fs, name.size() + body.size() );
    fs.write( name.data(), name.size() );
    fs.write( body.data(), body.size() );

    const auto last = body.size() + name.size()
                    + DLIS_LRSH_SIZE + DLIS_VRL_SIZE
                    ;


    const auto x = dl::tag( fs, 0 );
    CHECK( x.first == 0 );
    CHECK( std::get< 0 >( x.second.name ) == 1 );
    CHECK( std::get< 1 >( x.second.name ) == 1 );
    CHECK( std::get< 2 >( x.second.name ) == "iflr" );
    CHECK( fs.tell() == last );
}

TEST_CASE("IFRL in single VRL, unsegmented, obname and body") {
    filestream fs;

    std::array< char, 100 > body = {};
    const auto name = iflr();

    const auto last = body.size() + name.size()
                    + DLIS_LRSH_SIZE
                    + DLIS_VRL_SIZE
                    ;

    write_vrl( fs, last - DLIS_VRL_SIZE );
    write_iflr_segment( fs, name.size() + body.size() );
    fs.write( name.data(), name.size() );
    fs.write( body.data(), body.size() );

    const auto x = dl::tag( fs, 0 );
    CHECK( x.first == 0 );
    CHECK( std::get< 0 >( x.second.name ) == 1 );
    CHECK( std::get< 1 >( x.second.name ) == 1 );
    CHECK( std::get< 2 >( x.second.name ) == "iflr" );
    CHECK( fs.tell() == last );
}

TEST_CASE("IFRL in single VRL, segmented after obname") {
    filestream fs;

    std::array< char, 100 > body = {};
    const auto name = iflr();

    const auto last = name.size()
                    + 2 * body.size()
                    + 2 * DLIS_LRSH_SIZE
                    + DLIS_VRL_SIZE
                    ;

    write_vrl( fs, last - DLIS_VRL_SIZE );
    write_iflr_segment( fs, name.size() + body.size(), DLIS_SEGATTR_SUCCSEG );
    fs.write( name.data(), name.size() );
    fs.write( body.data(), body.size() );

    write_iflr_segment( fs, body.size() );
    fs.write( body.data(), body.size() );

    const auto x = dl::tag( fs, 0 );
    CHECK( x.first == 0 );
    CHECK( std::get< 0 >( x.second.name ) == 1 );
    CHECK( std::get< 1 >( x.second.name ) == 1 );
    CHECK( std::get< 2 >( x.second.name ) == "iflr" );
    CHECK( fs.tell() == last );
}

TEST_CASE("IFRL single VRL, full obname first segment") {
    filestream fs;

    std::array< char, 100 > body = {};
    std::array< char, 36 > name;

    const std::string refstr = "01234"
                               "56789"
                               "01234"
                               "56789"
                               "01234"
                               "56789"
                               "01";

    void* ptr = name.data();
    ptr = dlis_uvario( ptr, 1, 2 );
    ptr = dlis_ushorto( ptr, 1 );
    ptr = dlis_ushorto( ptr, refstr.size() );
    std::memcpy( ptr, refstr.data(), refstr.size() );
    const auto last = name.size()
                    + 2 * body.size()
                    + 2 * DLIS_LRSH_SIZE
                    + DLIS_VRL_SIZE
                    ;

    write_vrl( fs, last - DLIS_VRL_SIZE );
    write_iflr_segment( fs, name.size() + body.size(), DLIS_SEGATTR_SUCCSEG );
    fs.write( name.data(), name.size() );
    fs.write( body.data(), body.size() );

    write_iflr_segment( fs, body.size() );
    fs.write( body.data(), body.size() );

    const auto x = dl::tag( fs, 0 );
    CHECK( x.first == 0 );
    CHECK( std::get< 0 >( x.second.name ) == 1 );
    CHECK( std::get< 1 >( x.second.name ) == 1 );
    CHECK( std::get< 2 >( x.second.name ) == refstr );
    CHECK( fs.tell() == last );
}

TEST_CASE("IFRL single VRL, full obname split across segments") {
    filestream fs;

    std::array< char, 100 > body = {};
    std::array< char, 14 > name_fst;
    std::array< char, 22 > name_snd;

    const std::string refstr = "01234"
                               "56789"
                               "01234"
                               "56789"
                               "01234"
                               "56789"
                               "01";

    void* ptr = name_fst.data();
    ptr = dlis_uvario( ptr, 1, 2 );
    ptr = dlis_ushorto( ptr, 1 );
    ptr = dlis_ushorto( ptr, refstr.size() );
    std::memcpy( ptr, refstr.data(), 10 );
    std::memcpy( name_snd.data(), refstr.data() + 10, name_snd.size() );
    const auto last = name_fst.size()
                    + name_snd.size()
                    + body.size()
                    + 2 * DLIS_LRSH_SIZE
                    + DLIS_VRL_SIZE
                    ;

    write_vrl( fs, last - DLIS_VRL_SIZE );
    write_iflr_segment( fs, name_fst.size(), DLIS_SEGATTR_SUCCSEG );
    fs.write( name_fst.data(), name_fst.size() );

    write_iflr_segment( fs, name_snd.size() + body.size() );
    fs.write( name_snd.data(), name_snd.size() );
    fs.write( body.data(), body.size() );

    const auto x = dl::tag( fs, 0 );
    CHECK( x.first == 0 );
    CHECK( std::get< 0 >( x.second.name ) == 1 );
    CHECK( std::get< 1 >( x.second.name ) == 1 );
    CHECK( std::get< 2 >( x.second.name ) == refstr );
    CHECK( fs.tell() == last );
}

TEST_CASE("IFRL obname split across two VRLs") {
    filestream fs;

    std::array< char, 100 > body = {};
    std::array< char, 14 > name_fst;
    std::array< char, 22 > name_snd;

    const std::string refstr = "01234"
                               "56789"
                               "01234"
                               "56789"
                               "01234"
                               "56789"
                               "01";

    void* ptr = name_fst.data();
    ptr = dlis_uvario( ptr, 1, 2 );
    ptr = dlis_ushorto( ptr, 1 );
    ptr = dlis_ushorto( ptr, refstr.size() );
    std::memcpy( ptr, refstr.data(), 10 );
    std::memcpy( name_snd.data(), refstr.data() + 10, name_snd.size() );
    const auto last = name_fst.size()
                    + name_snd.size()
                    + body.size()
                    + 2 * DLIS_LRSH_SIZE
                    + 2 * DLIS_VRL_SIZE
                    ;

    write_vrl( fs, name_fst.size() + DLIS_LRSH_SIZE );
    write_iflr_segment( fs, name_fst.size(), DLIS_SEGATTR_SUCCSEG );
    fs.write( name_fst.data(), name_fst.size() );

    write_vrl( fs, name_snd.size() + body.size() + DLIS_VRL_SIZE );
    write_iflr_segment( fs, name_snd.size() + body.size() );
    fs.write( name_snd.data(), name_snd.size() );
    fs.write( body.data(), body.size() );

    const auto x = dl::tag( fs, 0 );
    CHECK( x.first == 0 );
    CHECK( std::get< 0 >( x.second.name ) == 1 );
    CHECK( std::get< 1 >( x.second.name ) == 1 );
    CHECK( std::get< 2 >( x.second.name ) == refstr );
    CHECK( fs.tell() == last );
}
