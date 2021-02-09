#ifndef DLISIO_TAPEMARK_HPP
#define DLISIO_TAPEMARK_HPP

#include <dlisio/stream.hpp>

/** tapemark.hpp - Tape Image Format
 *
 * dlisio uses Layered File Protocols (LFP) as its io-device. Thanks to lfp,
 * dlisio does not need to concern itself with tapemarks and the Tape Image
 * Format.
 *
 * However, lfp does not provide any tooling for determining if a file has
 * tapemarks. The following utilities are used to determine just that, so
 * dlisio can set up a correct stack of LFP protocols.
 */
namespace dlisio {

struct tapemark {
    std::uint32_t type;
    std::uint32_t prev;
    std::uint32_t next;

    static constexpr const int size = 12;
};

tapemark parse_tapemark( const char* ) noexcept (true);
tapemark read_tapemark( dlisio::stream& ) noexcept (false);
bool valid_tapemark( const tapemark& ) noexcept (true);

} // namespace dlisio

#endif // DLISIO_TAPEMARK_HPP
