#include <algorithm>
#include <iterator>

#include <catch2/catch.hpp>

#include <dlisio/dlisio.h>


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
