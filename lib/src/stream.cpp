#include <stdexcept>
#include <cstdint>

#include <lfp/lfp.h>

#include <dlisio/stream.hpp>

namespace dl {

stream::stream( lfp_protocol* f ) noexcept (false){
    this->f = f;
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

lfp_protocol* stream::protocol() const noexcept (true) {
    return this->f;
}

void stream::close() {
    lfp_close(this->f);
}

int stream::eof() const noexcept (true) {
    return lfp_eof(this->f);
}

}
