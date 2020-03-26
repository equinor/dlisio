#include <algorithm>
#include <cerrno>
#include <ciso646>
#include <string>
#include <system_error>
#include <vector>

#include <fmt/core.h>
#include <fmt/format.h>
#include <mio/mio.hpp>
#include <lfp/lfp.h>
#include <lfp/rp66.h>

#include <dlisio/dlisio.h>
#include <dlisio/types.h>

#include <dlisio/ext/io.hpp>

namespace dl {

stream open(const std::string& path, std::int64_t offset) noexcept (false) {
    auto* file = std::fopen(path.c_str(), "rb");
    auto* protocol = lfp_cfile(file);
    if ( protocol == nullptr  )
        throw io_error("lfp: unable to open lfp protocol cfile");

    auto err = lfp_seek(protocol, offset);
    switch (err) {
            case LFP_OK: break;
            default:
                throw io_error(lfp_errormsg(protocol));
        }
    return stream(protocol);
}

stream open_rp66(const stream& f) noexcept (false) {
    auto* protocol = lfp_rp66_open(f.protocol());
    if ( protocol == nullptr ) {
        if ( lfp_eof(f.protocol()) )
            throw eof_error("lfp: cannot open file past eof");
        else
            throw io_error("lfp: unable to apply rp66 protocol");
    }

    return stream(protocol);
}

void map_source( mio::mmap_source& file, const std::string& path ) noexcept (false) {
    std::error_code syserror;
    file.map( path, 0, mio::map_entire_file, syserror );
    if (syserror) throw std::system_error( syserror );

    if (file.size() == 0)
        throw std::invalid_argument( "non-existent or empty file" );
}

void unmap( mio::mmap_source& file ) noexcept (false) {
    file.unmap();
}

long long findsul( stream& file ) noexcept (false) {
    long long offset;

    char buffer[ 200 ];
    file.seek(0);
    auto bytes_read = file.read(buffer, 200);

    const auto err = dlis_find_sul(buffer, bytes_read, &offset);

    switch (err) {
        case DLIS_OK:
            return offset;

        case DLIS_NOTFOUND: {
            auto msg = "searched {} bytes, but could not find storage label";
            throw dl::not_found(fmt::format(msg, bytes_read));
        }

        case DLIS_INCONSISTENT: {
            auto msg = "found something that could be parts of a SUL, "
                       "file may be corrupted";
            throw std::runtime_error(msg);
        }

        default:
            throw std::runtime_error("dlis_find_sul: unknown error");
    }
}

long long findvrl( stream& file, long long from ) noexcept (false) {
    if (from < 0) {
        const auto msg = "expected from (which is {}) >= 0";
        throw std::out_of_range(fmt::format(msg, from));
    }

    long long offset;

    char buffer[ 200 ];
    file.seek(from);
    auto bytes_read = file.read(buffer, 200);
    const auto err = dlis_find_vrl(buffer, bytes_read, &offset);

    // TODO: error messages could maybe be pulled from core library
    switch (err) {
        case DLIS_OK:
            return from + offset;

        case DLIS_NOTFOUND: {
            const auto msg = "searched {} bytes, but could not find "
                             "visible record envelope pattern [0xFF 0x01]"
            ;
            throw dl::not_found(fmt::format(msg, bytes_read));
        }

        case DLIS_INCONSISTENT: {
            const auto msg = "found [0xFF 0x01] but len field not intact, "
                             "file may be corrupted";
            throw std::runtime_error(msg);
        }

        default:
            throw std::runtime_error("dlis_find_vrl: unknown error");
    }
}

bool record::isexplicit() const noexcept (true) {
    return this->attributes & DLIS_SEGATTR_EXFMTLR;
}

bool record::isencrypted() const noexcept (true) {
    return this->attributes & DLIS_SEGATTR_ENCRYPT;
}

namespace {

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

void trim_segment(std::uint8_t attrs,
                  const char* begin,
                  int segment_size,
                  std::vector< char >& segment)
noexcept (false) {
    int trim = 0;
    const auto* end = begin + segment_size;
    const auto err = dlis_trim_record_segment(attrs, begin, end, &trim);

    switch (err) {
        case DLIS_OK:
            segment.resize(segment.size() - trim);
            return;

        case DLIS_BAD_SIZE:
            if (trim - segment_size != DLIS_LRSH_SIZE) {
                const auto msg =
                    "bad segment trim: padbytes (which is {}) "
                    ">= segment.size() (which is {})";
                throw std::runtime_error(fmt::format(msg, trim, segment_size));
            }

            /*
             * padbytes included the segment header. It's larger than
             * the segment body, but only because it also counts the
             * header. accept that, pretend the body was never added,
             * and move on.
             */
            segment.resize(segment.size() - segment_size);
            return;

        default:
            throw std::invalid_argument("dlis_trim_record_segment");
    }
}

}

stream::stream( lfp_protocol* f ) noexcept (false){
    this->f = f;
}

void stream::close() {
    lfp_close(this->f);
}

lfp_protocol* stream::protocol() const noexcept (true) {
    return this->f;
}

int stream::eof() const noexcept (true) {
    return lfp_eof(this->f);
}

void stream::seek( std::int64_t offset ) noexcept (false) {
    const auto err = lfp_seek(this->f, offset);
    switch (err) {
        case LFP_OK:
            break;
        case LFP_INVALID_ARGS:
        case LFP_NOTIMPLEMENTED:
        default:
            throw std::runtime_error(lfp_errormsg( this->f ));
    }
}

std::int64_t stream::tell() const noexcept (true) {
    std::int64_t tell;
    lfp_tell(this->f, &tell);
    return tell;
}

std::int64_t stream::absolute_tell() const noexcept (false) {
    auto* outer = this->f;
    lfp_protocol* inner;

    while (true) {
        auto err = lfp_peek(outer, &inner);
        switch (err) {
            case LFP_OK:
                break;
            case LFP_LEAF_PROTOCOL:
                /*
                 * lfp_peek is not implemented for LEAF protocols
                 *
                 * We use this fact as an implicit check that we have reached the
                 * inner-most protocol.
                 */
                std::int64_t tell;
                lfp_tell(outer, &tell);
                return tell;
            case LFP_IOERROR:
            default:
                throw std::runtime_error(lfp_errormsg(outer));
        }
        outer = inner;
    }
}

std::int64_t stream::read( char* dst, int n )
noexcept (false) {
    std::int64_t nread = -1;
    const auto err = lfp_readinto(this->f, dst, n, &nread);
    switch (err) {
        case LFP_OK:
        case LFP_EOF:
            break;
        case LFP_OKINCOMPLETE:
        case LFP_UNEXPECTED_EOF:
        default:
            throw std::runtime_error(lfp_errormsg(this->f));
    }
    return nread;
}

/*
 * store attributes in a string to use the short-string optimisation if
 * available. Just before commit, these are checked for consistency, i.e.
 * that segments don't report inconsistent information on encryption and
 * formatting.
 */
template < typename T >
using shortvec = std::basic_string< T >;


record extract(stream& file, long long tell) noexcept (false) {
    record rec;
    rec.data.reserve( 8192 );
    auto nbytes = std::numeric_limits< std::int64_t >::max();
    return extract(file, tell, nbytes, rec);
}

record& extract(stream& file, long long tell, long long bytes, record& rec) noexcept (false) {
    shortvec< std::uint8_t > attributes;
    shortvec< int > types;
    bool consistent = true;

    rec.data.clear();
    file.seek(tell);

    while (true) {
        char buffer[ DLIS_LRSH_SIZE ];
        auto nread = file.read( buffer, DLIS_LRSH_SIZE );
        if ( nread < DLIS_LRSH_SIZE )
            throw std::runtime_error("extract: unable to read LRSH, file truncated");

        int len, type;
        std::uint8_t attrs;
        dlis_lrsh( buffer, &len, &attrs, &type );

        len -= DLIS_LRSH_SIZE;

        attributes.push_back( attrs );
        types.push_back( type );

        const long long prevsize = rec.data.size();
        const auto remaining = bytes - prevsize;

        auto to_read = len;
        /*
         * If the remaining bytes-to-read is less than the full LRS, we
         * can get away with reading a partial LRS as long as there is no
         * padding, checksum or trailing length.
         */
        if ( not (attrs & DLIS_SEGATTR_PADDING) and
             not (attrs & DLIS_SEGATTR_TRAILEN) and
             not (attrs & DLIS_SEGATTR_CHCKSUM) and
             remaining < len ) {

            to_read = remaining;
        }

        rec.data.resize( prevsize + to_read );

        nread = file.read(rec.data.data() + prevsize, to_read);
        if ( nread < to_read )
            throw std::runtime_error("extract: unable to read LRS, file truncated");

        /*
         * chop off trailing length and checksum for now
         * TODO: verify integrity by checking trailing length
         * TODO: calculate checksum
         */

        const auto* fst = rec.data.data() + prevsize;
        trim_segment(attrs, fst, len, rec.data);

        /* if the whole segment is getting trimmed, it's unclear if successor
         * attribute should be erased or not.  For now ignoring.  Suspecting
         * issue will never occur as whole "too many padbytes" problem might be
         * caused by encryption
         */

        const auto has_successor = attrs & DLIS_SEGATTR_SUCCSEG;
        const long long bytes_left = bytes - rec.data.size();
        if (has_successor and bytes_left > 0) continue;

        /*
         * The record type only cares about encryption and formatting, so only
         * extract those for checking consistency. Nothing else is interesting
         * to users, as it only describes how to read this specific segment
         */
        static const auto fmtenc = DLIS_SEGATTR_EXFMTLR | DLIS_SEGATTR_ENCRYPT;
        rec.attributes = attributes.front() & fmtenc;
        rec.type = types.front();

        rec.consistent = consistent;
        if (not attr_consistent( attributes )) rec.consistent = false;
        if (not type_consistent( types ))      rec.consistent = false;
        if (bytes_left < 0) rec.data.resize(bytes);
        return rec;
    }
}

stream_offsets findoffsets( dl::stream& file) noexcept (false) {
    stream_offsets ofs;

    std::int64_t offset = 0;
    char buffer[ DLIS_LRSH_SIZE ];

    int len = 0;
    while (true) {
        file.seek(offset);
        file.read(buffer, DLIS_LRSH_SIZE);
        if (file.eof())
            break;

        int type;
        std::uint8_t attrs;
        dlis_lrsh( buffer, &len, &attrs, &type );

        int isexplicit = attrs & DLIS_SEGATTR_EXFMTLR;
        if (not (attrs & DLIS_SEGATTR_PREDSEG)) {
            if (isexplicit and type == 0 and ofs.explicits.size()) {
                /*
                 * Wrap up when we encounter a EFLR of type FILE-HEADER that is
                 * NOT the first Logical Record. More precisely we expect the
                 * _first_ LR we encounter to be a FILE-HEADER. We gather up
                 * this LR and all successive LR's until we encounter another
                 * FILE-HEADER.
                 */
                file.seek( offset );
                break;
            }
            if (isexplicit) ofs.explicits.push_back( offset );
            /*
             * Consider doing fdata-indexing on the fly as we are now at the
             * correct offset to read the OBNAME. That would mean we only need
             * to traverse the file a single time to index it. Additionally it
             * would make the caller code from python way nicer.
             */
            else            ofs.implicits.push_back( offset );
        }
        offset += len;
    }
    return ofs;
}

std::vector< std::pair< std::string, long long > >
findfdata(dl::stream& file, const std::vector< long long >& tells)
noexcept (false) {
    std::vector< std::pair< std::string, long long > > xs;

    constexpr std::size_t OBNAME_SIZE_MAX = 262;

    record rec;
    rec.data.reserve( OBNAME_SIZE_MAX );

    for (auto tell : tells) {
        extract(file, tell, OBNAME_SIZE_MAX, rec);
        if (rec.isencrypted()) continue;
        if (rec.type != 0) continue;

        int32_t origin;
        uint8_t copy;
        int32_t idlen;
        char id[ 256 ];
        const char* cur = dlis_obname(rec.data.data(), &origin, &copy, &idlen, id);

        std::size_t obname_size = cur - rec.data.data();
        if (obname_size > rec.data.size()) {
            auto msg = "File corrupted. Error on reading fdata obname";
            throw std::runtime_error(msg);
        }
        dl::obname tmp{ dl::origin{ origin },
                        dl::ushort{ copy },
                        dl::ident{ std::string{ id, id + idlen } } };
        xs.emplace_back(tmp.fingerprint("FRAME"), tell);
    }
    return xs;
}

}
