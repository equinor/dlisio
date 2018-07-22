#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>

#include <dlisio/dlisio.h>

namespace {

struct fcloser {
    void operator()( std::FILE* fp ) { if( fp ) std::fclose( fp ); }
};

void readf( std::vector< char >& buf, std::size_t nmemb, std::FILE* fp ) {
    auto readc = std::fread( buf.data(), 1, nmemb, fp );
    buf.resize( nmemb );
    if( readc == nmemb ) return;

    if( std::feof( fp ) ) {
        std::fputs( "Unexpected EOF", stderr );
        std::exit( 1 );
    }

    std::perror( "" );
    std::exit( 1 );
}

int storage_unit_label( const char* buffer ) {
    int seqnum;
    int major;
    int minor;
    int layout;
    std::int64_t maxlen;
    char id[ 61 ] = {};
    auto err = dlis_sul( buffer, &seqnum,
                                 &major,
                                 &minor,
                                 &layout,
                                 &maxlen,
                                 id );

    if( err ) {
        std::fputs( "unabe to parse SUL", stderr );
        std::exit( 1 );
    }

    if( major != 1 && minor != 0 ) {
        std::fprintf( stderr, "only DLIS v1 supported, was v%d.%d\n",
                              major, minor );
        std::exit( 1 );
    }

    std::printf( "sequence-number: %d\n"
                 "dlis-version: v%d.%d\n"
                 "record-layout: %s\n"
                 "record-max-len: %" PRId64 "\n"
                 "identifier: %s\n",
                 seqnum,
                 major, minor,
                 layout == DLIS_STRUCTURE_RECORD
                        ? "RECORD"
                        : "UNKNOWN",
                maxlen,
                id );

    return 80;
}

int visible_record_label( const char* buffer, int record ) {
    int recordlen;
    int version;
    int err = dlis_vrl( buffer, &recordlen, &version );

    if( err ) {
        std::fprintf( stderr, "unable to parse VRL %d\n", record );
        std::exit( 1 );
    }

    std::printf( "record-len %d: %d\n", record, recordlen );
    return 4;
}

int logical_segment_header( const char* buffer, int record, int segment ) {
    int seglen;
    uint8_t attrs;
    int type;
    auto err = dlis_lrsh( buffer, &seglen, &attrs, &type );

    if( err ) {
        std::fprintf( stderr, "unable to parse LRSH %d.%d\n",
                              record, segment );
        std::exit( 1 );
    }

    std::printf( "segment-len %d.%d: %d\n"
                 "segment-type %d.%d: %d\n",
                 record, segment, seglen,
                 record, segment, type );

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

    std::string attributes;
    if( explicit_formatting )   attributes += "explicit-formatting ";
    if( has_predecessor )       attributes += "has-predecessor ";
    if( has_successor )         attributes += "has-successor ";
    if( is_encrypted )          attributes += "is-encrypted ";
    if( has_encryption_packet ) attributes += "has-encryption-packet ";
    if( has_checksum )          attributes += "has-checksum ";
    if( has_trailing_length )   attributes += "has-trailing-len ";
    if( has_padding )           attributes += "has-padding ";

    /* remove trailing white-space */
    if( !attributes.empty() ) attributes.pop_back();

    std::printf( "segment-attributes %d.%d: %s\n",
                 record, segment, attributes.c_str() );

    return 4;
}

void describe( const char* fname ) {
    std::unique_ptr< std::FILE, fcloser > ufp(
        std::fopen( fname, "rb" )
    );

    if( !ufp ) {
        std::perror( "" );
        return;
    }

    auto* fp = ufp.get();

    std::vector< char > buffer( 4096, 0 );

    readf( buffer, 80, fp );
    int len = storage_unit_label( buffer.data() );

    for( int record = 0; ; record++ ) {
        readf( buffer, 4, fp );
        visible_record_label( buffer.data(), record );

        for( int segment = 0; ; segment++ ) {
            readf( buffer, 4, fp );
            logical_segment_header( buffer.data(), record, segment );

            /* since no records are actually read now, just exit */
            return;
        }

        break;
    }
}

}

int main( int args, char** argv ) {
    for( int i = 1; i < args; ++i )
        describe( argv[ i ] );
}
