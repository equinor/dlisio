#include <cerrno>
#include <cstdio>
#include <exception>
#include <memory>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>

#include <dlisio/dlisio.h>
#include <dlisio/types.h>

namespace py = pybind11;
using namespace py::literals;

namespace {

/*
 * for some reason, pybind does not defined IOError, so make a quick
 * regular-looking exception like that and register its translation
 */
struct io_error : public std::runtime_error {
    using std::runtime_error::runtime_error;
    explicit io_error( int no ) : runtime_error( std::strerror( no ) ) {}
};

struct eof_error : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

void runtime_warning( const char* msg ) {
    int err = PyErr_WarnEx( PyExc_RuntimeWarning, msg, 1 );
    if( err ) throw py::error_already_set();
}

/*
 * automate the read-bytes-throw-if-fails, at least for now. file error
 * reporting isn't very sophisticated, but doesn't have to be yet.
 */
void getbytes( char* buffer, std::size_t nmemb, std::FILE* fd ) {
    const auto read = std::fread( buffer, 1, nmemb, fd );
    if( read != nmemb ) {
        if( std::feof( fd ) ) throw eof_error( "unexpected EOF" );
        throw io_error( errno );
    }
}

py::dict SUL( const char* buffer ) {
    char id[ 61 ] = {};
    int seqnum, major, minor, layout;
    int64_t maxlen;

    auto err = dlis_sul( buffer, &seqnum,
                                 &major,
                                 &minor,
                                 &layout,
                                 &maxlen,
                                 id );


    switch( err ) {
        case DLIS_OK: break;

        // TODO: report more precisely - a lot of stuff can go wrong with the
        // SUL
        if( err == DLIS_UNEXPECTED_VALUE )
            throw py::value_error( "unable to parse storage unit label (SUL)" );

        case DLIS_INCONSISTENT:
            runtime_warning( "storage unit label inconsistent with "
                             "specification - falling back to assuming DLIS v1"
            );
            break;
    }

    std::string version = std::to_string( major )
                        + "."
                        + std::to_string( minor );

    std::string laystr = "record";
    if( layout != DLIS_STRUCTURE_RECORD ) laystr = "unknown";

    return py::dict( "sequence"_a = seqnum,
                     "version"_a = version.c_str(),
                     "layout"_a = laystr.c_str(),
                     "maxlen"_a = maxlen,
                     "id"_a =  id );
}

struct bookmark {
    std::fpos_t pos;

    /*
     * the remaining bytes of the "previous" visible record. if 0, the current
     * object is the visible record label
     */
    int residual = 0;

    int isexplicit = 0;

    /*
     * only pos is used for seeking and repositioning - tell is used only for
     * __repr__ and debugging purposes
     */
    long long tell = 0;
};

struct segheader {
    std::uint8_t attrs;
    int len;
    int type;
};

segheader segment_header( std::FILE* fp ) {
    char buffer[ 4 ];
    getbytes( buffer, 4, fp );

    segheader seg;
    const auto err = dlis_lrsh( buffer, &seg.len, &seg.attrs, &seg.type );
    if( err ) throw py::value_error( "unable to parse "
                                     "logical record segment header" );
    return seg;
}

int visible_length( std::FILE* fp ) {
    char buffer[ 4 ];
    getbytes( buffer, 4, fp );

    int len, version;
    const auto err = dlis_vrl( buffer, &len, &version );
    if( err ) throw py::value_error( "unable to parse visible record label" );

    if( version != 1 ) {
        std::string msg = "VRL DLIS not v1, was " + std::to_string( version );
        runtime_warning( msg.c_str() );
    }

    return len;
}

class file {
public:
    explicit file( const std::string& path );

    operator std::FILE*() const {
        if( this->fp ) return this->fp.get();
        throw py::value_error( "I/O operation on closed file" );
    }

    void close() { this->fp.reset(); }
    bool eof();

    py::dict storage_unit_label();
    py::tuple markrecord( int );
    py::bytes getrecord( const bookmark& );


private:
    struct fcloser {
        void operator()( std::FILE* x ) {
            if( x ) std::fclose( x );
        }
    };

    std::unique_ptr< std::FILE, fcloser > fp;
};

file::file( const std::string& path ) :
    fp( std::fopen( path.c_str(), "rb" ) ) {

    if( !this->fp ) throw io_error( errno );
}

bool file::eof() {
    std::FILE* fd = *this;

    int c = std::fgetc( fd );

    if( c == EOF ) return true;
    else c = std::ungetc( c, fd );

    if( c == EOF ) return true;
    return std::feof( fd );
}

py::dict file::storage_unit_label() {
    auto err = std::fseek( *this, 0, SEEK_SET );
    if( err ) throw io_error( errno );

    char buffer[ 80 ];
    getbytes( buffer, sizeof( buffer ), *this );
    return SUL( buffer );
}

struct marker {
    bookmark m;
    int residual;
};

marker mark( std::FILE* fp, int remaining ) {
    bookmark mark;
    mark.residual = remaining;

    auto err = std::fgetpos( fp, &mark.pos );
    if( err ) throw io_error( errno );

    /*
     * TODO: use _ftell64 or similar on Windows, to handle >2G files.
     * It's not necessary for repositioning, but helps diagnostics
     */
    mark.tell = std::ftell( fp );
    if( mark.tell == -1 ) throw io_error( errno );

    while( true ) {

        /*
         * if remaining = 0 this is at the VRL, skip the inner-loop and read it
         */
        while( remaining > 0 ) {
            auto seg = segment_header( fp );
            remaining -= seg.len;

            int has_predecessor = 0;
            int has_successor = 0;
            int is_encrypted = 0;
            int has_encryption_packet = 0;
            int has_checksum = 0;
            int has_trailing_length = 0;
            int has_padding = 0;
            dlis_segment_attributes( seg.attrs, &mark.isexplicit,
                                                &has_predecessor,
                                                &has_successor,
                                                &is_encrypted,
                                                &has_encryption_packet,
                                                &has_checksum,
                                                &has_trailing_length,
                                                &has_padding );

            seg.len -= 4; // size of LRSH
            err = std::fseek( fp, seg.len, SEEK_CUR );
            if( err ) throw io_error( errno );

            if( !has_successor ) return { mark, remaining };
        }

        /* if remaining is 0, then we're at a VRL */
        remaining = visible_length( fp ) - 4;
    }
}

py::tuple file::markrecord( int remaining ) {
    auto next = mark( *this, remaining );
    return py::make_tuple( next.m, next.residual, next.m.isexplicit );
}

std::vector< char > catrecord( std::FILE* fp, int remaining ) {

    std::vector< char > cat;
    cat.reserve( 8192 );

    while( true ) {

        while( remaining > 0 ) {

            auto seg = segment_header( fp );
            remaining -= seg.len;

            int explicit_formatting = 0;
            int has_predecessor = 0;
            int has_successor = 0;
            int is_encrypted = 0;
            int has_encryption_packet = 0;
            int has_checksum = 0;
            int has_trailing_length = 0;
            int has_padding = 0;
            dlis_segment_attributes( seg.attrs, &explicit_formatting,
                                                &has_predecessor,
                                                &has_successor,
                                                &is_encrypted,
                                                &has_encryption_packet,
                                                &has_checksum,
                                                &has_trailing_length,
                                                &has_padding );


            seg.len -= 4; // size of LRSH
            const auto prevsize = cat.size();
            cat.resize( prevsize + seg.len );
            getbytes( cat.data() + prevsize, seg.len, fp );

            if( has_trailing_length ) cat.erase( cat.end() - 2, cat.end() );
            if( has_checksum )        cat.erase( cat.end() - 2, cat.end() );
            if( has_padding ) {
                std::uint8_t padbytes = 0;
                dlis_ushort( cat.data() + cat.size() - 1, &padbytes );
                cat.erase( cat.end() - padbytes, cat.end() );
            }

            if( !has_successor ) return cat;
        }

        remaining = visible_length( fp ) - 4;
    }
}

py::bytes file::getrecord( const bookmark& m ) {
    std::FILE* fd = *this;
    auto err = std::fsetpos( fd, &m.pos );
    if( err ) throw io_error( errno );

    auto cat = catrecord( fd, m.residual );
    return py::bytes( cat.data(), cat.size() );
}

}

PYBIND11_MODULE(core, m) {
    py::register_exception_translator( []( std::exception_ptr p ) {
        try {
            if( p ) std::rethrow_exception( p );
        } catch( const io_error& e ) {
            PyErr_SetString( PyExc_IOError, e.what() );
        } catch( const eof_error& e ) {
            PyErr_SetString( PyExc_EOFError, e.what() );
        }
    });

    py::class_< bookmark >( m, "bookmark" )
        .def( "__repr__", []( const bookmark& m ) {
            return "<dlisio.core.bookmark pos="
                 + std::to_string( m.tell )
                 + ">"
                 ;
        })
    ;

    m.def( "sul", []( const std::string& b ) {
        if( b.size() < 80 ) {
            throw py::value_error(
                    "SUL object too small: expected 80, was "
                    + std::to_string( b.size() ) );
        }
        return SUL( b.data() );
    } );

    py::class_< file >( m, "file" )
        .def( py::init< const std::string& >() )
        .def( "close", &file::close )
        .def( "eof",   &file::eof )

        .def( "sul",       &file::storage_unit_label )
        .def( "mark",      &file::markrecord )
        .def( "getrecord", &file::getrecord )
        ;
}
