#include <algorithm>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <memory>

#if defined(_DEBUG) && defined(_MSC_VER)
#  define _CRT_NOFORCE_MAINFEST 1
#  undef _DEBUG
#  include <Python.h>
#  include <bytesobject.h>
#  define _DEBUG 1
#else
#  include <Python.h>
#  include <bytesobject.h>
#endif

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace {

template< typename... A >
PyObject* BaseError( PyObject* err, const char* msg, A... args ) noexcept {
    return PyErr_Format( err, msg, args... );
}

template< typename... A >
PyObject* TypeError( const char* msg, A... args ) noexcept {
    return PyErr_Format( PyExc_TypeError, msg, args... );
}

template< typename... A >
PyObject* ValueError( const char* msg, A... args ) noexcept {
    return PyErr_Format( PyExc_ValueError, msg, args... );
}

template< typename... A >
PyObject* RuntimeError( const char* msg, A... args ) noexcept {
    return PyErr_Format( PyExc_RuntimeError, msg, args... );
}

template< typename... A >
PyObject* EOFError( const char* msg, A... args ) noexcept {
    return PyErr_Format( PyExc_EOFError, msg, args... );
}

template< typename... A >
PyObject* MemoryError( const char* msg, A... args ) noexcept {
    return PyErr_Format( PyExc_MemoryError, msg, args... );
}

template< typename... A >
PyObject* NotImplementedError( const char* msg, A... args ) noexcept {
    return PyErr_Format( PyExc_NotImplementedError, msg, args... );
}

template< typename... A >
PyObject* IOError( const char* msg, A... args ) {
    std::string exmsg = msg;
    if( errno ) {
        exmsg += ": ";
        exmsg += std::strerror( errno );
    }
    return PyErr_Format( PyExc_IOError, exmsg.c_str(), args... );
}

struct fcloser {
    void operator()( std::FILE* fp ) { if( fp ) std::fclose( fp ); }
};

struct autofd : public std::unique_ptr< std::FILE, fcloser > {
    using std::unique_ptr< std::FILE, fcloser >::unique_ptr;

    operator std::FILE*() const {
        if( *this ) return this->get();

        ValueError( "I/O operation on closed file" );
        return nullptr;
    }
};

struct file_handle {
    PyObject_HEAD
    autofd fd;
};

int filehandle_init( file_handle* self, PyObject* args, PyObject* kwargs ) {
    char* filename = NULL;
    char* modearg = NULL;

    new (&self->fd) decltype(self->fd);

    static const char* kwlist[] = {
        "path",
        "mode",
        NULL,
    };

    if( !PyArg_ParseTupleAndKeywords( args, kwargs,
                "s|s",
                const_cast< char** >(kwlist),
                &filename,
                &modearg ) )
        return -1;

    char mode[8] = "rb";
    const int modelen = 6;
    if( modearg ) std::strncpy( mode, modearg, modelen );

    /* append 'b' if it's not there, non-binary modes are not accepted */
    auto itr = std::find( mode, mode + modelen, 'b' );
    if( itr == mode + modelen ) *itr = 'b';

    autofd fd{ std::fopen( filename, mode ) };
    if( !fd ) {
        PyErr_SetFromErrnoWithFilename( PyExc_ValueError, filename );
        return -1;
    }

    self->fd.swap( fd );
    return 0;
}

void filehandle_dealloc( file_handle* self ) {
    self->fd.~autofd();
    Py_TYPE( self )->tp_free( (PyObject*) self );
}

PyObject* rewind( file_handle* self, PyObject* ) {
    std::FILE* fd = self->fd;
    if( !fd ) return nullptr;

    std::rewind( fd );
    return Py_BuildValue( "" );
}

PyObject* seek( file_handle* self, PyObject* args ) {
    std::FILE* fd = self->fd;
    if( !fd ) return nullptr;

    long offset;
    if( !PyArg_ParseTuple( args, "l", &offset ) ) return nullptr;

    const auto pos = std::fseek( fd, offset, SEEK_CUR );
    if( pos == -1 ) return IOError( "seek error" );

    return PyLong_FromLong( pos );
}

PyObject* tell( file_handle* self, PyObject* ) {
    std::FILE* fd = self->fd;
    if( !fd ) return nullptr;

    const auto pos = std::ftell( fd );
    if( pos == -1 ) return IOError( "seek error" );

    return PyLong_FromLong( pos );
}

PyObject* read( file_handle* self, PyObject* args ) {
    std::FILE* fd = self->fd;
    if( !fd ) return nullptr;

    long n;
    if( !PyArg_ParseTuple( args, "l", &n ) ) return nullptr;

    std::unique_ptr< char[] > buffer( new char[ n ] );
    if( !buffer )
        return MemoryError( "unable to allocate io-buffer of size %ld", n );

    std::fread( buffer.get(), 1, n, fd );
    return PyByteArray_FromStringAndSize( buffer.get(), n );
}

PyObject* close( file_handle* self, PyObject* ) {
    std::FILE* fd = self->fd;
    if( !fd ) return nullptr;

    self->fd.reset();
    return Py_BuildValue( "" );
}

PyObject* iseof( file_handle* self, PyObject* ) {
    std::FILE* fd = self->fd;
    if( !fd ) return nullptr;

    int c = std::fgetc( fd );

    if( c == EOF ) return PyLong_FromLong( 1 );
    else c = std::ungetc( c, fd );

    if( c == EOF ) return PyLong_FromLong( 1 );
    return PyLong_FromLong( std::feof( fd ) );
}


PyMethodDef file_methods[] = {
    { "tell",   (PyCFunction) tell,   METH_NOARGS,  "Tell"   },
    { "rewind", (PyCFunction) rewind, METH_NOARGS,  "Rewind" },
    { "seek",   (PyCFunction) seek,   METH_VARARGS, "Seek"   },
    { "read",   (PyCFunction) read,   METH_VARARGS, "Read"   },
    { "close",  (PyCFunction) close,  METH_NOARGS,  "Close"  },
    { "iseof",  (PyCFunction) iseof,  METH_NOARGS,  "Is EOF" },

    { nullptr },
};

PyTypeObject Filehandle = {
    PyVarObject_HEAD_INIT( NULL, 0 )
    "core.file",                    /* name */
    sizeof( file_handle ),          /* basic size */
    0,                              /* tp_itemsize */
    (destructor)filehandle_dealloc, /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_compare */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    "file handle",                  /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                              /* tp_iternext */
    file_methods,                   /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    (initproc)filehandle_init,      /* tp_init */
};

}

PyMethodDef module_functions[] = {
    { NULL },
};

/* module initialization */
#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef dlisio_module = {
        PyModuleDef_HEAD_INIT,
        "core",   /* name of module */
        NULL,     /* module documentation, may be NULL */
        -1,       /* size of per-interpreter state of the module */
        module_functions,
};

PyMODINIT_FUNC PyInit_core( void ) {
    Filehandle.tp_new = PyType_GenericNew;
    if( PyType_Ready( &Filehandle ) < 0 ) return nullptr;

    PyObject* m = PyModule_Create( &dlisio_module );
    if( !m ) return nullptr;

    Py_INCREF( &Filehandle );
    PyModule_AddObject( m, "file", (PyObject*)&Filehandle );

    return m;
}
#else
PyMODINIT_FUNC init_core( void ) {
    Filehandle.tp_new = PyType_GenericNew;
    if( PyType_Ready( &Filehandle ) < 0 ) return nullptr;

    PyObject* m = Py_InitModule( "core", module_functions );

    Py_INCREF( &Filehandle );
    PyModule_AddObject( m, "file", (PyObject*)&Filehandle );
}
#endif
