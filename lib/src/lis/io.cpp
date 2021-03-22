#include <ciso646>
#include <vector>
#include <string>
#include <cassert>
#include <numeric>

#include <lfp/lfp.h>
#include <lfp/tapeimage.h>

#include <fmt/core.h>
#include <fmt/format.h>

#include <dlisio/lis/protocol.hpp>
#include <dlisio/lis/io.hpp>
#include <dlisio/stream.hpp>
#include <dlisio/exception.hpp>

namespace dlisio { namespace lis79 {
namespace lis = dlisio::lis79;

/* range */
range::iterator range::begin() const noexcept (true) {
    return this->start;
}

range::iterator range::end() const noexcept (true) {
    return this->stop;
}

std::size_t range::size() const noexcept (true) {
    return std::distance( this->begin(), this->end() );
}


/* record_index */
std::size_t record_index::size() const noexcept (true) {
    return this->impls.size() + this->expls.size();
}

bool record_index::is_incomplete() const noexcept (true) {
    return this->incomplete;
}

const std::string& record_index::errmsg() const noexcept (true) {
    return this->err;
}

const std::vector< record_info >& record_index::explicits() const noexcept (true) {
    return this->expls;
}

const std::vector< record_info >& record_index::implicits() const noexcept (true) {
    return this->impls;
}

range record_index::implicits_of( const record_info& info ) const
noexcept (false) {
    return this->implicits_of( info.ltell );
}

range record_index::implicits_of( std::int64_t dfsr_tell ) const
noexcept (false) {
    // Find the actual DFS record in the index
    auto curr_dfsr = std::find_if( this->expls.begin(), this->expls.end(),
            [dfsr_tell](const record_info& cur) {
                return cur.ltell == dfsr_tell;
            }
    );

    if ( curr_dfsr == this->expls.end() ){
        const auto msg = "Could not find DFS record at tell {}";
        throw std::invalid_argument(fmt::format(msg, dfsr_tell));
    }

    // Find the next DFS record in the index, if any
    auto next_dfsr = std::find_if(std::next(curr_dfsr), this->expls.end(),
        [](const record_info& cur) {
            return cur.type == record_type::data_format_spec;
        }
    );

    auto lt = [](std::int64_t tell, const record_info& cur) {
        return tell < cur.ltell;
    };

    // Find the first implicit record after curr_dfsr
    auto begin = std::upper_bound(
                    this->impls.begin(),
                    this->impls.end(),
                    curr_dfsr->ltell,
                    lt
                );

    // Find the last implicit record before next_dfsr (or implicits.end())
    std::vector< record_info >::const_iterator end;
    if (next_dfsr < this->expls.end())
        end = std::upper_bound( begin, this->impls.end(), next_dfsr->ltell, lt );
    else
        end = this->impls.end();

    return lis::range(begin, end);
}


/* iodevice */
lis::prheader iodevice::read_physical_header() noexcept (false) {
    char buf[lis::prheader::size];

    /* Find and read the next PR header
     *
     * LIS allows for arbitrary padding between physical records. However, it
     * does not offer any information to whether or not such pad bytes are present,
     * nor how many padbytes one can expect. The spec states:
     *
     * > Physical Record Length (PRL) is a 16-bit, unsigned, binary integer
     *   that specifies the length, in bytes, of information in the Physical
     *   Record. This length, which includes the Physical Record Header and
     *   Trailer (if present), may be smaller than the actual number of bytes
     *   written-that is, a Physical Record may be padded with null characters
     *   to guarantee a minimum record size.
     *
     * Or shown graphically:
     *
     *                  unknown-
     *      PRH len     size        PRH len
     * |              |         |              |
     *  ---------------------------------------
     * | PRH | PRdata | padding | PRH | PRdata |
     *  ---------------------------------------
     *
     * Thus dlisio will have to seek for the next physical header. After
     * reading the first 4 bytes (PRH size), the first two bytes are inspected,
     * which we would normally believe to be the PR length. If these are *not*
     * null or space characters we assume no padding and simply parse the read
     * buffer as the next header. If both those bytes are null or space
     * characters, we are in padland:
     *
     * To be able to deal effectively with padding dlisio makes one key
     * assumption:
     *
     *    The next header, after the padding (if any) *always* start on a even
     *    tell that is divisible by 4 (PRH len).
     *
     *  To avoid any backwards seek we first check if the read buffer needs to
     *  be aligned with this criteria (as it is perfectly valid that the padding
     *  started on an uneven tell). If so, left-shift the bytes accordingly and
     *  read in the remaining bytes needed for full PRH buffer:
     *
     * tell     7      8
     *          |      |
     *      --------------------------------------------
     *     |... | null | null | null | null | null | ...|
     *      --------------------------------------------
     *          |   initially read buffer   |
     *                 |    aligned buffer         |
     *
     *
     * Then 4 bytes are read at the time until we find a new PRH or hit EOF.
     */

    // TODO measure the cost of large amount of padbytes between PR's as that
    //      will involved alot of small reads.
    // TODO move "find next PR" to it's own function?


    /* There are several reasons why the io might not be able to read as many
     * bytes as requested. Depending on the context it might mean that we are
     * at EOF, or that the file is truncated, or that io is blocked. This
     * function does a bit ceremony to establish the correct context and then
     * throws the appropriate error.
     */
    auto error = [this]( const char* buf, int bufsize, int nread ) {
        const auto where = "iodevice::read_physical_header: {}";
        if ( this->eof() and (nread == 0 or lis::is_padbytes(buf, bufsize)) ) {
            const auto what = "end-of-file";
            throw dlisio::eof_error( fmt::format( where, what ) );
        }

        else if ( this->eof() ) {
            // TODO This might be symptom of our alignment assumption
            //      being wrong. should inform about that somehow
            const auto what = "unexpected end-of-file";
            throw dlisio::truncation_error( fmt::format( where, what ) );
        }

        else {
            const auto what = "Unable to read from file";
            throw dlisio::io_error( fmt::format( where, what ) );
        }
    };

    auto nread = this->read(buf, lis::prheader::size);
    if ( nread < lis::prheader::size ) {
        error( buf, nread, nread );
    }

    /* Check if the first two bytes - which we believe to be the prh length
     * are in fact a valid length, or padbytes */
    if ( lis::is_padbytes( buf, 2 ) ) {
        auto alignment = this->ptell() % lis::prheader::size;

        /* Reposition the buffer if necessary */
        if ( alignment ) {
            int padbytes = lis::prheader::size - alignment;
            char tmp[lis::prheader::size];
            std::memcpy(tmp, buf + padbytes, alignment );

            nread = this->read(tmp + alignment, padbytes);
            if ( nread < padbytes )
                error( tmp, alignment + nread, nread );

            std::memcpy(buf, tmp, lis::prheader::size);
        }

        // Read 4 bytes at the time until a new PRH is found or EOF is hit
        while (true) {
            if ( not lis::is_padbytes( buf, lis::prheader::size ) ) break;

            nread = this->read(buf, lis::prheader::size);
            if ( nread < lis::prheader::size )
                error( buf, nread, nread );
        }
    }

    const auto head = lis::read_prh(buf);

    /* Minimum valid length (mvl) depends on whether this is the first PR in a
     * series of assosiated PR's or not and on the the optional Physical Record
     * Traielr. The first PR must contain a LR, while the remaining PR's have
     * no requirements w.r.t. content - and hence length.
     *
     *  - mvl for the first heade: PRH size + LRH size + PRT size
     *  - mvl for other PR's: PRH + PRT size
     */
    std::size_t mvl = (head.attributes & lis::prheader::predces) ? 4 : 6;

    if ( head.attributes & lis::prheader::reconum ) mvl += 2;
    if ( head.attributes & lis::prheader::filenum ) mvl += 2;
    if ( head.attributes & lis::prheader::chcksum ) mvl += 2;

    if ( head.length < mvl ) {
        std::string where = "iodevice::read_physical_header: ";
        std::string what  = "Too short record length (was {} bytes)";
        throw std::runtime_error(where + fmt::format(what, head.length));
    }

    return head;
}

lis::lrheader iodevice::read_logical_header() noexcept (false) {
    char buf[lis::lrheader::size];

    auto nread = this->read(buf, lis::lrheader::size);

    if (nread == 0 and this->eof()) {
        throw dlisio::eof_error("iodevice::read_logical_header: "
                                "unexpected end-of-file");
    } else if (nread < lis::lrheader::size){
        throw dlisio::io_error("iodevice::read_logical_header: "
                               "could not read full header from disk");
    }
    return lis::read_lrh(buf);
}

namespace {

/*
 * store attributes in a string to use the short-string optimisation if
 * available. Just before commit, these are checked for consistency, i.e.
 * that PRHs don't report inconsistent information.
 */
template < typename T >
using shortvec = std::basic_string< T >;

bool attr_consistent( const shortvec<std::uint16_t>& attrs ) noexcept (true) {
    /* For attributes to be considered consistent across all PRHs in a
     * record, the following needs to hold:
     *
     *  1) the predecessor bit should be set in all PRHs but the first
     *  2) the successor bit should be set in all PRHs but the last
     *
     *      PRH   predecessor  successor
     *      0          0            1
     *      1          1            1
     *      ..
     *      n - 1      1            1
     *      n          1            0
     *
     */
    if (attrs.size() == 0) return true;
    if (attrs.size() == 1) {
        const auto attr = attrs.at(0);
        return not (attr & lis::prheader::succses) and
               not (attr & lis::prheader::predces);
    }

    /* This lambda is a bit convoluted - but it accomplishes the
     * (in)consistency checking, for both attributes with a single iteration.
     *
     * For predecessor and successor we use the fact that the lambda is called
     * with pair-wise elements like so, which means we have an easy check for
     * all the '1' bits:
     *
     * n =  [attrs.begin(),     attrs.end() - 1) and
     * n1 = [attrs.begin() + 1, attrs.end)
     *
     * The first predecessor and last successor, which should be 0, needs special
     * care.
     */
    std::size_t pos  = 0;
    std::size_t size = attrs.size() - 1;

    auto inconsistent = [pos, size](const std::uint16_t& n,
                                    const std::uint16_t& n1) mutable {
        if (pos++ == 0    and n  & lis::prheader::predces) return true;
        if (pos   == size and n1 & lis::prheader::succses) return true;
        return not (n & lis::prheader::succses) or
               not (n1 & lis::prheader::predces);
    };

    return std::adjacent_find(attrs.begin(),
                              attrs.end(),
                              inconsistent) == attrs.end();
}

} // namespace

lis::record_info iodevice::index_record() noexcept (false) {
    shortvec< std::uint16_t > attributes;

    /* There is no explicitly defined "last" record in a logical file.
     *
     * A logical file is terminated when an exhausted record is followed by
     * EOF. Hence hitting EOF when trying to read the *next* record is a valid
     * termination of the file.
     *
     * Note that recording the logical tell _after_ reading the PRH here is
     * important. This is to ensure a correct ltell regardless of the presence
     * of padbytes.
     */
    auto prh = this->read_physical_header();
    std::int64_t ltell = this->ltell() - lis::prheader::size;

    std::size_t length = prh.length;
    attributes.push_back( prh.attributes );

    lis::lrheader lrh;
    try {
        lrh = this->read_logical_header();
    } catch( const dlisio::eof_error& e ) {
        const auto msg =  "iodevice::index_record: {}";
        throw dlisio::truncation_error( fmt::format(msg, e.what()) );
    } catch( const dlisio::io_error& e ) {
        const auto msg =  "iodevice::index_record: {}";
        throw dlisio::truncation_error( fmt::format(msg, e.what()) );
    }

    if ( not lis::valid_rectype( lrh.type ) ) {
        /* There is really no way of telling if the LRH is zero'd out, as 0 is
        * valid record_type and the second byte is undefined.
        *
        * Thus we rely on a fully zero'd out record to be caught elsewhere.
        */
        const auto msg = "iodevice::index_record: "
                         "Found invalid record type ({}) when reading "
                         "header at ptell ({})";
        const auto tell = this->ptell() - lis::lrheader::size;
        throw std::runtime_error(fmt::format( msg, lis::decay(lrh.type), tell));
    }

    while ( true ) {
        // TODO Should consider to read the PR trailer too - and possible
        //      include in index
        if ( not (prh.attributes & lis::prheader::succses) ) {
            /* Before returning, verify that the record is not truncated
             * by attempting to read the last byte in the record.
             */
            char tmp;
            this->seek( ltell + length - 1 );
            this->read( &tmp, 1 );

            if ( this->eof() ) {
                const auto msg = "iodevice::index_record: "
                                 "physical record truncated";
                throw dlisio::truncation_error( msg );
            }

            break;
        }

        this->seek(ltell + length);

        try {
            prh = this->read_physical_header();
            length += prh.length;
            attributes.push_back( prh.attributes );
        } catch( const dlisio::eof_error& e ) {
            const auto msg = "iodevice::index_record: Missing next PRH. ({})";
            throw dlisio::truncation_error( fmt::format(msg, e.what()) );
        }
    }

    if (not attr_consistent( attributes )) {
        const auto msg = "iodevice::index_record: "
                         "predecessor/successor inconsistency";
        throw std::runtime_error(msg);
    }

    record_info info;
    info.type  = static_cast< lis::record_type >(lis::decay(lrh.type));
    info.size  = length;
    info.ltell = ltell;

    return info;
}

namespace {


} // namespace

record_index iodevice::index_records() noexcept (true) {
    std::vector< record_info > ex;
    std::vector< record_info > im;
    bool incomplete = false;
    auto err = std::string{};

    lis::record_info info;

    /* Essentially seek past potential pad-bytes after the record.
     *
     * This leaves the tell after termination of this function on
     * the start of the next record - or at EOF. That is useful for
     * caller code that often would want to open a new file-handle
     * and keep indexing the file from this tell.
     *
     * TODO: This hack can go away if we decouple the
     *       "seek_past_padding"-logic from read_physical_header
     */
    const auto reposition_tell = [this](){
        try {
            auto nextinfo = this->index_record();
            this->seek(nextinfo.ltell);
        } catch ( const std::exception& ) {
            /* Ignore any errors.
            *
            * If we hit EOF, we achieved what we wanted w.r.t. the tell.
            * Any other errors will be the problem of the next "LF".
            */
        }
    };

    while (true) {
        try {
            info = this->index_record();
        } catch( const dlisio::eof_error& e ) {
            /* For well-formatted files, the last byte of the last PR perfectly
             * aligns with EOF. Our underlying IO device (rightly so) does not
             * report EOF until we try to read _past_ the last byte.
             */
            break;
        } catch ( const std::exception& e ) {
            err = e.what();
            incomplete = true;
            break;
        }

        if (info.type == lis::record_type::normal_data or
            info.type == lis::record_type::alternate_data) {
            im.push_back( info );
        } else {
            ex.push_back( info );
        }

        switch (info.type) {
            case lis::record_type::reel_header:
            case lis::record_type::reel_trailer:
            case lis::record_type::tape_header:
            case lis::record_type::tape_trailer: {
                /* Reel and Tape records are index separately. If this is not
                 * the _first_ record in the index, pop it off and rewind. This
                 * typically happens then the FTLR is missing.
                 */
                if ( ex.size() > 1 ) {
                    this->seek(info.ltell);
                    ex.pop_back();
                } else {
                    reposition_tell();
                }
                break;
            }
            case lis::record_type::file_header: {
                /* Continue indexing if this is the first record. If not,
                 * there is probably a missing File Trailer record and we have
                 * moved into the next LF.
                 */
                if ( ex.size() == 1 ) {
                    continue;
                }
                this->seek(info.ltell);
                ex.pop_back();
                break;
            }
            case lis::record_type::logical_eof:
            case lis::record_type::file_trailer: {
                reposition_tell();
                break;
            }

            default:
                /* Continue indexing more records */
                continue;
        }

        break;
    }

    return record_index(std::move(ex), std::move(im), incomplete, std::move(err));
}

record iodevice::read_record(const record_info& info) noexcept (false) {
    record rec;
    rec.info = info; // Copy the headerinfo

    this->seek(rec.info.ltell);
    std::int64_t prevlen = 0;

    while (true) {
        const auto prh = this->read_physical_header();

        std::uint8_t trlen = 0;
        if ( prh.attributes & lis::prheader::reconum ) trlen += 2;
        if ( prh.attributes & lis::prheader::filenum ) trlen += 2;
        if ( prh.attributes & lis::prheader::chcksum ) trlen += 2;

        /* LRs spanning multiple PRs: The LRH is only present in the first PRH,
         * i.e. when the predecessor attribute is not set. The LRH is already
         * read, and is a part of record_info, so just skip past it.
         */
        std::int64_t toread = prh.length - lis::prheader::size - trlen;
        if ( not (prh.attributes & lis::prheader::predces) ) {
            this->seek(this->ltell() + lis::lrheader::size);
            toread -= lis::lrheader::size;
        }

        rec.data.resize(rec.data.size() + toread);

        auto nread = this->read(rec.data.data() + prevlen, toread);

        if (nread < toread) {
            throw dlisio::io_error("iodevice::read_record: record truncated");
        }

        /* Skip past trailer(s) */
        if (trlen) this->seek(this->ltell() + trlen);

        prevlen += toread;

        if ( not (prh.attributes & lis::prheader::succses) ) break;
    }
    return rec;
}


/* miscellaneous */
iodevice open( const std::string& path, std::int64_t offset, bool tapeimage )
noexcept (false) {
    auto* file = std::fopen(path.c_str(), "rb");
    if ( not file ) {
        auto msg = "lis::open: unable to open file for path {} : {}";
        throw dlisio::io_error(fmt::format(msg, path, strerror(errno)));
    }

    auto* protocol = lfp_cfile_open_at_offset(file, offset);
    if ( protocol == nullptr ) {
        std::fclose(file);
        const auto msg = "lis::open: "
                         "unable to open lfp protocol cfile at tell {}";
        throw dlisio::io_error(fmt::format(msg, offset));
    }

    if ( tapeimage ) {
        auto* tif = lfp_tapeimage_open(protocol);
        if ( tif == nullptr ) {
            lfp_close( protocol );
            throw dlisio::io_error("lis::open: "
                                   "unable to open lfp protocol tapeimage");
        }
        protocol = tif;
    }

    auto device = iodevice( protocol );

    /* Verify that the device is not opened at EOF by attempting to read one byte */
    try {
        char tmp;
        device.read(&tmp, 1);
    } catch ( const std::exception& e ) {
        device.close();
        const auto msg = "lis::open: "
                            "Cannot open lis::iodevice (ptell={}): {}";
        throw dlisio::io_error( fmt::format(msg, offset, e.what() ));
    }

    if ( device.eof() ) {
        device.close();
        const auto msg = "open: handle is opened at EOF (ptell={})";
        throw dlisio::eof_error( fmt::format(msg, offset) );
    }

    try {
        device.seek( 0 );
    } catch ( const std::exception& e ) {
        device.close();
        const auto msg = "lis::open: "
                         "Could not rewind lis::iodevice to ptell {}: {}";
        throw dlisio::io_error( fmt::format(msg, offset, e.what()) );
    }

    return device;
}

} // namespace lis79

} // namespace dlisio

