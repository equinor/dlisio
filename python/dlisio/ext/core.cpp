#include <exception>
#include <string>
#include <vector>

#include <mpark/variant.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include <pybind11/stl.h>
#include <datetime.h>

namespace py = pybind11;
using namespace py::literals;

namespace dlisio {
/*
 * Explicitly make the custom exceptions visible, by forward declarling them
 * with pybind's export macro. Otherwise they can be considered different
 * symbols in parse.cpp and in the python extension, making exception
 * translation impossible.
 *
 * https://github.com/pybind/pybind11/issues/1272
 */

struct PYBIND11_EXPORT io_error;
struct PYBIND11_EXPORT eof_error;
struct PYBIND11_EXPORT not_implemented;
struct PYBIND11_EXPORT not_found;
}

#include <dlisio/tapemark.hpp>
#include <dlisio/exception.hpp>
#include <dlisio/dlis/records.hpp>
#include <dlisio/lis/protocol.hpp>

#include "common.hpp"

namespace dl = dlisio::dlis;
namespace lis = dlisio::lis79;

namespace {
/*
 * Global list of encodings to try when making UTF-8 strings.
 *
 * The encodings are global, which is a result of the current design of dlisio.
 *
 * Ideally, what encodings to try should be configurable on a much finer level
 * - it's quite reasonable to have multiple files open, which both can have
 * different encodings used. In the future it's quite possible to fine tune it
 * more, but that requires a larger redesign of dlisio's internals.
 *
 * However, in practice the outcome of a global-only configuration is a minor
 * annoyance at best. DLIS only allows ASCII, so anything that isn't UTF-8
 * compatible is already non-standard, and it's unlikely there's a need for
 * opening *many files at once*, all with different encodings. Also, since the
 * global can be re-set between successive file loads, work-arounds are usually
 * possible.
 *
 * The main reason it has to be global is that strings are converted to python
 * strings pretty deep in the call graph, using pybind11's casting features.
 * The casts, however, are unary functions, so no extra parameters there.
 * Moreover, the compounded dlis types, like ATTREF, rely on the type cast
 * mechanism in order to convert its members to python types. To resolve this,
 * a major redesign is needed.
 */
std::vector< std::string > encodings = {};

void set_encodings(const std::vector< std::string >& encs) {
    encodings = encs;
}

const std::vector< std::string >& get_encodings() {
    return encodings;
}

} // namespace

namespace dlisio { namespace detail {
py::handle decode_str(const std::string& src) noexcept (false) {
    auto* p = PyUnicode_FromString(src.c_str());
    if (p) return p;
    PyErr_Clear();

    for (const auto& enc : encodings) {
        auto* p = PyUnicode_Decode(
                src.c_str(),
                src.size(),
                enc.c_str(),
                "strict"
            );

        if (p) return p;
        PyErr_Clear();
    }

    /*
     * To get a better warning, include the source string. The problem is that
     * the PyExc_WarnEx (warnings.warn() in python) tries to encode the string
     * to unicode, which is what triggers the warning in the first place,
     * meaning C++ string concatenation or stringstreams won't work.
     *
     * Instead, work around this by doing '{}'.format(bytes()) to get the
     * string-representation of the bytes.
     */
    auto pysrc = py::bytes(src);
    const auto pymsg = py::str("unable to decode string {}");
    const auto msg   = std::string(pymsg.format(pysrc));
    if (PyErr_WarnEx(PyExc_UnicodeWarning, msg.c_str(), 1) == -1)
        throw py::error_already_set();

    return pysrc.release();
}

} // namespace detail

} // namespace dlisio

namespace {

/** trampoline helper class for dlis::error_handler bindings */
class PyErrorHandler : public dl::error_handler {
public:
    /* Inherit the constructor */
    using dl::error_handler::error_handler;

    /* Trampoline (need one for each virtual function) */
    void log(const dl::error_severity& level, const std::string& context,
             const std::string& problem, const std::string& specification,
             const std::string& action, const std::string& debug)
    const noexcept(false) override {
        PYBIND11_OVERLOAD_PURE(
            void,              /* Return type */
            dl::error_handler, /* Parent class */
            log,               /* Name of function in C++ */
            level,             /* Argument(s) */
            context,
            problem,
            specification,
            action,
            debug
        );
    }
};

} // namespace

/** dlis-specific binding code is implemented in a separate file. This has
 * several benefits [1]:
 *
 * 1. Reduce build time and enable parallel builds
 * 2. Faster incremental builds
 * 3. Keeping the binding module tidy and manageable
 *
 * [1] https://pybind11.readthedocs.io/en/stable/faq.html#how-can-i-reduce-the-build-time
 */
void init_lis_extension(py::module_ &m);
void init_dlis_extension(py::module_ &m);


PYBIND11_MAKE_OPAQUE( std::vector< dl::object_set > )
PYBIND11_MAKE_OPAQUE( std::vector< lis::record > )

PYBIND11_MODULE(core, m) {
    PyDateTime_IMPORT;

    py::register_exception_translator( []( std::exception_ptr p ) {
        try {
            if( p ) std::rethrow_exception( p );
        } catch( const dlisio::not_implemented& e ) {
            PyErr_SetString( PyExc_NotImplementedError, e.what() );
        } catch( const dlisio::io_error& e ) {
            PyErr_SetString( PyExc_IOError, e.what() );
        } catch( const dlisio::eof_error& e ) {
            PyErr_SetString( PyExc_EOFError, e.what() );
        }
    });

    init_lis_extension(m);
    init_dlis_extension(m);

    m.def( "read_tapemark",  dlisio::read_tapemark );
    m.def( "valid_tapemark", dlisio::valid_tapemark );

    py::class_< dlisio::tapemark >( m, "tapemark" )
        .def_readonly( "type", &dlisio::tapemark::type )
        .def_readonly( "prev", &dlisio::tapemark::prev )
        .def_readonly( "next", &dlisio::tapemark::next )
        .def( "__repr__", []( const dlisio::tapemark& x ) {
            return "dlisio.core.tapemark(type={}, prev={}, next={})"_s.format(
                    x.type, x.prev, x.next );
        })
    ;

    py::enum_< dl::error_severity >( m, "error_severity" )
        .value( "info",     dl::error_severity::INFO )
        .value( "minor",    dl::error_severity::MINOR )
        .value( "major",    dl::error_severity::MAJOR )
        .value( "critical", dl::error_severity::CRITICAL )
    ;

    py::class_< dl::dlis_error >( m, "dlis_error" )
        .def_readonly( "severity",      &dl::dlis_error::severity )
        .def_readonly( "problem",       &dl::dlis_error::problem )
        .def_readonly( "specification", &dl::dlis_error::specification )
        .def_readonly( "action",        &dl::dlis_error::action )
    ;

    py::class_< dl::error_handler, PyErrorHandler >( m, "error_handler")
        .def(py::init<>())
    ;

    /* settings */
    m.def("set_encodings", set_encodings);
    m.def("get_encodings", get_encodings);

}
