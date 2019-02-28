#include <algorithm>
#include <cerrno>
#include <ciso646>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <system_error>
#include <vector>

#include <mio/mio.hpp>

#include <dlisio/dlisio.h>
#include <dlisio/types.h>

#include <dlisio/ext/io.hpp>

namespace dl {

void stream_offsets::resize( std::size_t n ) noexcept (false) {
    this->tells.resize( n );
    this->residuals.resize( n );
    this->explicits.resize( n );
}

void map_source( mio::mmap_source& file, const std::string& path ) noexcept (false) {
    std::error_code syserror;
    file.map( path, 0, mio::map_entire_file, syserror );
    if (syserror) throw std::system_error( syserror );

    if (file.size() == 0)
        throw std::invalid_argument( "non-existent or empty file" );
}

long long findsul( mio::mmap_source& file ) noexcept (false) {
    /*
     * search at most 200 bytes, looking for the SUL
     *
     * if it doesn't show up by then it's probably not there, or require other
     * information
     *
     * Return the offset of the _first byte_ of the SUL. In a conforming file,
     * this is 0.
     */
    static const auto needle = "RECORD";
    static const std::size_t search_limit = 200;

    const auto first = file.data();
    const auto last = first + (std::min)( file.size(), search_limit );
    auto itr = std::search( first, last, needle, needle + 6 );

    if (itr == last) {
        const std::string msg = "searched "
                              + std::to_string(search_limit)
                              + " bytes, but could not find SUL"
                              ;
        throw dl::not_found( msg );
    }

    /*
     * Before the structure field of the SUL there should be 10 bytes, i.e.
     * sequence-number and DLIS version.
     */
    const auto structure_offset = 9;

    if (std::distance( first, itr ) < structure_offset) {
        auto pos = std::distance( first, itr );
        const std::string msg = "found 'RECORD' at pos = "
                              + std::to_string( pos )
                              + ", but expected pos >= 10"
                              ;
        throw std::runtime_error( msg );
    }

    return std::distance( file.data(), itr - structure_offset );
}

long long findvrl( mio::mmap_source& file, long long from ) noexcept (false) {
    /*
     * The first VRL does sometimes not immediately follow the SUL (or whatever
     * came before it), but according to spec it should be a triple of
     * (len,0xFF,0x01), where len is a UNORM. The second half shouldn't change,
     * so look for the first occurence of that.
     *
     * If that too doesn't work then the file is likely too corrupted to read
     * without manual intervention
     */

    if (from < 0) {
        std::stringstream msg;
        msg << "from (which is " << from << ") >= 0";
        throw std::out_of_range(msg.str());
    }

    if (std::size_t(from) > file.size()) {
        std::stringstream msg;
        msg << "from (which is " << from << ") "
            << "<= file.size (which is " << file.size() << ")"
        ;
        throw std::out_of_range(msg.str());
    }

    static const unsigned char needle[] = { 0xFF, 0x01 };
    static const auto search_limit = 200;

    const auto limit = std::min< long long >(file.size() - from, search_limit);

    /*
     * reinterpret the bytes as usigned char*. This is compatible and fine.
     *
     * When operator == is ued on the elements, they'll otherwise be promoted
     * to int, so all of a sudden (char)0xFF != (unsigned char)0xFF. Forcing
     * the pointer to be unsigend char fixes this issue.
     */
    const auto front = reinterpret_cast< const unsigned char* >(file.data());
    const auto first = front + from;
    const auto last = first + limit;
    const auto itr = std::search(first, last, needle, needle + sizeof(needle));

    if (itr == last) {
        std::stringstream msg;
        msg << "searched " << limit << " bytes, but could not find VRL";
        throw dl::not_found( msg.str() );
    }

    /*
     * Before the 0xFF 0x01 there should be room for at least an unorm
     */
    if (std::distance( first, itr ) < DLIS_SIZEOF_UNORM) {
        auto pos = std::distance( first, itr );
        std::stringstream msg;
        msg << "found 0xFF 0x01 at pos = " << from + pos
            << ", but expected pos >= " << from + DLIS_SIZEOF_UNORM
        ;
        throw std::runtime_error(msg.str());
    }

    return std::distance(front, itr - DLIS_SIZEOF_UNORM);
}

stream_offsets findoffsets( mio::mmap_source& file, long long from )
noexcept (false)
{
    const auto* begin = file.data() + from;
    const auto* end = file.data() + file.size();

    // by default, assume ~4K per segment on average. This should be fairly few
    // reallocations, without overshooting too much
    std::size_t alloc_size = file.size() / 4196;

    stream_offsets ofs;
    ofs.resize( alloc_size );
    auto& tells     = ofs.tells;
    auto& residuals = ofs.residuals;
    auto& explicits = ofs.explicits;

    int err;
    const char* next;
    int count = 0;
    int initial_residual = 0;

    while (true) {
        err = dlis_index_records( begin,
                                  end,
                                  alloc_size,
                                  &initial_residual,
                                  &next,
                                  &count,
                                  count + tells.data(),
                                  count + residuals.data(),
                                  count + explicits.data() );

        if (err == DLIS_TRUNCATED)
            throw std::runtime_error( "file truncated" );

        if (err == DLIS_INCONSISTENT)
            throw std::runtime_error( "inconsistensies in record sizes" );

        if (err)
            throw std::runtime_error( "unknown error " + std::to_string( err ) );

        if (next == end) break;

        const auto prev_size = tells.size();
        ofs.resize( prev_size * 1.5 );


        /* size of the now trailing newly-allocated area */
        alloc_size = tells.size() - prev_size;
        begin = next;
    }

    ofs.resize( count );

    const auto dist = file.size();
    for (auto& tell : tells) tell += dist;

    return ofs;
}

bool record::isexplicit() const noexcept (true) {
    return this->attributes & DLIS_SEGATTR_EXFMTLR;
}

bool record::isencrypted() const noexcept (true) {
    return this->attributes & DLIS_SEGATTR_ENCRYPT;
}

stream::stream( const std::string& path ) noexcept (false)
{
    this->fs.exceptions( fs.exceptions()
                       | std::ios::eofbit
                       | std::ios::failbit
                       );

    this->fs.open( path, std::ios::binary | std::ios::in );

    if (!this->fs.good()) {
        std::stringstream msg;
        msg << "unable to open file: " << std::strerror(errno);
        throw std::invalid_argument( msg.str() );
    }
}

record stream::at( int i ) noexcept (false) {
    record r;
    r.data.reserve( 8192 );
    return this->at( i, r );
}

namespace {

bool consumed_record( long long tell,
                      const std::vector< long long >& tells,
                      int i ) noexcept (true) {
    /*
     * this was the last record, so have no idea how to determine that
     * everything is properly consumed. Always true
     */
    if (std::size_t(i) == tells.size() - 1) return true;

    return tell == tells[ i + 1 ];
}

template < typename T >
bool attr_consistent( const T& ) noexcept (true) {
    // TODO: implement
    // internal attributes should have both successor and predecessor
    // first only successors, last only predecessors
    return true;
}

template < typename T >
bool type_consistent( const T& ) noexcept (true) {
    // TODO: implement
    // should be all-equal
    return true;
}

}

/*
 * store attributes in a string to use the short-string optimisation if
 * available. Just before commit, these are checked for consistency, i.e.
 * that segments don't report inconsistent information on encryption and
 * formatting.
 */
template < typename T >
using shortvec = std::basic_string< T >;

record& stream::at( int i, record& rec ) noexcept (false) {

    auto tell = this->tells.at( i );
    auto remaining = this->residuals.at( i );

    shortvec< std::uint8_t > attributes;
    shortvec< int > types;
    bool consistent = true;

    this->fs.seekg( tell );

    const auto chop = []( std::vector< char >& vec, int bytes ) {
        vec.erase( vec.end() - bytes, vec.end() );
    };

    while (true) {
        while (remaining > 0) {
            int len, type;
            std::uint8_t attrs;
            char buffer[ DLIS_LRSH_SIZE ];
            this->fs.read( buffer, DLIS_LRSH_SIZE );
            const auto err = dlis_lrsh( buffer, &len, &attrs, &type );

            remaining -= len;
            len -= DLIS_LRSH_SIZE;

            if (err) consistent = false;
            attributes.push_back( attrs );

            int explicit_formatting = 0;
            int has_predecessor = 0;
            int has_successor = 0;
            int is_encrypted = 0;
            int has_encryption_packet = 0;
            int has_checksum = 0;
            int has_trailing_length = 0;
            int has_padding = 0;
            dlis_segment_attributes( attrs, &explicit_formatting,
                                            &has_predecessor,
                                            &has_successor,
                                            &is_encrypted,
                                            &has_encryption_packet,
                                            &has_checksum,
                                            &has_trailing_length,
                                            &has_padding );

            if (remaining < 0) {
                /*
                 * mismatch between visisble-record-length and segment length.
                 * For now, just throw, but this could be reduced to a warning
                 * with guide on which one to believe
                 */

                const auto vrl_len = remaining + len;
                const auto tell = std::int64_t(this->fs.tellg()) - DLIS_LRSH_SIZE;
                consistent = false;
                std::stringstream msg;
                msg << "visible record/segment inconsistency:"
                    << " segment (len = " << len << ")"
                    << " >= visible (len = " << vrl_len << ")"
                    << " record " << i
                    << " (tell = " << tell << ")"
                ;
                throw std::runtime_error( msg.str() );
            }

            const auto prevsize = rec.data.size();
            rec.data.resize( prevsize + len );
            this->fs.read( rec.data.data() + prevsize, len );

            /*
             * chop off trailing length and checksum for now
             * TODO: verify integrity by checking trailing length
             * TODO: calculate checksum
             */
            if (has_trailing_length) chop( rec.data, 2 );
            if (has_checksum)        chop( rec.data, 2 );
            if (has_padding) {
                std::uint8_t padcount = 0;
                const auto* pad = rec.data.data() + rec.data.size() - 1;
                dlis_ushort( pad, &padcount );
                chop( rec.data, padcount );
            }

            if (has_successor) continue;

            /* read last segment - check consistency and wrap up */
            if (this->contiguous and not consumed_record( this->fs.tellg(),
                                                          this->tells,
                                                          i )) {
                /*
                 * If this happens something is VERY wrong. Every new record
                 * should start just after the previous, unless bytes have been
                 * purposely skipped, because the file was otherwise broken.
                 * This probably comes from consistent, but lying, length
                 * attributes
                 */
                std::stringstream msg;
                msg << "non contiguous record: "
                    << "#" << i << " (tell = " << this->tells.at(i) << ")"
                    << " ends prematurely at " << this->fs.tellg()
                    << ", not at "
                    << "#" << i << " (tell = " << this->tells.at(i + 1) << ")"
                ;
                throw std::runtime_error( msg.str() );
            }


            /*
             * The record type only cares about encryption and formatting, so only
             * extract those for checking consistency. Nothing else is interesting to
             * users, as it only describes how to read this specific segment
             */
            static const auto fmtenc = DLIS_SEGATTR_EXFMTLR | DLIS_SEGATTR_ENCRYPT;
            rec.attributes = attributes.front() & fmtenc;
            rec.type = types.front();

            rec.consistent = consistent;
            if (not attr_consistent( attributes )) rec.consistent = false;
            if (not type_consistent( types ))      rec.consistent = false;
            return rec;
        }

        int len, version;
        char buffer[ DLIS_VRL_SIZE ];
        this->fs.read( buffer, DLIS_VRL_SIZE );
        const auto err = dlis_vrl( buffer, &len, &version );

        if (err) consistent = false;
        if (version != 1) consistent = false;

        remaining = len - DLIS_VRL_SIZE;
    }
}

void stream::reindex( std::vector< long long > tells,
                      std::vector< int > residuals ) noexcept (false) {
    if (tells.empty())
        throw std::invalid_argument( "tells must be non-empty" );

    if (residuals.empty())
        throw std::invalid_argument( "residuals must be non-empty" );

    if (tells.size() != residuals.size()) {
        // TODO: fmtlib
        throw std::invalid_argument( "indices must be same size" );
    }

    // TODO: assert all-positive etc.
    this->tells = tells;
    this->residuals = residuals;
}

void stream::close() {
    this->fs.close();
}

void stream::read( char* dst, long long offset, int n ) {
    if (n < 0) {
        std::stringstream msg;
        msg << "expected positive n >= 0 (was " << n << ")";
        throw std::invalid_argument( msg.str() );
    }

    if (offset < 0) {
        std::stringstream msg;
        msg << "expected offset >= 0 (was " << offset << ")";
        throw std::invalid_argument( msg.str() );
    }

    this->fs.seekg( offset );
    this->fs.read( dst, n );
}

}
