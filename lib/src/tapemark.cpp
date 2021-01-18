#include <cstring>

#include <dlisio/tapemark.hpp>
#include <dlisio/stream.hpp>
#include <dlisio/exception.hpp>

namespace dlisio {

bool valid_tapemark( const dlisio::tapemark& tm ) noexcept (false) {
    if ( tm.type != 0 and tm.type != 1 ) return false;
    if ( tm.prev >= tm.next  )           return false;

    return true;
}

tapemark parse_tapemark( const char* xs ) noexcept (true) {

    #ifdef HOST_BIG_ENDIAN
        char tmp[ dlisio::tapemark::size ];
        std::memcpy(tmp, xs, dlisio::tapemark::size);

        std::reverse(tmp + 0, tmp + 4);
        std::reverse(tmp + 4, tmp + 8);
        std::reverse(tmp + 8, tmp + 12);
        xs = tmp;
    #endif

    tapemark tm;
    std::memcpy(&tm.type, xs + 0, 4);
    std::memcpy(&tm.prev, xs + 4, 4);
    std::memcpy(&tm.next, xs + 8, 4);
    return tm;
}

tapemark read_tapemark( dlisio::stream& f ) noexcept (false) {
    char buffer[ dlisio::tapemark::size ];

    std::int64_t nread = f.read( buffer, dlisio::tapemark::size );

    if ( nread < dlisio::tapemark::size and f.eof() ) {
        const auto msg = "dlisio::read_tapemark: could not read enough bytes "
                         "from disk before hitting EOF";
        throw dlisio::eof_error(msg);
    }
    else if ( nread < dlisio::tapemark::size ) {
        const auto msg = "dlisio::read_tapemark: could not read enough bytes "
                         "from disk";
        throw dlisio::io_error(msg);
    }

    return parse_tapemark( buffer );
}

} // namespace dlisio
