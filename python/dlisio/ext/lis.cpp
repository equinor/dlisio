#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <mpark/variant.hpp>

#include <dlisio/lis/pack.h>
#include <dlisio/lis/types.h>
#include <dlisio/lis/types.hpp>
#include <dlisio/lis/io.hpp>
#include <dlisio/lis/protocol.hpp>
#include <dlisio/exception.hpp>

#include "common.hpp"

namespace lis = dlisio::lis79;
namespace py = pybind11;
using namespace py::literals;

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
struct lis_caster {
    PYBIND11_TYPE_CASTER(T, _("dlisio.core.type.")+_(lis::typeinfo< T >::name));

    static handle cast( const T& src, return_value_policy, handle ) {
        return py::cast( lis::decay( src ) ).release();
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
handle lis_caster< lis::string >::cast(const lis::string& src,
                                       return_value_policy,
                                       handle) {
    //TODO possibly implement a trailing whitespace stripper?
    return dlisio::detail::decode_str(lis::decay(src));
}

template <>
handle lis_caster< lis::mask >::cast(const lis::mask& src,
                                     return_value_policy,
                                     handle) {
    return dlisio::detail::decode_str(lis::decay(src));
}
/*
 * Now *register* the strong-typedef type casters with pybind, so that py::cast
 * and the pybind implicit conversion works.
 *
 * Notice that types that just alias native types (std::int32_t/i32 etc.)
 * SHOULD NOT be registered this way, as the conversion already exists, and
 * would cause an infinite loop in the conversion logic.
 */
template <> struct type_caster< lis::i8     > : lis_caster< lis::i8     > {};
template <> struct type_caster< lis::i16    > : lis_caster< lis::i16    > {};
template <> struct type_caster< lis::i32    > : lis_caster< lis::i32    > {};
template <> struct type_caster< lis::f16    > : lis_caster< lis::f16    > {};
template <> struct type_caster< lis::f32    > : lis_caster< lis::f32    > {};
template <> struct type_caster< lis::f32low > : lis_caster< lis::f32low > {};
template <> struct type_caster< lis::f32fix > : lis_caster< lis::f32fix > {};
template <> struct type_caster< lis::string > : lis_caster< lis::string > {};
template <> struct type_caster< lis::byte   > : lis_caster< lis::byte   > {};
template <> struct type_caster< lis::mask   > : lis_caster< lis::mask   > {};

}} // namespace pybind11::detail

namespace {

void assert_overflow(const char* ptr, const char* end, int skip) {
    if (ptr + skip > end) {
        const auto msg = "corrupted record: fmtstr would read past end";
        throw std::runtime_error(msg);
    }
}

void read_frame( const std::string& fmt,
                 const char*& ptr,
                 const char* end,
                 unsigned char*& dst )
noexcept (false) {
    auto swap_pointer = [&](py::object obj)
    {
        PyObject* p;
        std::memcpy(&p, dst, sizeof(p));
        Py_DECREF(p);
        p = obj.inc_ref().ptr();
        std::memcpy(dst, &p, sizeof(p));
        dst += sizeof(p);
    };

    const char* f = fmt.c_str();
    while (true) {
        if (*f == LIS_FMT_EOL) {
            return;
        }

        else if (*f == LIS_FMT_SUPPRESS) {
            char* next;
            ptr += std::strtol(++f, &next, 10);
            f = next;
        }

        else if (*f == LIS_FMT_STRING) {
            char* next;
            auto len = std::strtol(++f, &next, 10);
            f = next;

            auto str = py::str(ptr, len);
            swap_pointer(str);
            ptr += len;
        }

        else {
            int src_skip, dst_skip;
            const char localfmt[] = {*f, '\0'};
            lis_packflen(localfmt, ptr, &src_skip, &dst_skip);
            assert_overflow(ptr, end, src_skip);
            lis_packf(localfmt, ptr, dst);
            dst += dst_skip;
            ptr += src_skip;
            ++f;
        }
    }
}

void read_data_record( const std::string& fmt,
                       const lis::record& src,
                       unsigned char*&    dst,
                       int& frames,
                       const std::size_t& itemsize,
                       std::size_t allocated_rows,
                       std::function<void (std::size_t)> resize )
noexcept (false) {

    const auto* ptr = src.data.data();
    const auto* end = ptr + src.data.size();

    /* get frame number and slots */
    while (ptr < end) {
        if (frames == allocated_rows) {
            resize(frames * 2);
            dst += (frames * itemsize);
        }

        read_frame(fmt, ptr, end, dst);

        ++frames;
    }
}


py::object read_data_records(const std::string& fmt,
                             lis::iodevice& file,
                             const lis::record_index& index,
                             const lis::record_info& recinfo,
                             std::size_t itemsize,
                             py::object alloc)
noexcept (false) {
    /*
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
    auto implicits = index.implicits_of( recinfo.ltell );
    auto allocated_rows = implicits.size();
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

    int frames = 0;

    for ( const auto& head : implicits ) {
        /* get record */
        auto record = file.read_record( head );
        read_data_record( fmt,
                          record,
                          dst,
                          frames,
                          itemsize,
                          allocated_rows,
                          resize );
    }

    assert(allocated_rows >= frames);
    if (allocated_rows > frames)
        resize(frames);

    return dstobj;
}

} // namespace


void init_lis_extension(py::module_ &m) {
    py::enum_< lis::record_type >( m, "lis_rectype")
        .value( "normal_data"         , lis::record_type::normal_data         )
        .value( "alternate_data"      , lis::record_type::alternate_data      )
        .value( "job_identification"  , lis::record_type::job_identification  )
        .value( "wellsite_data"       , lis::record_type::wellsite_data       )
        .value( "tool_string_info"    , lis::record_type::tool_string_info    )
        .value( "enc_table_dump"      , lis::record_type::enc_table_dump      )
        .value( "table_dump"          , lis::record_type::table_dump          )
        .value( "data_format_spec"    , lis::record_type::data_format_spec    )
        .value( "data_descriptor"     , lis::record_type::data_descriptor     )
        .value( "tu10_software_boot"  , lis::record_type::tu10_software_boot  )
        .value( "bootstrap_loader"    , lis::record_type::bootstrap_loader    )
        .value( "cp_kernel_loader"    , lis::record_type::cp_kernel_loader    )
        .value( "prog_file_header"    , lis::record_type::prog_file_header    )
        .value( "prog_overlay_header" , lis::record_type::prog_overlay_header )
        .value( "prog_overlay_load"   , lis::record_type::prog_overlay_load   )
        .value( "file_header"         , lis::record_type::file_header         )
        .value( "file_trailer"        , lis::record_type::file_trailer        )
        .value( "tape_header"         , lis::record_type::tape_header         )
        .value( "tape_trailer"        , lis::record_type::tape_trailer        )
        .value( "reel_header"         , lis::record_type::reel_header         )
        .value( "reel_trailer"        , lis::record_type::reel_trailer        )
        .value( "logical_eof"         , lis::record_type::logical_eof         )
        .value( "logical_bot"         , lis::record_type::logical_bot         )
        .value( "logical_eot"         , lis::record_type::logical_eot         )
        .value( "logical_eom"         , lis::record_type::logical_eom         )
        .value( "op_command_inputs"   , lis::record_type::op_command_inputs   )
        .value( "op_response_inputs"  , lis::record_type::op_response_inputs  )
        .value( "system_outputs"      , lis::record_type::system_outputs      )
        .value( "flic_comment"        , lis::record_type::flic_comment        )
        .value( "blank_record"        , lis::record_type::blank_record        )
        .value( "picture"             , lis::record_type::picture             )
        .value( "image"               , lis::record_type::image               )
    ;

    py::enum_< lis::representation_code >( m, "lis_reprc")
        .value( "i8"     , lis::representation_code::i8     )
        .value( "i16"    , lis::representation_code::i16    )
        .value( "i32"    , lis::representation_code::i32    )
        .value( "f16"    , lis::representation_code::f16    )
        .value( "f32"    , lis::representation_code::f32    )
        .value( "f32low" , lis::representation_code::f32low )
        .value( "f32fix" , lis::representation_code::f32fix )
        .value( "string" , lis::representation_code::string )
        .value( "byte"   , lis::representation_code::byte   )
        .value( "mask"   , lis::representation_code::mask   )
    ;
    m.def( "rectype_tostring", &lis::record_type_str );
    m.def( "lis_sizeof_type",  &lis_sizeof_type );

    /* start - io.hpp */
    m.def("openlis", &lis::open,
            py::arg("filepath"),
            py::arg("offset")    = 0,
            py::arg("tapeimage") = true
    );

    py::class_< lis::iodevice >( m, "lis_stream" )
        .def( "__repr__", [](const lis::iodevice&) {
            return "dlisio.core.iodevice";
        })
        .def( "read_record",   &lis::iodevice::read_record )
        .def( "index_records", &lis::iodevice::index_records )
        .def( "index_record",  &lis::iodevice::index_record )
        .def( "ptell",         &lis::iodevice::ptell )
        .def( "close",         &lis::iodevice::close )
        .def( "seek",          &lis::iodevice::seek )
        .def( "eof",           &lis::iodevice::eof )
        .def( "read", []( lis::iodevice& s, py::buffer b, long long off, int n ) {
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
            s.read( static_cast< char* >( info.ptr ), n);
            return b;
        })
        .def( "read_physical_header",  &lis::iodevice::read_physical_header )
        .def( "read_logical_header",   &lis::iodevice::read_logical_header )
    ;

    py::class_< lis::lrheader >( m, "lrheader" )
        .def_readonly( "type", &lis::lrheader::type )
        .def( "__repr__", []( const lis::lrheader& x ) {
            return "dlisio.core.lrheader(type={})"_s.format( x.type );
        })
    ;

    py::class_< lis::prheader >( m, "prheader" )
        .def_property_readonly( "length", []( const lis::prheader& x ) {
            return x.length;
        })
        .def( "__repr__", [](const lis::prheader& x) {
            bool prev = x.attributes & lis::prheader::predces;
            bool succ = x.attributes & lis::prheader::succses;
            return "dlisio.core.prheader(length={}, pred={}, succ={})"_s.format(
                x.length,
                prev,
                succ
            );
        })
    ;

    py::class_< lis::record_info >( m, "lis_record_info" )
        .def( "__repr__", [](const lis::record_info& x) {
            return "dlisio.core.record_info(type={}, ltell={})"_s.format(
                x.type, x.ltell
            );
        })
        .def_readonly( "ltell", &lis::record_info::ltell )
        .def_readonly( "size",  &lis::record_info::size  )
        .def_readonly( "type",  &lis::record_info::type  )
    ;

    py::class_< lis::record >( m, "lis_record", py::buffer_protocol() )
        .def_readonly( "info", &lis::record::info )
        .def( "__repr__", [](const lis::record& x) {
            return "dlisio.core.record(type={}, ltell={}, size={})"_s.format(
                x.info.type, x.info.ltell, x.data.size()
            );
        })
        .def_buffer( []( lis::record& rec ) -> py::buffer_info {
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

    py::class_< lis::record_index >( m, "lis_record_index" )
        .def( "explicits",    &lis::record_index::explicits )
        .def( "implicits",    &lis::record_index::implicits )
        .def( "size",         &lis::record_index::size )
        .def( "isincomplete", &lis::record_index::is_incomplete)
        .def( "errmsg",       &lis::record_index::errmsg)
        .def( "__repr__", [](const lis::record_index& x) {
            return "dlisio.core.record_info(size={})"_s.format(
                x.size()
            );
        })
    ;
    /* end - io.hpp */

    /* start - parse.hpp */
    py::class_< lis::entry_block >( m, "entry_block" )
        .def_readonly( "type",  &lis::entry_block::type  )
        .def_readonly( "size",  &lis::entry_block::size  )
        .def_readonly( "reprc", &lis::entry_block::reprc )
        .def_readonly( "value", &lis::entry_block::value )
        .def( "__repr__", [](const lis::entry_block& x) {
            return "dlisio.core.entry_block(type={}, val={})"_s.format(
                x.type, x.value
            );
        })
    ;

    py::class_< lis::detail::spec_block >( m, "spec_block" )
        .def_readonly( "mnemonic",         &lis::spec_block0::mnemonic         )
        .def_readonly( "service_id",       &lis::spec_block0::service_id       )
        .def_readonly( "service_order_nr", &lis::spec_block0::service_order_nr )
        .def_readonly( "units",            &lis::spec_block0::units            )
        .def_readonly( "filenr",           &lis::spec_block0::filenr           )
        .def_readonly( "reserved_size",    &lis::spec_block0::reserved_size    )
        .def_readonly( "samples",          &lis::spec_block0::samples          )
        .def_readonly( "reprc",            &lis::spec_block0::reprc            )
    ;

    py::class_< lis::spec_block0, lis::detail::spec_block >( m, "spec_block0" )
        // TODO implement spec_block 0 specific fields
        .def( "__repr__", [](const lis::spec_block0& x) {
            return "dlisio.core.spec_block0(mnemonic={})"_s.format(
                x.mnemonic
            );
        })
    ;

    py::class_< lis::spec_block1, lis::detail::spec_block >( m, "spec_block1" )
        // TODO implement spec_block 1 specific fields
        .def( "__repr__", [](const lis::spec_block1& x) {
            return "dlisio.core.spec_block1(mnemonic={})"_s.format(
                x.mnemonic
            );
        })
    ;

    py::class_< lis::component_block >( m, "component_block" )
        .def_readonly( "type_nb",   &lis::component_block::type_nb   )
        .def_readonly( "reprc",     &lis::component_block::reprc     )
        .def_readonly( "size",      &lis::component_block::size      )
        .def_readonly( "category",  &lis::component_block::category  )
        .def_readonly( "mnemonic",  &lis::component_block::mnemonic  )
        .def_readonly( "units",     &lis::component_block::units     )
        .def_readonly( "component", &lis::component_block::component )
        .def( "__repr__", []( const lis::component_block& x ) {
            return "dlisio.core.component_block(mnem='{}', units='{}', component='{}')"_s.format(
                x.mnemonic,
                x.units,
                x.component
            );
        })
    ;

    py::class_< lis::information_record >( m, "information_record" )
        .def_readonly( "info",        &lis::information_record::info       )
        .def_readonly( "components",  &lis::information_record::components )
        .def_property_readonly( "isstructured", []( const lis::information_record& x ) {
            if (x.components.size() == 0) return false;
            const auto& cb = x.components.at(0);
            return lis::decay(cb.type_nb) == 73;
        })
        .def( "__repr__", []( const lis::information_record& x ) {
            return "dlisio.core.information_record(type={}, ncomponents={})"_s.format(
                x.info.type,
                x.components.size()
            );
        })
    ;

    py::class_< lis::text_record >( m, "text_record" )
        .def_readonly( "message", &lis::text_record::message )
        .def_readonly( "type",    &lis::text_record::type    )
        .def( "__repr__", []( const lis::text_record& x ) {
            return "dlisio.core.text_record(type={})"_s.format(
                x.type
            );
        })
    ;

    py::class_< lis::detail::file_record >( m, "file_record" )
        .def_readonly( "file_name",           &lis::detail::file_record::file_name           )
        .def_readonly( "service_sublvl_name", &lis::detail::file_record::service_sublvl_name )
        .def_readonly( "version_number",      &lis::detail::file_record::version_number      )
        .def_readonly( "date_of_generation",  &lis::detail::file_record::date_of_generation  )
        .def_readonly( "max_pr_length",       &lis::detail::file_record::max_pr_length       )
        .def_readonly( "file_type",           &lis::detail::file_record::file_type           )
    ;

    py::class_< lis::file_header, lis::detail::file_record >( m, "file_header" )
        .def_readonly( "prev_file_name", &lis::file_header::prev_file_name )
        .def( "__repr__", []( const lis::file_header& ) {
                return "dlisio.core.file_header";
        })
    ;

    py::class_< lis::file_trailer, lis::detail::file_record >( m, "file_trailer" )
        .def_readonly( "next_file_name", &lis::file_trailer::next_file_name )
        .def( "__repr__", []( const lis::file_trailer& ) {
                return "dlisio.core.file_trailer";
        })
    ;

    py::class_< lis::detail::reel_tape_record >( m, "reel_tape_record" )
        .def_readonly( "service_name",        &lis::detail::reel_tape_record::service_name        )
        .def_readonly( "date",                &lis::detail::reel_tape_record::date                )
        .def_readonly( "origin_of_data",      &lis::detail::reel_tape_record::origin_of_data      )
        .def_readonly( "name",                &lis::detail::reel_tape_record::name                )
        .def_readonly( "continuation_number", &lis::detail::reel_tape_record::continuation_number )
        .def_readonly( "comment",             &lis::detail::reel_tape_record::comment             )
    ;

    py::class_< lis::tape_header, lis::detail::reel_tape_record >( m, "tape_header" )
        .def_readonly( "prev_tape_name", &lis::tape_header::prev_tape_name )
        .def( "__repr__", []( const lis::tape_header& ) {
                return "dlisio.core.tape_header";
        })
    ;

    py::class_< lis::tape_trailer, lis::detail::reel_tape_record >( m, "tape_trailer" )
        .def_readonly( "next_tape_name", &lis::tape_trailer::next_tape_name )
        .def( "__repr__", []( const lis::tape_trailer& ) {
                return "dlisio.core.tape_trailer";
        })
    ;

    py::class_< lis::reel_header, lis::detail::reel_tape_record >( m, "reel_header" )
        .def_readonly( "prev_reel_name", &lis::reel_header::prev_reel_name )
        .def( "__repr__", []( const lis::reel_header& ) {
                return "dlisio.core.reel_header";
        })
    ;

    py::class_< lis::reel_trailer, lis::detail::reel_tape_record >( m, "reel_trailer" )
        .def_readonly( "next_reel_name", &lis::reel_trailer::next_reel_name )
        .def( "__repr__", []( const lis::reel_trailer& ) {
                return "dlisio.core.reel_trailer";
        })
    ;
    ;

    py::class_< lis::dfsr >( m, "dfsr" )
        .def_readonly( "info",    &lis::dfsr::info    )
        .def_readonly( "entries", &lis::dfsr::entries )
        .def_readonly( "specs",   &lis::dfsr::specs   )
        .def( "__repr__", []( const lis::dfsr& x ) {
            return "dlisio.core.dfsr(nchannels={})"_s.format(
                x.specs.size()
            );
        })
    ;

    m.def( "parse_text_record", &lis::parse_text_record );

    m.def( "parse_file_header",  &lis::parse_file_header );
    m.def( "parse_file_trailer", &lis::parse_file_trailer );
    m.def( "parse_tape_header",  &lis::parse_tape_header );
    m.def( "parse_tape_trailer", &lis::parse_tape_trailer );
    m.def( "parse_reel_header",  &lis::parse_reel_header );
    m.def( "parse_reel_trailer", &lis::parse_reel_trailer );

    m.def( "parse_dfsr", &lis::parse_dfsr );
    m.def("dfs_formatstring", &lis::dfs_fmtstr);
    /* end - parse.hpp */

    m.def( "parse_info_record", &lis::parse_info_record );

    m.def("read_data_records", read_data_records);
}
