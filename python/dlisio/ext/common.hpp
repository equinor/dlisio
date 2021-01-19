#ifndef DLISIO_EXT_COMMON
#define DLISIO_EXT_COMMON

#include <string>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace dlisio { namespace detail {

py::handle decode_str(const std::string& src) noexcept (false);

} // namespace detail

} // namespace dlisio

#endif // DLISIO_EXT_COMMON
