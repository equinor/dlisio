#include <stdexcept>
#include <cstdint>

#include <lfp/lfp.h>

#include <dlisio/stream.hpp>

namespace dlisio {

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

std::int64_t stream::ltell() const noexcept (true) {
    std::int64_t tell;
    lfp_tell(this->f, &tell);
    return tell;
}

std::int64_t stream::ptell() const noexcept (false) {
    std::int64_t ptell;
    lfp_ptell(this->f, &ptell);
    return ptell;
}

std::int64_t stream::read( char* dst, int n )
noexcept (false) {
    if ( n == 0 ) return 0;
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

void stream::close() noexcept (true) {
    lfp_close(this->f);
}

int stream::eof() const noexcept (true) {
    return lfp_eof(this->f);
}

int stream::peof() const noexcept (false) {
    auto* outer = this->f;
    lfp_protocol* inner;

    while (true) {
        auto err = lfp_peek(outer, &inner);
        switch (err) {
            case LFP_OK:
                break;
            case LFP_LEAF_PROTOCOL:
                return lfp_eof(outer);
            case LFP_IOERROR:
            default:
                throw std::runtime_error(lfp_errormsg(outer));
        }
        outer = inner;
    }
}

} // namespace dlisio
