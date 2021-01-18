#ifndef DLISIO_TAPEMARK_HPP
#define DLISIO_TAPEMARK_HPP

#include <dlisio/stream.hpp>

namespace dlisio {

struct tapemark {
    std::uint32_t type;
    std::uint32_t prev;
    std::uint32_t next;

    static constexpr const int size = 12;
};

tapemark parse_tapemark( const char* ) noexcept (true);
tapemark read_tapemark( dlisio::stream& ) noexcept (false);
bool valid_tapemark( const tapemark& ) noexcept (false);

} // namespace dlisio

#endif // DLISIO_TAPEMARK_HPP
