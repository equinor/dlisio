#ifndef DLISIO_IO_HPP
#define DLISIO_IO_HPP

#include <array>
#include <string>
#include <tuple>
#include <vector>
#include <map>

#include <lfp/lfp.h>

#include <dlisio/stream.hpp>
#include <dlisio/dlis/types.hpp>
#include <dlisio/dlis/records.hpp>

namespace dlisio { namespace dlis {

namespace dl = dlisio::dlis;

struct stream_offsets {
    std::vector< long long > explicits;
    std::vector< long long > implicits;
    std::vector< long long > broken;
};

dlisio::stream open(const std::string&, std::int64_t) noexcept (false);
dlisio::stream open_rp66(const dlisio::stream&) noexcept (false);
dlisio::stream open_tapeimage(const dlisio::stream&) noexcept (false);

/* Find SUL and position on it.
 *
 * Stream is expected to be positioned at the supposed SUL start.
 * Check will be performed in two steps. First, mininum amount of bytes that
 * should be enough to find SUL will be read and processed. If SUL is not found
 * in the first step, but is expected, then SUL is assumed to be late and in
 * second step maximum amount of bytes is read.
 *
 * If SUL is not found, RuntimeException is thrown.
 */
void findsul(dlisio::stream&, const dl::error_handler&, bool) noexcept(false);
long long findvrl(dlisio::stream&, long long) noexcept (false);

dl::record extract(dlisio::stream&, long long, dl::error_handler&) noexcept (false);
dl::record& extract(dlisio::stream&, long long, long long, dl::record&,
    dl::error_handler&) noexcept (false);

stream_offsets findoffsets(dlisio::stream&, dl::error_handler&) noexcept (false);

std::map< dl::ident, std::vector< long long > >
findfdata(dlisio::stream&, const std::vector< long long >&, dl::error_handler&)
noexcept (false);

} // namespace dlis

} // namespace dlisio

#endif // DLISIO_IO_HPP
