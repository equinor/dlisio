#ifndef DLISIO_IO_HPP
#define DLISIO_IO_HPP

#include <array>
#include <string>
#include <tuple>
#include <vector>
#include <map>

#include <lfp/lfp.h>

#include <dlisio/stream.hpp>
#include <dlisio/types.hpp>
#include <dlisio/records.hpp>

namespace dl = dlisio::dlis;

namespace dlisio { namespace dlis {

struct stream_offsets {
    std::vector< long long > explicits;
    std::vector< long long > implicits;
    std::vector< long long > broken;
};

dlisio::stream open(const std::string&, std::int64_t) noexcept (false);
dlisio::stream open_rp66(const dlisio::stream&) noexcept (false);
dlisio::stream open_tapeimage(const dlisio::stream&) noexcept (false);

long long findsul(dlisio::stream&) noexcept (false);
long long findvrl(dlisio::stream&, long long) noexcept (false);
bool hastapemark(dlisio::stream&) noexcept (false);

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
