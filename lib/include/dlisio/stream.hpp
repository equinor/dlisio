#ifndef DLISIO_STREAM_HPP
#define DLISIO_STREAM_HPP

#include <cstdint>

#include <lfp/lfp.h>

namespace dl {

/* Stream - C++ wrapper for lfp's API.
 *
 * The main purpose of stream is to wrap lfp's C API into something more
 * C++-ish. lfp return codes are translated into exceptions. All functions
 * except ptell work on the logical file as presented by the current
 * lfp_protocol. E.g. take a stream-instance with the protocol stack lfp_cfile,
 * lfp_tapeimage and lfp_rp66 opened on a dlis-file. This stream will only
 * "see" bytes corresponding to the Logical Record Segments. I.e. the file will
 * look like a series of LRS from start to finish. All bytes corresponding to
 * tapemarks or the visible envelope are abstracted away.
 */
class stream {
public:
    explicit stream( lfp_protocol* p ) noexcept (true) : f(p) {};

    void seek( std::int64_t offset ) noexcept (false);

    /** Physical tell
     *
     * The tell reported by the inner-most lfp_protocol. I.e. the actual number
     * of bytes into the file as the file is seen on disk */
    std::int64_t ptell() const noexcept(false);

    /** Logical tell
     *
     * logical tell is the tell reported by current (outer-most) lfp_protocol.
     *
     * Example
     * -------
     *
     * A file as seen on disk
     *
     *                                           (EOF)
     * byte offset      0    100      300   400   500
     *                   --------------------------
     *                  | ... | header | ... | ... |
     *                   --------------------------
     *                        ^                 ^
     *                        |                 |
     *                  lfp_protocol         current
     *                     opened            position
     *                      here             in file
     *
     * In the above example the current protocol was opened at ptell=100 and
     * the 200 bytes corresponding to some header are abstracted away by the
     * lfp_protocol*. The current position (offset) in the file is as marked.
     * In this case ltell == 150 and ptell == 450.
     */
    std::int64_t ltell() const noexcept(true);

    std::int64_t read( char* dst, int n ) noexcept (false);

    /* return a pointer to the current lfp_protocol */
    lfp_protocol* protocol() const noexcept (true);

    void close() noexcept (true);
    int eof() const noexcept (true);
private:
    lfp_protocol* f;
};

}

#endif // DLISIO_STREAM_HPP
