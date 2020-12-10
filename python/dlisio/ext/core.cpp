#include <bitset>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <exception>
#include <fstream>
#include <iterator>
#include <memory>
#include <string>
#include <type_traits>
#include <vector>
#include <limits>
#include <functional>

#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include <pybind11/stl.h>
#include <datetime.h>

#include <dlisio/dlisio.h>
#include <dlisio/types.h>

namespace py = pybind11;
using namespace py::literals;

namespace dl {
/*
 * Explicitly make the custom exceptions visible, by forward declarling them
 * with pybind's export macro. Otherwise they can be considered different
 * symbols in parse.cpp and in the python extension, making exception
 * translation impossible.
 *
 * https://github.com/pybind/pybind11/issues/1272
 */

class PYBIND11_EXPORT io_error;
class PYBIND11_EXPORT eof_error;
class PYBIND11_EXPORT not_implemented;
class PYBIND11_EXPORT not_found;
}

#include <dlisio/ext/exception.hpp>
#include <dlisio/ext/io.hpp>
#include <dlisio/ext/types.hpp>

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

}

namespace pybind11 { namespace detail {

/*
 * Register boost::optional and mpark::variant type casters, since C++17 is not
 * a requirement yet, and auto-conversion from optional to None/object and
 * auto-variant-extraction is desired.
 *
 * https://pybind11.readthedocs.io/en/stable/advanced/cast/stl.html
 */

template < typename... T >
struct type_caster< mpark::variant< T... > > :
    variant_caster< mpark::variant< T... > > {};

/*
 * Automate the conversion of strong typedefs to python type that corresponds
 * to the underlying data type (as returned by dl::decay).
 */
template < typename T >
struct dlis_caster {
    PYBIND11_TYPE_CASTER(T, _("dlisio.core.type.")+_(dl::typeinfo< T >::name));

    static handle cast( const T& src, return_value_policy, handle ) {
        return py::cast( dl::decay( src ) ).release();
    }

    /*
     * For now, do not succeed ever when trying to convert from a python value
     * to the corresponding C++ value, because it's not used and probably
     * requires some template specialisation
     */
    bool load( handle, bool ) { return false; }
};


template <>
struct type_caster< mpark::monostate > {
    PYBIND11_TYPE_CASTER(mpark::monostate, _("monostate"));

    static handle cast( const mpark::monostate&, return_value_policy, handle ) {
        return py::none();
    }

    bool load( handle, bool ) { return false; }
};

template <>
handle dlis_caster< dl::dtime >::cast( const dl::dtime& src, return_value_policy, handle )
{
    // TODO: add TZ info
    return PyDateTime_FromDateAndTime( src.Y,
                                       src.M,
                                       src.D,
                                       src.H,
                                       src.MN,
                                       src.S,
                                       src.MS * 1000);
}

template <>
handle dlis_caster< dl::fsing1 >::cast( const dl::fsing1& src, return_value_policy, handle )
{
    return py::make_tuple(src.V, src.A).release();
}

template <>
handle dlis_caster< dl::fsing2 >::cast( const dl::fsing2& src, return_value_policy, handle )
{
    return py::make_tuple(src.V, src.A, src.B).release();
}

template <>
handle dlis_caster< dl::fdoub1 >::cast( const dl::fdoub1& src, return_value_policy, handle )
{
    return py::make_tuple(src.V, src.A).release();
}

template <>
handle dlis_caster< dl::fdoub2 >::cast( const dl::fdoub2& src, return_value_policy, handle )
{
    return py::make_tuple(src.V, src.A, src.B).release();
}

template <>
handle dlis_caster< dl::csingl >::cast( const dl::csingl& src, return_value_policy, handle )
{
    return PyComplex_FromDoubles(src.real(), src.imag());
}

template <>
handle dlis_caster< dl::cdoubl >::cast( const dl::cdoubl& src, return_value_policy, handle )
{
    return PyComplex_FromDoubles(src.real(), src.imag());
}

namespace {

handle decode_str(const std::string& src) noexcept (false) {
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

}

template <>
handle dlis_caster< dl::ascii >::cast(const dl::ascii& src, return_value_policy, handle)
{
    return decode_str(dl::decay(src));
}

template <>
handle dlis_caster< dl::ident >::cast(const dl::ident& src, return_value_policy, handle)
{
    return decode_str(dl::decay(src));
}

template <>
handle dlis_caster< dl::units >::cast(const dl::units& src, return_value_policy, handle)
{
    return decode_str(dl::decay(src));
}

/*
 * Now *register* the strong-typedef type casters with pybind, so that py::cast
 * and the pybind implicit conversion works.
 *
 * Notice that types that just alias native types (std::int32_t/slong etc.)
 * SHOULD NOT be registered this way, as the conversion already exists, and
 * would cause an infinite loop in the conversion logic.
 */
template <> struct type_caster< dl::fshort > : dlis_caster< dl::fshort > {};
template <> struct type_caster< dl::isingl > : dlis_caster< dl::isingl > {};
template <> struct type_caster< dl::vsingl > : dlis_caster< dl::vsingl > {};
template <> struct type_caster< dl::fsing1 > : dlis_caster< dl::fsing1 > {};
template <> struct type_caster< dl::fsing2 > : dlis_caster< dl::fsing2 > {};
template <> struct type_caster< dl::fdoub1 > : dlis_caster< dl::fdoub1 > {};
template <> struct type_caster< dl::fdoub2 > : dlis_caster< dl::fdoub2 > {};
template <> struct type_caster< dl::csingl > : dlis_caster< dl::csingl > {};
template <> struct type_caster< dl::cdoubl > : dlis_caster< dl::cdoubl > {};
template <> struct type_caster< dl::uvari  > : dlis_caster< dl::uvari  > {};
template <> struct type_caster< dl::ident  > : dlis_caster< dl::ident  > {};
template <> struct type_caster< dl::ascii  > : dlis_caster< dl::ascii  > {};
template <> struct type_caster< dl::dtime  > : dlis_caster< dl::dtime  > {};
template <> struct type_caster< dl::origin > : dlis_caster< dl::origin > {};
template <> struct type_caster< dl::status > : dlis_caster< dl::status > {};
template <> struct type_caster< dl::units  > : dlis_caster< dl::units  > {};

}} // namespace pybind11::detail

namespace {

py::dict storage_label( py::buffer b ) {
    auto info = b.request();
    if (info.size < DLIS_SUL_SIZE) {
        std::string msg =
            "buffer to small: buffer.size (which is "
            + std::to_string( info.size ) + ") < "
            + "n (which is " + std::to_string( DLIS_SUL_SIZE ) + ")"
        ;
        throw std::invalid_argument( msg );
    }

    int seqnum;
    int major;
    int minor;
    int layout;
    std::int64_t maxlen;
    char id[ 61 ] = {};
    auto err = dlis_sul( static_cast< const char* >( info.ptr ),
                         &seqnum,
                         &major,
                         &minor,
                         &layout,
                         &maxlen,
                         id );


    switch (err) {
        case DLIS_OK: break;

        // TODO: report more precisely  a lot of stuff can go wrong with the
        // SUL
        case DLIS_UNEXPECTED_VALUE:
            throw py::value_error( "unable to parse storage label" );

        case DLIS_INCONSISTENT:
            runtime_warning(
                "storage unit label inconsistent with "
                "specification - falling back to assuming DLIS v1"
            );
            break;
    }

    std::string version = std::to_string( major )
        + "."
        + std::to_string( minor );

    std::string laystr = "record";
    if (layout != DLIS_STRUCTURE_RECORD) laystr = "unknown";

    return py::dict(
        "sequence"_a = seqnum,
        "version"_a = version.c_str(),
        "layout"_a = laystr.c_str(),
        "maxlen"_a = maxlen,
        "id"_a =  id
    );
}

dl::ident fingerprint(const std::string& type,
                      const std::string& id,
                      std::int32_t origin,
                      std::int32_t copy) {

    std::string msg = "Invalid argument, copy out of range";
    if ( copy > (std::numeric_limits< std::uint8_t >::max)() )
        throw std::invalid_argument( msg );

    if ( copy < (std::numeric_limits< std::uint8_t >::min)() )
        throw std::invalid_argument( msg );

    const auto ucopy = std::uint8_t(copy);

    dl::objref ref;
    ref.type = dl::ident{ type };
    ref.name.origin = dl::origin{ origin };
    ref.name.copy = dl::ushort{ ucopy };
    ref.name.id = dl::ident{ id };
    return ref.fingerprint();
}

void assert_overflow(const char* ptr, const char* end, int skip) {
    if (ptr + skip > end) {
        const auto msg = "corrupted record: fmtstr would read past end";
        throw std::runtime_error(msg);
    }
}

void read_curve_sample(const char* f, const char*& ptr, const char* end,
                      unsigned char*& dst)
{
    /*
     * Reads to dst buffer a singular curve where:
     *    f   - current fmt character
     *    ptr - pointer to current position in source buffer (file record)
     *    end - pointer to end of the source buffer (record end)
     *    dst - pointer to current position in destination buffer
     */

    /*
     * Supporting bounded-length identifiers in frame data is
     * slightly more difficult than it immediately seem like, and
     * this implementation relies on a few assumptions that may not
     * hold.
     *
     * 1. numpy structured arrays interpret unicode on the fly
     *
     * On my amd64 linux:
     * >>> dt = np.dtype('U5')
     * >>> dt.itemsize
     * 20
     * >>> np.array(['foo'], dtype = dt)[0]
     * 'foo'
     * >>> np.array(['foobar'], dtype = dt)[0]
     * 'fooba'
     *
     * Meaning it supports string lengths of [0, n]. It apparently
     * (and maybe rightly so) uses null termination, or the bounded
     * length, which ever comes first.
     *
     * 2. numpy stores characters as int32 Py_UNICODE
     * Numpy seems to always use uint32, and not Py_UNICODE, which
     * can be both 16 and 32 bits [1]. Since it's an integer it's
     * endian sensitive, and widening from char works. This is not
     * really documented by numpy.
     *
     * 3. numpy stores no metadata with the string
     * It is assumed, and seems necessary from the interface, that
     * there is no in-band metadata stored about the strings when
     * used in structured arrays. This means we can just write the
     * unicode ourselves, and have numpy interpret it correctly.
     *
     * --
     * Units is just an IDENT in disguise, so it can very well take
     * the same code path.
     *
     * [1] http://docs.h5py.org/en/stable/strings.html#what-about-numpy-s-u-type
     *     NumPy also has a Unicode type, a UTF-32 fixed-width
     *     format (4-byte characters). HDF5 has no support for wide
     *     characters. Rather than trying to hack around this and
     *     “pretend” to support it, h5py will raise an error when
     *     attempting to create datasets or attributes of this
     *     type.
     *
     */
     auto swap_pointer = [&](py::object obj)
     {
         PyObject* p;
         std::memcpy(&p, dst, sizeof(p));
         Py_DECREF(p);
         p = obj.inc_ref().ptr();
         std::memcpy(dst, &p, sizeof(p));
         dst += sizeof(p);
     };

     if (*f == DLIS_FMT_FSING1) {
        float v;
        float a;
        ptr = dlis_fsing1(ptr, &v, &a);
        auto t = py::make_tuple(v, a);

        swap_pointer(t);
        return;
    }

     if (*f == DLIS_FMT_FSING2) {
        float v;
        float a;
        float b;
        ptr = dlis_fsing2(ptr, &v, &a, &b);
        auto t = py::make_tuple(v, a, b);

        swap_pointer(t);
        return;
    }

     if (*f == DLIS_FMT_FDOUB1) {
        double v;
        double a;
        ptr = dlis_fdoub1(ptr, &v, &a);
        auto t = py::make_tuple(v, a);

        swap_pointer(t);
        return;
    }

     if (*f == DLIS_FMT_FDOUB2) {
        double v;
        double a;
        double b;
        ptr = dlis_fdoub2(ptr, &v, &a, &b);
        auto t = py::make_tuple(v, a, b);

        swap_pointer(t);
        return;
    }

    if (*f == DLIS_FMT_IDENT || *f == DLIS_FMT_UNITS) {
        constexpr auto chars = 255;
        constexpr auto ident_size = chars * sizeof(std::uint32_t);

        std::int32_t len;
        char tmp[chars];
        ptr = dlis_ident(ptr, &len, tmp);

        /*
         * From reading the numpy source, it looks like they put
         * and interpret the unicode buffer in the array directly,
         * and pad with zero. This means the string is both null
         * and length terminated, whichever comes first.
         */
        std::memset(dst, 0, ident_size);
        for (auto i = 0; i < len; ++i) {
            const auto x = std::uint32_t(tmp[i]);
            std::memcpy(dst + i * sizeof(x), &x, sizeof(x));
        }
        dst += ident_size;
        return;
    }

    if (*f == DLIS_FMT_ASCII) {
        std::int32_t len;
        ptr = dlis_uvari(ptr, &len);
        auto ascii = py::str(ptr, len);
        ptr += len;

        /*
         * Numpy seems to default initalize object types even in
         * the case of np.empty to None [1]. The refcount is surely
         * increased, so decref it before replacing the pointer
         * with a fresh str.
         *
         * [1] Array of uninitialized (arbitrary) data of the given
         *     shape, dtype, and order. Object arrays will be
         *     initialized to None.
         *     https://docs.scipy.org/doc/numpy/reference/generated/numpy.empty.html
         */
        swap_pointer(ascii);
        return;
    }

    if (*f == DLIS_FMT_OBNAME) {
        std::int32_t origin;
        std::uint8_t copy;
        std::int32_t idlen;
        char id[255];
        ptr = dlis_obname(ptr, &origin, &copy, &idlen, id);

        const auto name = dl::obname {
            dl::origin(origin),
            dl::ushort(copy),
            dl::ident(std::string(id, idlen)),
        };

        swap_pointer(py::cast(name));
        return;
    }

    if (*f == DLIS_FMT_OBJREF) {
        std::int32_t idlen;
        char id[255];
        std::int32_t origin;
        std::uint8_t copy;
        std::int32_t objnamelen;
        char objname[255];
        ptr = dlis_objref(ptr,
                          &idlen,
                          id,
                          &origin,
                          &copy,
                          &objnamelen,
                          objname);

        const auto name = dl::objref {
            dl::ident(std::string(id, idlen)),
            dl::obname {
                dl::origin(origin),
                dl::ushort(copy),
                dl::ident(std::string(objname, objnamelen)),
            },
        };

        swap_pointer(py::cast(name));
        return;
    }

    if (*f == DLIS_FMT_ATTREF) {
        std::int32_t id1len;
        char id1[255];
        std::int32_t origin;
        std::uint8_t copy;
        std::int32_t objnamelen;
        char objname[255];
        std::int32_t id2len;
        char id2[255];
        ptr = dlis_attref(ptr,
                          &id1len,
                          id1,
                          &origin,
                          &copy,
                          &objnamelen,
                          objname,
                          &id2len,
                          id2);

        const auto ref = dl::attref {
            dl::ident(std::string(id1, id1len)),
            dl::obname {
                dl::origin(origin),
                dl::ushort(copy),
                dl::ident(std::string(objname, objnamelen)),
            },
            dl::ident(std::string(id2, id2len)),
        };

        swap_pointer(py::cast(ref));
        return;
    }

    if (*f == DLIS_FMT_DTIME) {
        int Y, TZ, M, D, H, MN, S, MS;
        ptr = dlis_dtime(ptr, &Y, &TZ, &M, &D, &H, &MN, &S, &MS);
        Y = dlis_year(Y);
        const auto US = MS * 1000;

        PyObject* p;
        std::memcpy(&p, dst, sizeof(p));
        Py_DECREF(p);
        p = PyDateTime_FromDateAndTime(Y, M, D, H, MN, S, US);
        if (!p) throw py::error_already_set();
        std::memcpy(dst, &p, sizeof(p));
        dst += sizeof(p);
        return;
    }

    int src_skip, dst_skip;
    const char localfmt[] = {*f, '\0'};
    dlis_packflen(localfmt, ptr, &src_skip, &dst_skip);
    assert_overflow(ptr, end, src_skip);
    dlis_packf(localfmt, ptr, dst);
    dst += dst_skip;
    ptr += src_skip;
}

void read_fdata_frame(const char* fmt, const char*& ptr, const char* end,
                      unsigned char*& dst) noexcept (false) {
    for (auto* f = fmt; *f; ++f) {
        read_curve_sample(f, ptr, end, dst);
    }
}

void read_fdata_record(const char* pre_fmt,
                       const char* fmt,
                       const char* post_fmt,
                       const char* ptr,
                       const char* end,
                       unsigned char*& dst,
                       int& frames,
                       const std::size_t& itemsize,
                       std::size_t allocated_rows,
                       std::function<void (std::size_t)> resize)
noexcept (false) {

    /* get frame number and slots */
    while (ptr < end) {
        if (frames == allocated_rows) {
            resize(frames * 2);
            dst += (frames * itemsize);
        }

        int src_skip, dst_skip;

        dlis_packflen(pre_fmt, ptr, &src_skip, nullptr);
        assert_overflow(ptr, end, src_skip);
        ptr += src_skip;

        read_fdata_frame(fmt, ptr, end, dst);

        dlis_packflen(post_fmt, ptr, &src_skip, nullptr);
        assert_overflow(ptr, end, src_skip);
        ptr += src_skip;

        ++frames;
    }
}

py::object read_fdata(const char* pre_fmt,
                      const char* fmt,
                      const char* post_fmt,
                      dl::stream& file,
                      const std::vector< long long >& indices,
                      std::size_t itemsize,
                      py::object alloc,
                      dl::error_handler& errorhandler)
noexcept (false) {
    // TODO: reverse fingerprint to skip bytes ahead-of-time
    /*
     * TODO: error has already been checked (in python), but should be more
     * thorough
     *
     * TODO: veriy that format string is valid
     */
    /*
     * This function goes through a lot of ceremony to use numpy arrays
     * directly, and to write output data in-place in the return value. The
     * main reason is *exception safety*.
     *
     * Virtually every operation that goes into this can throw an exception,
     * and when that happens it's important that not-yet-complete data is
     * cleaned up.
     *
     * Of course, for all non-object types this is not a problem, as they're
     * just bytes in an array, and std::vector would've been plenty. It's made
     * more complicated by the presence of PyObject* pointers embedded in the
     * data stream - there are no C++ destructors that can elegantly reach
     * them, and doing that would pretty much be replicating numpy
     * functionality anyway.
     *
     * By writing directly into the numpy array as we go, PyObjects are either
     * default-constructed (set to None) by numpy, or properly created (and
     * replaced) here.
     */
    auto allocated_rows = indices.size();
    auto dstobj = alloc(allocated_rows);
    auto dstb = py::buffer(dstobj);
    auto info = dstb.request(true);
    auto* dst = static_cast< unsigned char* >(info.ptr);

    /*
     * Resizing is clumsy, because in-place resize (through the method)
     * requires there to be no references to the underlying data. That means
     * the buffer-info and buffer must be wiped before resizing takes place,
     * and then carefully restored to the new memory.
     */
    auto resize = [&](std::size_t n) {
        info = py::buffer_info {};
        dstb = py::buffer {};
        dstobj.attr("resize")(n);
        allocated_rows = n;
        dstb = py::buffer(dstobj);
        info = dstb.request(true);
        dst = static_cast< unsigned char* >(info.ptr);
    };


    /*
     * The frameno is a part of the dtype, and only frame.channels is allowed
     * to call this function. If pre/post format is set, wrong data is read.
     *
     * The interface is not changed for now as they're to be reintroduced at
     * some point.
     */
    assert(std::string(pre_fmt) == "");
    assert(std::string(post_fmt) == "");

    auto record_dst = dst;

    const auto handle = [&]( const std::string& problem ) {
        const auto context = "dl::read_fdata: reading curves";
        errorhandler.log(dl::error_severity::CRITICAL, context, problem, "",
                         "Record is skipped");
        // we update the buffer as we go. Hence if error happened we need to
        // go back and start rewriting updated data
        dst = record_dst;
    };

    int frames = 0;
    for (auto i : indices) {
        record_dst = dst;

        /* get record */
        dl::record record;
        try {
            record = dl::extract(file, i, errorhandler);
        } catch (std::exception& e) {
            handle(e.what());
            continue;
        }

        if (record.isencrypted()) {
            handle("encrypted FDATA record");
            continue;
        }

        const auto* ptr = record.data.data();
        const auto* end = ptr + record.data.size();

        /* read fingerprint */
        std::int32_t origin;
        std::uint8_t copy;
        ptr = dlis_obname(ptr, &origin, &copy, nullptr, nullptr);

        try {
            read_fdata_record(pre_fmt, fmt, post_fmt, ptr, end, dst, frames,
                              itemsize, allocated_rows, resize);
        } catch (std::exception& e) {
            handle(e.what());
            continue;
        }
    }

    assert(allocated_rows >= frames);
    if (allocated_rows > frames)
        resize(frames);

    return dstobj;
}

/** trampoline helper class for dl::matcher bindings
 *
 * Creating the binding code for a abstract c++ class that we want do derive
 * new classes from in python requires some extra boilerplate code in the form
 * of this "trampoline" class [1].
 *
 * This class helps redirect virtual calls back to python and is *not* intended
 * to be used for anything other than creating valid bindings for dl::matcher.
 *
 * [1] https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtual-functions-in-python
 */
class Pymatcher : public dl::matcher {
public:
    /* Inherit the constructor */
    using dl::matcher::matcher;

    /* Trampoline (need one for each virtual function) */
    bool match(const dl::ident& pattern, const dl::ident& candidate)
    const noexcept(false) override {
        PYBIND11_OVERLOAD_PURE(
            bool,           /* Return type */
            dl::matcher,    /* Parent class */
            match,          /* Name of function in C++ (must match Python name) */
            pattern,        /* Argument(s) */
            candidate
        );
    }
};

/** trampoline helper class for dl::error_handler bindings */
class PyErrorHandler : public dl::error_handler {
public:
    /* Inherit the constructor */
    using dl::error_handler::error_handler;

    /* Trampoline (need one for each virtual function) */
    void log(const dl::error_severity& level, const std::string& context,
             const std::string& problem, const std::string& specification,
             const std::string& action)
    const noexcept(false) override {
        PYBIND11_OVERLOAD_PURE(
            void,              /* Return type */
            dl::error_handler, /* Parent class */
            log,               /* Name of function in C++ */
            level,             /* Argument(s) */
            context,
            problem,
            specification,
            action
        );
    }
};

}

PYBIND11_MAKE_OPAQUE( std::vector< dl::object_set > )

PYBIND11_MODULE(core, m) {
    PyDateTime_IMPORT;

    py::register_exception_translator( []( std::exception_ptr p ) {
        try {
            if( p ) std::rethrow_exception( p );
        } catch( const dl::not_implemented& e ) {
            PyErr_SetString( PyExc_NotImplementedError, e.what() );
        } catch( const dl::io_error& e ) {
            PyErr_SetString( PyExc_IOError, e.what() );
        } catch( const dl::eof_error& e ) {
            PyErr_SetString( PyExc_EOFError, e.what() );
        }
    });

    py::bind_vector<std::vector< dl::object_set >>(m, "list(object_set)");

    m.def("open", &dl::open, py::arg("path"), py::arg("zero") = 0);
    m.def("open_rp66", &dl::open_rp66);
    m.def("open_tif", &dl::open_tapeimage);

    m.def( "storage_label", storage_label );
    m.def("fingerprint", fingerprint);
    m.def("read_fdata", read_fdata);

    /*
     * TODO: support constructor with kwargs
     * TODO: support comparison with tuple
     * TODO: fmtlib for strings
     * TODO: remove obname/objref etc altogether. The obnoxious __eq__ is a
     *       symptom of bad design
     *
     */
    py::class_< dl::obname >( m, "obname" )
        .def_readonly( "origin",     &dl::obname::origin )
        .def_readonly( "copynumber", &dl::obname::copy )
        .def_readonly( "id",         &dl::obname::id )
        .def(py::init([](int origin, std::uint8_t copynum, std::string id){
            return dl::obname{dl::origin{origin},
                              dl::ushort{copynum},
                              dl::ident{id}};
        }))
        .def( "fingerprint",         &dl::obname::fingerprint )
        .def( "__eq__",              &dl::obname::operator == )
        .def( "__ne__",              &dl::obname::operator != )
        .def( "__repr__", []( const dl::obname& o ) {
            return "dlisio.core.obname(id='{}', origin={}, copynum={})"_s
                    .format( dl::decay(o.id),
                             dl::decay(o.origin),
                             dl::decay(o.copy) )
                    ;
        })
        .def( "__eq__", [](const dl::obname& lhs,
                           const std::tuple< int, std::uint8_t, std::string >& rhs) {
            auto r = dl::obname {
                dl::origin{ std::get< 0 >(rhs) },
                dl::ushort{ std::get< 1 >(rhs) },
                dl::ident{  std::get< 2 >(rhs) },
            };

            return r == lhs;
        })
    ;

    py::class_< dl::objref >( m, "objref" )
        .def_readonly( "type", &dl::objref::type )
        .def_readonly( "name", &dl::objref::name )
        .def( "__eq__",        &dl::objref::operator == )
        .def( "__ne__",        &dl::objref::operator != )
        .def_property_readonly("fingerprint", &dl::objref::fingerprint)
        .def( "__repr__", []( const dl::objref& o ) {
            return "dlisio.core.objref(fingerprint={})"_s
                    .format(o.fingerprint());
        })
        .def( "__eq__", [](const dl::objref& lhs,
                           const std::tuple<
                                std::string,
                                std::tuple< int, std::uint8_t, std::string >
                            >& rhs)
        {
            auto r = dl::objref {
                dl::ident { std::get< 0 >(rhs) },
                dl::obname {
                    dl::origin{ std::get< 0 >(std::get< 1 >(rhs)) },
                    dl::ushort{ std::get< 1 >(std::get< 1 >(rhs)) },
                    dl::ident{  std::get< 2 >(std::get< 1 >(rhs)) },
                },
            };

            return r == lhs;
        })
    ;

    py::class_< dl::attref >( m, "attref" )
        .def_readonly( "type", &dl::attref::type )
        .def_readonly( "name", &dl::attref::name )
        .def_readonly( "label", &dl::attref::label )
        .def( "__eq__", &dl::attref::operator == )
        .def( "__ne__", &dl::attref::operator != )
        .def( "__repr__", []( const dl::attref& o ) {
            return "dlisio.core.attref(id='{}', origin={}, copynum={}, type={})"_s
                    .format( dl::decay(o.name.id),
                             dl::decay(o.name.origin),
                             dl::decay(o.name.copy),
                             dl::decay(o.type) )
                    ;
        })
        .def( "__eq__", [](const dl::attref& lhs,
                           const std::tuple<
                                std::string,
                                std::tuple< int, std::uint8_t, std::string >,
                                std::string
                            >& rhs)
        {
            auto r = dl::attref {
                dl::ident { std::get< 0 >(rhs) },
                dl::obname {
                    dl::origin{ std::get< 0 >(std::get< 1 >(rhs)) },
                    dl::ushort{ std::get< 1 >(std::get< 1 >(rhs)) },
                    dl::ident{  std::get< 2 >(std::get< 1 >(rhs)) },
                },
                dl::ident { std::get< 2 >(rhs) },
            };

            return r == lhs;
        })
    ;

    py::class_< dl::object_attribute >( m, "object_attribute" )
        .def_readonly("value", &dl::object_attribute::value)
        .def_readonly("units", &dl::object_attribute::units)
        .def_readonly("log",   &dl::object_attribute::log)
    ;

    py::class_< dl::basic_object >( m, "basic_object" )
        .def_readonly("type", &dl::basic_object::type)
        .def_readonly("name", &dl::basic_object::object_name)
        .def_readonly("log",  &dl::basic_object::log)
        .def( "__len__", []( const dl::basic_object& o ) {
            return o.attributes.size();
        })
        .def( "__eq__", &dl::basic_object::operator == )
        .def( "__ne__", &dl::basic_object::operator != )
        .def( "__getitem__", []( dl::basic_object& o, const std::string& key ) {
            try { return o.at(key); }
            catch (const std::out_of_range& e) { throw py::key_error( e.what() ); }
        })
        .def( "__repr__", []( const dl::basic_object& o ) {
            return "dlisio.core.basic_object(name={})"_s
                    .format(o.object_name);
        })
        .def( "keys", []( const dl::basic_object& o ){
            std::vector< dl::ident > keys;
            for ( auto attr : o.attributes ) {
                keys.push_back( attr.label );
            }
            return keys;
        })
    ;

    py::class_< dl::object_set >( m, "object_set" )
        .def_readonly( "type", &dl::object_set::type )
        .def_readonly( "name", &dl::object_set::name )
        .def( "objects", &dl::object_set::objects )
    ;

    py::class_< dl::pool >( m, "pool" )
        .def(py::init< std::vector< dl::object_set> >())
        .def_property_readonly( "types", &dl::pool::types )
        .def( "get", (dl::object_vector (dl::pool::*) (
            const std::string&,
            const std::string&,
            const dl::matcher&,
            const dl::error_handler&
        )) &dl::pool::get )
        .def( "get", (dl::object_vector (dl::pool::*) (
            const std::string&,
            const dl::matcher&,
            const dl::error_handler&
        )) &dl::pool::get )
    ;

    py::enum_< dl::representation_code >( m, "reprc" )
        .value( "fshort", dl::representation_code::fshort )
        .value( "fsingl", dl::representation_code::fsingl )
        .value( "fsing1", dl::representation_code::fsing1 )
        .value( "fsing2", dl::representation_code::fsing2 )
        .value( "isingl", dl::representation_code::isingl )
        .value( "vsingl", dl::representation_code::vsingl )
        .value( "fdoubl", dl::representation_code::fdoubl )
        .value( "fdoub1", dl::representation_code::fdoub1 )
        .value( "fdoub2", dl::representation_code::fdoub2 )
        .value( "csingl", dl::representation_code::csingl )
        .value( "cdoubl", dl::representation_code::cdoubl )
        .value( "sshort", dl::representation_code::sshort )
        .value( "snorm" , dl::representation_code::snorm  )
        .value( "slong" , dl::representation_code::slong  )
        .value( "ushort", dl::representation_code::ushort )
        .value( "unorm" , dl::representation_code::unorm  )
        .value( "ulong" , dl::representation_code::ulong  )
        .value( "uvari" , dl::representation_code::uvari  )
        .value( "ident" , dl::representation_code::ident  )
        .value( "ascii" , dl::representation_code::ascii  )
        .value( "dtime" , dl::representation_code::dtime  )
        .value( "origin", dl::representation_code::origin )
        .value( "obname", dl::representation_code::obname )
        .value( "objref", dl::representation_code::objref )
        .value( "attref", dl::representation_code::attref )
        .value( "status", dl::representation_code::status )
        .value( "units" , dl::representation_code::units  )
    ;

    py::class_< dl::record >( m, "record", py::buffer_protocol() )
        .def_property_readonly( "explicit",  &dl::record::isexplicit )
        .def_property_readonly( "encrypted", &dl::record::isencrypted )
        .def_readonly( "consistent", &dl::record::consistent )
        .def_readonly( "type", &dl::record::type )
        .def_buffer( []( dl::record& rec ) -> py::buffer_info {
            const auto fmt = py::format_descriptor< char >::format();
            return py::buffer_info(
                rec.data.data(),    /* Pointer to buffer */
                sizeof(char),       /* Size of one scalar */
                fmt,                /* Python struct-style format descriptor */
                1,                  /* Number of dimensions */
                { rec.data.size() },/* Buffer dimensions */
                { 1 }               /* Strides (in bytes) for each index */
            );
        })
    ;

    py::class_< dl::stream >( m, "stream" )
        .def_property_readonly("absolute_tell", &dl::stream::absolute_tell)
        .def("seek", &dl::stream::seek)
        .def("eof", &dl::stream::eof)
        .def( "close", &dl::stream::close )
        .def( "get", []( dl::stream& s, py::buffer b, long long off, int n ) {
            auto info = b.request();
            if (info.size < n) {
                std::string msg =
                      "buffer to small: buffer.size (which is "
                    + std::to_string( info.size ) + ") < "
                    + "n (which is " + std::to_string( n ) + ")"
                ;
                throw std::invalid_argument( msg );
            }
            s.seek( off );
            s.read( static_cast< char* >( info.ptr ), n );
            return b;
        })
    ;

    m.def( "extract", [](dl::stream& s,
                        const std::vector< long long >& tells,
                        dl::error_handler& errorhandler) {
        std::vector< dl::record > recs;
        recs.reserve( tells.size() );
        for (auto tell : tells) {
            dl::record rec;
            try {
                rec = dl::extract(s, tell, errorhandler);
            } catch (const std::exception& e) {
                const auto context =
                    "dl::extract: Reading raw bytes from record";
                errorhandler.log(dl::error_severity::CRITICAL, context,
                                 e.what(), "", "Record is skipped");
                continue;
            }
            if (rec.data.size() > 0) {
                recs.push_back( std::move( rec ) );
            }
        }
        return recs;
    });

    m.def( "parse_objects", []( const std::vector< dl::record >& recs,
                                dl::error_handler& errorhandler ) {
        std::vector< dl::object_set > objects;
        for (const auto& rec : recs) {
            if (rec.isencrypted()) continue;

            try {
                objects.push_back( dl::object_set( rec ) );
            } catch (const std::exception& e) {
                const auto context =
                    "core.parse_objects: Construct object sets";
                errorhandler.log(dl::error_severity::CRITICAL, context,
                                 e.what(), "", "Set is skipped");
                continue;
            }
        }
        return objects;
    });

    m.def( "findsul", dl::findsul );
    m.def( "findvrl", dl::findvrl );
    m.def( "hastapemark", dl::hastapemark );
    m.def("findfdata", dl::findfdata);

    m.def( "findoffsets", []( dl::stream& file,
                              dl::error_handler& errorhandler) {
        const auto ofs = dl::findoffsets( file, errorhandler );
        return py::make_tuple( ofs.explicits, ofs.implicits, ofs.broken );
    });

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

    py::class_< dl::matcher, Pymatcher >( m, "matcher")
        .def(py::init<>())
    ;

    py::class_< dl::error_handler, PyErrorHandler >( m, "error_handler")
        .def(py::init<>())
    ;

    /* settings */
    m.def("set_encodings", set_encodings);
    m.def("get_encodings", get_encodings);

}
