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

struct one_record {
    one_record() {
        begin = file;
        end = std::copy( plain16,
                         plain16 + plain16_size,
                         begin );
    }

    char* begin;
    char* end;
    char file[plain16_size];
    int initial_residual = 0;
};

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
    0xC0,       /* seg.attr: explicit | pred */
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

static const unsigned char multisegment2VR[] = {
    /* first VR */
    0x00, 0x18, /* VRL.len */
    0xFF,       /* VRL.padding */
    0x01,       /* VRL.version */

    /* first LRS: header */
    0x00, 0x14, /* seg.len */
    0xa0,       /* seg.attr: explicit | succ */
    0x00,       /* seg.type */

    /* first LRS: 16 bytes body */
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    /* no trailer */

    /* second VR */
    0x00, 0x18, /* VRL.len */
    0xFF,       /* VRL.padding */
    0x01,       /* VRL.version */

    /* second LRS: header */
    0x00, 0x14, /* seg.len */
    0xC0,       /* seg.attr: explicit | pred */
    0x00,       /* seg.type */

    /* second LRS: 16 bytes body */
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    /* no trailer */
};

struct multi_segment_record_2_visible_records {
    multi_segment_record_2_visible_records() {
        begin = file;
        end = std::copy( multisegment2VR,
                         multisegment2VR + sizeof(multisegment2VR),
                         begin );
    }

    char* begin;
    char* end;
    char file[sizeof(multisegment2VR)];
    int initial_residual = 0;
};

static const unsigned char multirecords[] = {
    /*VR */
    0x00, 0x40, /* VRL.len */
    0xFF,       /* VRL.padding */
    0x01,       /* VRL.version */

    /* first LR:*/
    /* header */
    0x00, 0x14, /* seg.len */
    0x80,       /* seg.attr: explicit */
    0x00,       /* seg.type */

    /* 16 bytes body */
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    /* no trailer */

    /* second LR:*/
    /* header */
    0x00, 0x14, /* seg.len */
    0x00,       /* seg.attr:  */
    0x00,       /* seg.type */

    /* 16 bytes body */
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    /* no trailer */

    /* thrid LR:*/
    /* header */
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

struct multi_logical_records_in_1_visible_envelope {
    multi_logical_records_in_1_visible_envelope() {
        begin = file;
        end = std::copy( multirecords,
                         multirecords + sizeof(multirecords),
                         begin );
    }

    char* begin;
    char* end;
    char file[sizeof(multirecords)];
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

TEST_CASE_METHOD( multi_logical_records_in_1_visible_envelope,
                  "truncated 2nd logical record in same visible envelope",
                  "[envelope]") {
    int count = 0;
    long long tells[3];
    int explicits[3];
    int residuals[3];
    const char* next;
    int err;


    auto trunc_end = begin + 4 + 20 + 1;
    err = dlis_index_records( begin,
                              trunc_end,
                              3,
                              &initial_residual,
                              &next,
                              &count,
                              tells,
                              residuals,
                              explicits );
    CHECK( err == DLIS_TRUNCATED );
    CHECK( count == 1 );
}

TEST_CASE_METHOD(one_record,
                 "truncated LR due to existing successor, no new VR",
                 "[envelope]") {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
    const char* next;
    file[6] = 0xA0; //set successor
    const auto err = dlis_index_records( begin,
                                         end,
                                         1,
                                         &initial_residual,
                                         &next,
                                         &count,
                                         tells,
                                         residuals,
                                         explicits );
    CHECK( err == DLIS_TRUNCATED );
    CHECK( count == 0 );
}

TEST_CASE_METHOD(two_records,
                 "truncated VR after segment end, follow with garbage",
                 "[envelope]") {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
    const char* next;
    file[1] = 0x30; //set VRL
    file[6] = 0xA0; //set successor
    file[plain16_size + 1] = 16;
    auto err = dlis_index_records( begin,
                                   begin + plain16_size,
                                   1,
                                   &initial_residual,
                                   &next,
                                   &count,
                                   tells,
                                   residuals,
                                   explicits );
    CHECK( err == DLIS_TRUNCATED );
    CHECK( count == 0 );

    file[plain16_size + 1] = 0;
    err = dlis_index_records( begin,
                              begin + plain16_size,
                              1,
                              &initial_residual,
                              &next,
                              &count,
                              tells,
                              residuals,
                              explicits );
    CHECK( err == DLIS_TRUNCATED );
    CHECK( count == 0 );
}

TEST_CASE_METHOD(multi_segment_record,
                 "truncated in LRSH",
                 "[envelope]") {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
    const char* next;
    const auto err = dlis_index_records( begin,
                                         begin + 27,
                                         1,
                                         &initial_residual,
                                         &next,
                                         &count,
                                         tells,
                                         residuals,
                                         explicits );
    CHECK( err == DLIS_TRUNCATED );
    CHECK( count == 0 );
}

TEST_CASE_METHOD( multi_segment_record,
                  "valid, multi-segment record"
                  "[envelope]" ) {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
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
    CHECK( next == end );

    CHECK( count == 1 );
    CHECK( tells[0] == std::distance(end, begin) );
    CHECK( residuals[0] == 0 );
    CHECK( explicits[0] );
}

TEST_CASE_METHOD( multi_segment_record_2_visible_records,
                  "multi-segment record spaced on 2 visible records"
                  "[envelope]" ) {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
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
    CHECK( next == end );

    CHECK( count == 1 );
    CHECK( tells[0] == std::distance(end, begin) );
    CHECK( residuals[0] == 0 );
    CHECK( explicits[0] );
}

TEST_CASE_METHOD( multi_logical_records_in_1_visible_envelope,
                  "multi logical records spaced in 1 visible record"
                  "[envelope]" ) {
    int count = 0;
    long long tells[3];
    int explicits[3];
    int residuals[3];
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

    //data: 4 bytes of VR header, 20 bytes x 3 for logical segments

    CHECK( count == 2 );
    CHECK( tells[0] == std::distance(end, begin) );
    CHECK( residuals[0] == 0 );
    CHECK( explicits[0] );
    CHECK( tells[1] == -40 );
    CHECK( residuals[1] == 40 );
    CHECK( !explicits[1] );
    CHECK( initial_residual == 20 );

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
    CHECK( count == 3 );
    CHECK( tells[2] == -20 );
    CHECK( residuals[2] == 20 );
    CHECK( explicits[2] );
}


TEST_CASE_METHOD(one_record, "0 allocsize on start", "[envelope]") {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
    const char* next;
    const auto err = dlis_index_records( begin,
                                         end,
                                         0,
                                         &initial_residual,
                                         &next,
                                         &count,
                                         tells,
                                         residuals,
                                         explicits );
    CHECK( err == DLIS_OK );
    CHECK( next == begin );
    CHECK( count == 0 );
}

TEST_CASE_METHOD(one_record, "same begin and end on start", "[envelope]") {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
    const char* next;
    const auto err = dlis_index_records( begin,
                                         begin,
                                         1,
                                         &initial_residual,
                                         &next,
                                         &count,
                                         tells,
                                         residuals,
                                         explicits );
    CHECK( err == DLIS_INVALID_ARGS );
    CHECK( count == 0 );
}

TEST_CASE_METHOD(one_record, "insufficent VR length", "[envelope]") {
    int count = 0;
    long long tells[1];
    int explicits[1];
    int residuals[1];
    const char* next;
    file[1] = 0x0A;
    const auto err = dlis_index_records( begin,
                                         begin + 10,
                                         1,
                                         &initial_residual,
                                         &next,
                                         &count,
                                         tells,
                                         residuals,
                                         explicits );
    CHECK( err == DLIS_UNEXPECTED_VALUE );
    CHECK( count == 0 );
}

TEST_CASE_METHOD(one_record, "null next and explicits", "[envelope]") {
    int count = 0;
    //more than sufficient allocation space and allocsize
    long long tells[2];
    int residuals[2];
    const auto err = dlis_index_records( begin,
                                         end,
                                         2,
                                         &initial_residual,
                                         nullptr,
                                         &count,
                                         tells,
                                         residuals,
                                         nullptr );
    CHECK( err == DLIS_OK );
    CHECK( count == 1 );
}
