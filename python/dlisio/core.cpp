#include <bitset>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <exception>
#include <iterator>
#include <memory>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <dlisio/dlisio.h>
#include <dlisio/types.h>

namespace py = pybind11;
using namespace py::literals;

#include "typeconv.cpp"

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

void user_warning( const char* msg ) {
    int err = PyErr_WarnEx( PyExc_UserWarning, msg, 1 );
    if( err ) throw py::error_already_set();
}

void user_warning( const std::string& msg ) {
    user_warning( msg.c_str() );
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
    int isencrypted = 0;

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

    py::tuple mkindex();
    py::bytes raw_record( const bookmark& );
    py::dict eflr( const bookmark& );


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

bool iseof( std::FILE* fp ) {
    int c = std::fgetc( fp );

    if( c == EOF ) return true;
    else c = std::ungetc( c, fp );

    if( c == EOF ) return true;
    return std::feof( fp );
}

bool file::eof() {
    return iseof( *this );
}

bookmark mark( std::FILE* fp, int& remaining ) {
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
            int has_encryption_packet = 0;
            int has_checksum = 0;
            int has_trailing_length = 0;
            int has_padding = 0;
            dlis_segment_attributes( seg.attrs, &mark.isexplicit,
                                                &has_predecessor,
                                                &has_successor,
                                                &mark.isencrypted,
                                                &has_encryption_packet,
                                                &has_checksum,
                                                &has_trailing_length,
                                                &has_padding );

            seg.len -= 4; // size of LRSH
            err = std::fseek( fp, seg.len, SEEK_CUR );
            if( err ) throw io_error( errno );

            if( !has_successor ) return mark;
        }

        /* if remaining is 0, then we're at a VRL */
        remaining = visible_length( fp ) - 4;
    }
}

py::tuple file::mkindex() {
    std::FILE* fd = *this;

    char buffer[ 80 ];
    getbytes( buffer, sizeof( buffer ), fd );
    auto sul = SUL( buffer );

    std::vector< bookmark > bookmarks;
    int remaining = 0;

    while( !iseof( fd ) )
        bookmarks.push_back( mark( fd, remaining ) );

    return py::make_tuple( sul, bookmarks );
}

py::list getarray( const char*& xs, int count, int reprc ) {
    py::list l;

    for( int i = 0; i < count; ++i ) {
        switch( reprc ) {
            case DLIS_FSHORT: l.append( fshort( xs ) ); break;
            case DLIS_FSINGL: l.append( fsingl( xs ) ); break;
            case DLIS_FSING1: l.append( fsing1( xs ) ); break;
            case DLIS_FSING2: l.append( fsing2( xs ) ); break;
            case DLIS_ISINGL: l.append( isingl( xs ) ); break;
            case DLIS_VSINGL: l.append( vsingl( xs ) ); break;
            case DLIS_FDOUBL: l.append( fdoubl( xs ) ); break;
            case DLIS_FDOUB1: l.append( fdoub1( xs ) ); break;
            case DLIS_FDOUB2: l.append( fdoub2( xs ) ); break;
            case DLIS_CSINGL: l.append( csingl( xs ) ); break;
            case DLIS_CDOUBL: l.append( cdoubl( xs ) ); break;
            case DLIS_SSHORT: l.append( sshort( xs ) ); break;
            case DLIS_SNORM:  l.append(  snorm( xs ) ); break;
            case DLIS_SLONG:  l.append(  slong( xs ) ); break;
            case DLIS_USHORT: l.append( ushort( xs ) ); break;
            case DLIS_UNORM:  l.append(  unorm( xs ) ); break;
            case DLIS_ULONG:  l.append(  ulong( xs ) ); break;
            case DLIS_UVARI:  l.append(  uvari( xs ) ); break;
            case DLIS_IDENT:  l.append(  ident( xs ) ); break;
            case DLIS_ASCII:  l.append(  ascii( xs ) ); break;
            case DLIS_DTIME:  l.append(  dtime( xs ) ); break;
            case DLIS_STATUS: l.append( status( xs ) ); break;
            case DLIS_ORIGIN: l.append( origin( xs ) ); break;
            case DLIS_OBNAME: l.append( obname( xs ) ); break;
            case DLIS_OBJREF: l.append( objref( xs ) ); break;
            case DLIS_UNITS:  l.append(  ident( xs ) ); break;

            default:
                throw py::value_error( "unknown representation code "
                                     + std::to_string( reprc ) );
        }
    }

    return l;
}

struct setattr {
    int type, name;
};

setattr set_attributes( const char*& cur ) {
    std::uint8_t attr;
    std::memcpy( &attr, cur, sizeof( std::uint8_t ) );
    cur += sizeof( std::uint8_t );

    int role;
    dlis_component( attr, &role );

    switch( role ) {
        case DLIS_ROLE_RDSET:
        case DLIS_ROLE_RSET:
        case DLIS_ROLE_SET:
            break;

        default:
            throw py::value_error(
                std::string("first item in EFLR not SET, RSET or RDSET, was ")
                + dlis_component_str( role )
                + "(" + std::bitset< sizeof( attr ) >( role ).to_string() + ")"
            );
    }

    setattr flags;
    const auto err = dlis_component_set( attr, role, &flags.type, &flags.name );

    switch( err ) {
        case DLIS_OK:
            break;

        case DLIS_INCONSISTENT:
            user_warning( "SET:type not set, but must be non-null." );
            flags.type = 1;
            break;

        default:
            throw std::runtime_error( "unhandled error in dlis_component_set" );
    }

    return flags;
}

struct attribattr {
    int label;
    int count;
    int reprc;
    int units;
    int value;
    int object = 0;
    int absent = 0;
    int invariant = 0;
};

attribattr attrib_attributes( const char*& cur ) {
    std::uint8_t attr;
    std::memcpy( &attr, cur, sizeof( std::uint8_t ) );

    int role;
    dlis_component( attr, &role );

    attribattr flags;
    switch( role ) {
        case DLIS_ROLE_ABSATR:
            flags.absent= 1;
            break;

        case DLIS_ROLE_OBJECT:
            flags.object = 1;
            break;

        case DLIS_ROLE_INVATR:
            flags.invariant = 1;

        case DLIS_ROLE_ATTRIB:
            break;

        default:
            throw py::value_error(
                std::string("expected ATTRIB, INVATR, or OBJECT, was ")
                + dlis_component_str( role )
                + "(" + std::bitset< sizeof( attr ) >( role ).to_string() + ")"
            );
    }

    /*
     * only consume the component tag if it is not object, because if it is
     * then the next function assumes its there
     */
    if( role != DLIS_ROLE_OBJECT )
        cur += sizeof( std::uint8_t );

    if( flags.object || flags.absent ) return flags;

    const auto err = dlis_component_attrib( attr, role, &flags.label,
                                                        &flags.count,
                                                        &flags.reprc,
                                                        &flags.units,
                                                        &flags.value );

    if( !err ) return flags;

    // all sources for this error should've been checked, so
    // something is REALLY wrong if we end up here
    throw std::runtime_error( "unhandled error in dlis_component_attrib" );
}

void object_attributes( const char*& cur ) {
    std::uint8_t attr;
    std::memcpy( &attr, cur, sizeof( std::uint8_t ) );

    cur += sizeof( std::uint8_t );

    int role;
    dlis_component( attr, &role );

    if( role != DLIS_ROLE_OBJECT )
        throw py::value_error( std::string("expected OBJECT, was ")
                             + dlis_component_str( role ) );

    int obname;
    const auto err = dlis_component_object( attr, role, &obname );

    if( err ) user_warning( "OBJECT:name not set, but must be non-null" );
}

struct object_template {
    std::vector< py::dict > attribute;
    std::vector< py::dict > invariant;
};

object_template explicit_template( const char*& cur, const char* end ) {
    object_template cols;

    while( true ) {
        if( cur >= end )
            throw py::value_error( "unexpected end-of-record in template" );

        auto flags = attrib_attributes( cur );

        if( flags.object ) return cols;

        if( flags.absent ) {
            user_warning( "ABSATR in object template - skipping" );
            continue;
        }

        int count = 1;
        int reprc = DLIS_IDENT;
        /* set the global defaults unconditionally */
        py::dict col( "count"_a = count,
                      "reprc"_a = reprc,
                      "value"_a = py::none() );

        if( !flags.label ) {
            user_warning( "ATTRIB:label not set, but must be non-null" );
            flags.label = 1;
        }

                          col["label"] = ident( cur );
        if( flags.count ) col["count"] = count = uvari( cur );
        if( flags.reprc ) col["reprc"] = reprc = ushort( cur );
        if( flags.units ) col["units"] = ident( cur );
        if( flags.value ) col["value"] = getarray( cur, count, reprc );

        if( flags.invariant ) cols.invariant.push_back( std::move( col ) );
        else                  cols.attribute.push_back( std::move( col ) );
    }
}

py::dict deepcopy( const py::dict& d ) {
    return py::reinterpret_steal< py::dict >( PyDict_Copy( d.ptr() ) );
}

template< typename T >
std::vector< T > deepcopy( const std::vector< T >& xs ) {
    std::vector< T > ys;
    ys.reserve( xs.size() );

    for( const auto& x : xs )
        ys.push_back( deepcopy( x ) );

    return ys;
}

py::dict eflr( const char* cur, const char* end ) {
    if( std::distance( cur, end ) == 0 )
        throw py::value_error( "eflr must be non-empty" );

    py::dict record;
    auto set = set_attributes( cur );
    if( cur >= end ) {
        throw py::value_error( "unexpected end-of-record "
                                 "after SET component" );
    }

    if( set.type ) record["type"] = ident( cur );
    if( set.name ) record["name"] = ident( cur );

    auto tmpl = explicit_template( cur, end );

    if( cur >= end )
        throw py::value_error( "unexpected end-of-record after template" );

    py::dict objects;
    while( true ) {
        if( cur == end ) break;

        object_attributes( cur );

        /*
         * just assume obname. objects have to specify it, and if it is unset
         * then UserWarning has already been emitted
         */
        auto name = obname( cur );

        /*
         * each object is a row in a table of attributes. If the object is cut
         * short (terminated by a new object), use the defaults from the template
         */
        auto row = deepcopy( tmpl.attribute );

        for( auto& cell : row ) {
            if( cur == end ) break;

            auto flags = attrib_attributes( cur );

            if( flags.object ) break;

            if( flags.absent ) {
                cell["value"] = py::none();
                continue;
            }

            if( flags.label ) {
                user_warning( "ATTRIB:label set, but must be null - was "
                            + ident( cur ) );
            }

            if( flags.count ) cell["count"] = uvari( cur );
            if( flags.reprc ) cell["reprc"] = ushort( cur );
            if( flags.units ) cell["units"] = ident( cur );
            if( flags.value ) {
                /*
                 * count/repr can both be set by this label, and by the
                 * template, so the simplest thing is to just look them up in
                 * the dict
                 */
                auto count = cell["count"].cast< int >();
                auto reprc = cell["reprc"].cast< int >();
                cell["value"] = getarray( cur, count, reprc );
            }
        }

        /* patch invariant-attributes onto the record */
        row.insert( row.end(), tmpl.invariant.begin(), tmpl.invariant.end() );
        auto pyname = py::make_tuple( std::get< 0 >( name ),
                                      std::get< 1 >( name ),
                                      std::get< 2 >( name ) );
        objects[pyname] = row;
    }

    record["template-attribute"] = tmpl.attribute;
    record["template-invariant"] = tmpl.invariant;
    record["objects"] = objects;
    return record;
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

py::bytes file::raw_record( const bookmark& m ) {
    std::FILE* fd = *this;
    auto err = std::fsetpos( fd, &m.pos );
    if( err ) throw io_error( errno );

    auto cat = catrecord( fd, m.residual );
    return py::bytes( cat.data(), cat.size() );
}

py::dict file::eflr( const bookmark& mark ) {
    if( mark.isencrypted ) return py::none();
    auto err = std::fsetpos( *this, &mark.pos );
    if( err ) throw io_error( errno );

    auto cat = catrecord( *this, mark.residual );
    return ::eflr( cat.data(), cat.data() + cat.size() );
}

}

PYBIND11_MODULE(core, m) {
    PyDateTime_IMPORT;

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
        .def_readwrite( "encrypted", &bookmark::isencrypted )
        .def_readwrite( "explicit",  &bookmark::isexplicit )
        .def( "__repr__", []( const bookmark& m ) {
            auto pos = " pos=" + std::to_string( m.tell );
            auto enc = std::string(" encrypted=") +
                     (m.isencrypted ? "True": "False");
            auto exp = std::string(" explicit=") +
                     (m.isexplicit ? "True": "False");
            return "<dlisio.core.bookmark" + pos + enc + exp + ">";
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

    m.def( "eflr", []( py::buffer b ) {
        const auto info = b.request();
        const auto len = info.size * info.itemsize;
        const auto ptr = static_cast< char* >( info.ptr );
        return eflr( ptr, ptr + len );
    } );

    py::class_< file >( m, "file" )
        .def( py::init< const std::string& >() )
        .def( "close", &file::close )
        .def( "eof",   &file::eof )

        .def( "mkindex",   &file::mkindex )
        .def( "raw_record", &file::raw_record )
        .def( "eflr",       &file::eflr )
        ;
}
