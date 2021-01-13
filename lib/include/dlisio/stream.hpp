#ifndef DLISIO_STREAM_HPP
#define DLISIO_STREAM_HPP

#include <cstdint>

#include <lfp/lfp.h>

namespace dl {

/* Stream - wrapper for lfp_protocol
 *
 * The main purpose of stream is to handle lfp return codes in a manner that
 * suits dlisio and make a more ergonomic interface for caller functions.
 */
class stream {
public:
    explicit stream( lfp_protocol* p ) noexcept (true) : f(p) {};

    void seek( std::int64_t offset ) noexcept (false);
    std::int64_t tell() const noexcept(true);
    std::int64_t absolute_tell() const noexcept(false);

    std::int64_t read( char* dst, int n ) noexcept (false);

    lfp_protocol* protocol() const noexcept (true);

    void close();
    int eof() const noexcept (true);
private:
    lfp_protocol* f;
};

}

#endif // DLISIO_STREAM_HPP
