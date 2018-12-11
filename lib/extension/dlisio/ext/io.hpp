#ifndef DLISIO_PYTHON_IO_HPP
#define DLISIO_PYTHON_IO_HPP

#include <array>
#include <iosfwd>
#include <string>
#include <tuple>

#include <dlisio/ext/types.hpp>

namespace dl {

struct bookmark {
    std::streamsize tell = 0;
    /*
     * the remaining bytes of the "previous" visible record. if 0, the current
     * object is the visible record label
     */
    int residual = 0;

    int isexplicit = 0;
    int isencrypted = 0;

    object_name name;

    /*
     * only pos is used for seeking and repositioning - tell is used only for
     * __repr__ and debugging purposes
     */
};

template< typename Stream = std::ifstream >
class basic_file {
public:
    basic_file() {
        fs.exceptions( fs.exceptions() | std::ios_base::eofbit );
    }
    explicit basic_file( const std::string& path );

    template< int N > std::array< char, N > read();
    std::vector< char > read( std::streamsize nmemb );
    char* read( char*, std::streamsize nmemb );

    void write( const char*, std::streamsize nmemb );

    bool eof();

    std::streamsize tell();
    basic_file& seek( std::streamsize );
    basic_file& skip( std::streamsize );

    void close();

private:
    Stream fs;
};

template< typename Stream >
basic_file< Stream >::basic_file( const std::string& path ) :
    fs( path, std::ios_base::binary | std::ios_base::in )
{
    fs.exceptions( fs.exceptions() | std::ios_base::eofbit );
}

template< typename Stream >
template< int N >
std::array< char, N > basic_file< Stream >::read() {
    std::array< char, N > xs;
    this->read( xs.data(), N );
    return xs;
}

template< typename Stream >
std::vector< char > basic_file< Stream >::read( std::streamsize nmemb ) {
    std::vector< char > xs( nmemb );
    this->read( xs.data(), nmemb );
    return xs;
}

template< typename Stream >
char* basic_file< Stream >::read( char* buffer, std::streamsize nmemb ) {
    this->fs.read( buffer, nmemb );
    return buffer;
}

template< typename Stream >
void basic_file< Stream >::write( const char* buffer, std::streamsize nmemb ) {
    this->fs.write( buffer, nmemb );
}

template< typename Stream >
bool basic_file< Stream >::eof() {
    /*
     * This is a little hairy, but it seems like macos/clang/libc++ treats
     * eof-flags and failbit slightly differently from linux/clang and
     * linux/gcc.
     *
     * The intention is to move away from iostream anyway (to memory-mapping or
     * similar), so just keep it like this for now.
     */
    try {
        this->fs.peek();
        if ( !this->fs.eof() ) return false;
    } catch ( std::ios_base::failure& ) {
        if ( !this->fs.eof() ) throw;
    }

    this->fs.clear();
    return true;
}

template< typename Stream >
std::streamsize basic_file< Stream >::tell() {
    return this->fs.tellg();
}

template< typename Stream >
basic_file< Stream >& basic_file< Stream >::seek( std::streamsize pos ) {
    this->fs.seekg( pos, std::ios_base::beg );
    return *this;
}

template< typename Stream >
basic_file< Stream >& basic_file< Stream >::skip( std::streamsize n ) {
    this->fs.seekg( n, std::ios_base::cur );
    return *this;
}

template< typename Stream >
void basic_file< Stream >::close() {
    this->fs.close();
}

struct segheader {
    std::uint8_t attrs;
    int len;
    int type;
};

template< typename Stream >
segheader segment_header( basic_file< Stream >& fs ) {
    auto buffer = fs.template read< DLIS_LRSH_SIZE >();

    segheader seg;
    const auto err = dlis_lrsh( buffer.data(), &seg.len,
                                               &seg.attrs,
                                               &seg.type );
    if( err ) throw std::invalid_argument(
            "unable to parse logical record segment header"
    );
    return seg;
}

template< typename Stream >
int visible_length( basic_file< Stream >& fs ) {
    auto buffer = fs.template read< DLIS_VRL_SIZE >();

    int len, version;
    const auto err = dlis_vrl( buffer.data(), &len, &version );
    if( err ) throw std::invalid_argument(
            "unable to parse visible record label"
    );

    if( version != 1 ) {
        std::string msg = "VRL DLIS not v1, was " + std::to_string( version );
        // TODO: warning
    }

    return len;
}

template< typename Stream >
int skiprecord( basic_file< Stream >& fs, int remaining ) {
    while( true ) {

        /*
         * if remaining = 0 this is at the VRL, skip the inner-loop and read it
         */
        while( remaining > 0 ) {
            auto seg = segment_header( fs );

            if( seg.len > remaining ) {
                // TODO: better exception
                throw std::runtime_error( "skip: seg.len > vrl.len ("
                    + std::to_string( seg.len ) + " > "
                    + std::to_string( remaining ) + ")" );
            }

            remaining -= seg.len;

            int isexplicit = 0;
            int has_predecessor = 0;
            int has_successor = 0;
            int has_encryption_packet = 0;
            int isencrypted = 0;
            int has_checksum = 0;
            int has_trailing_length = 0;
            int has_padding = 0;
            dlis_segment_attributes( seg.attrs, &isexplicit,
                                                &has_predecessor,
                                                &has_successor,
                                                &isencrypted,
                                                &has_encryption_packet,
                                                &has_checksum,
                                                &has_trailing_length,
                                                &has_padding );

            seg.len -= DLIS_LRSH_SIZE;
            fs.skip( seg.len );

            if( !has_successor ) return remaining;
        }

        /* if remaining is 0, then we're at a VRL */
        remaining = visible_length( fs ) - DLIS_VRL_SIZE;
    }
}


/*
 * TODO: account for padding
 */
template< typename Stream >
std::pair< int, bookmark > tag( basic_file< Stream >& fs, int remaining ) {
    bookmark mark;
    mark.residual = remaining;
    mark.tell = fs.tell();

    /*
     * there's a bit of state to keep track of, that all change very similarly,
     * so bundle it up and automate it
     */
    struct Cursor {
        basic_file< Stream >& fs;
        int remaining;
        segheader seg;
        int strlen = 0;
        bool has_successor = false;

        Cursor( basic_file< Stream >& f, int rem ) :
            fs( f ), remaining( rem )
        {}

        char* read( char* dst, int count ) {
            this->fs.read( dst, count );
            this->remaining -= count;
            this->seg.len -= count;
            this->strlen += count;
            return dst + count;
        }

        void next_segment() {
            this->seg = segment_header( fs );
            this->seg.len -= DLIS_LRSH_SIZE;
            this->remaining -= DLIS_LRSH_SIZE;
            this->has_successor = seg.attrs & DLIS_SEGATTR_SUCCSEG;

            if( this->seg.len > this->remaining ) {
                // TODO: better exception
                // TODO: should be warning?
                throw std::runtime_error(
                      "seg.len > vrl.len ("
                    + std::to_string( this->seg.len )
                    + " > "
                    + std::to_string( this->remaining )
                    + ")"
                    + " at " + std::to_string( this->fs.tell() ) );
            }
        }

        void next_visible() {
            if( this->remaining == 0 )
                this->remaining = visible_length( this->fs ) - DLIS_VRL_SIZE;
        }

        int skip_remaining() {
            this->fs.skip( this->seg.len );
            this->remaining -= this->seg.len;

            if( this->has_successor )
                this->remaining = skiprecord( this->fs, this->remaining );

            return this->remaining;

        }

    } cursor{ fs, remaining };

    cursor.next_visible();
    cursor.next_segment();

    mark.isexplicit  = cursor.seg.attrs & DLIS_SEGATTR_EXFMTLR;
    mark.isencrypted = cursor.seg.attrs & DLIS_SEGATTR_ENCRYPT;

    /*
     * if explicit, callers can consider to either read it now, or manually
     * skip it and parse it later
     *
     * TODO: actually don't skip on EFLRs, but let caller manage
     *
     * skip encrypted records completely
     */
    if( mark.isexplicit || mark.isencrypted ) {
        return { cursor.skip_remaining(), mark };
    }

    /*
     * fs is at the first byte of the record body, and is IFLR. read and parse
     * the object name, then seek until the next logical record
     */

    /*
     * 12 is the minimum size of a segment (body, 16 with header), and often
     * enough to fully contain an object name. do this first, and only if this
     * is not enough, fall back to a more complicated reading. That read should
     * never fail
     *
     * TODO: constant for min-body-size?
     */
    std::array< char, 256 > body_buffer;
    cursor.read( body_buffer.data(), 12 );
    const auto* begin = body_buffer.data();
    const auto* xs = begin;

    std::int32_t origin;
    std::uint8_t copynum;
    std::uint8_t namelen;
    xs = dlis_uvari( xs, &origin );
    xs = dlis_ushort( xs, &copynum );
    xs = dlis_ushort( xs, &namelen );

    const auto intlen = std::distance( begin, xs );
    char* ptr = body_buffer.data() + 12;
    cursor.strlen = 12 - intlen;

    mark.name.origin = origin;
    mark.name.copy = copynum;

    /*
     * check that the obname isn't segmented, and if not, just read the
     * remaining bits of the obname
     */
    while( namelen > cursor.strlen ) {

        const auto count = std::min( namelen - cursor.strlen, cursor.seg.len );
        ptr = cursor.read( ptr, count );

        if( cursor.strlen == namelen )
            break;

        if( !cursor.has_successor ) {
            /*
             * for now, do nothing, but should raise a warning here that
             * the record is kinda broken
             */
        }

        /*
         * so this obname was segmented mid-record, so read the next segment
         * too (and more, if necessary). this can also span VRLs
         */
        cursor.next_visible();
        cursor.next_segment();
    }

    /* all good - complete the obname */
    mark.name.id.assign( xs, namelen );

    cursor.skip_remaining();
    return { cursor.remaining, mark };
}

}

#endif // DLISIO_PYTHON_IO_HPP
