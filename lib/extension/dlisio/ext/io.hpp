#ifndef DLISIO_PYTHON_IO_HPP
#define DLISIO_PYTHON_IO_HPP

#include <array>
#include <string>
#include <tuple>
#include <vector>

#include <lfp/lfp.h>

#include <dlisio/ext/types.hpp>

namespace dl {


/*
 * Explicitly make the custom exceptions visible, otherwise they can be
 * considered different symbols in parse.cpp and in the python extension,
 * making exception translation impossible.
 *
 * https://github.com/pybind/pybind11/issues/1272
 */

struct DLISIO_API eof_error : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

struct DLISIO_API io_error : public std::runtime_error {
    using std::runtime_error::runtime_error;
    explicit io_error( int no ) : runtime_error( std::strerror( no ) ) {}
};

struct record {
    bool isexplicit()  const noexcept (true);
    bool isencrypted() const noexcept (true);

    int type;
    std::uint8_t attributes;
    bool consistent;
    std::vector< char > data;
};

/* Stream - wrapper for lfp_protocol
 *
 * The main purpose of stream is to handle lfp return codes in a manner that
 * suits dlisio and make a more ergonomic interface for caller functions.
 */
class stream {
public:
    explicit stream( lfp_protocol* p ) noexcept (false);

    void close();
    int eof() const noexcept (true);
    lfp_protocol* protocol() const noexcept (true);

    void seek( std::int64_t offset ) noexcept (false);
    std::int64_t tell() const noexcept(true);
    std::int64_t absolute_tell() const noexcept(false);

    std::int64_t read( char* dst, int n ) noexcept (false);

private:
    lfp_protocol* f;
};


struct stream_offsets {
    std::vector< index_entry > explicits;
    std::vector< index_entry > implicits;
};

stream open(const std::string&, std::int64_t) noexcept (false);
stream open_rp66(const stream&) noexcept (false);
stream open_tapeimage(const stream&) noexcept (false);

long long findsul(stream&) noexcept (false);
long long findvrl(stream&, long long) noexcept (false);
bool hastapemark(stream&) noexcept (false);

record extract(stream&, long long) noexcept (false);
record& extract(stream&, long long, long long, record&) noexcept (false);

dl::stream_offsets findoffsets(dl::stream&) noexcept (false);

std::vector< std::pair< std::string, long long > >
findfdata(dl::stream&, const std::vector< long long >&) noexcept (false);

}

#endif // DLISIO_PYTHON_IO_HPP
